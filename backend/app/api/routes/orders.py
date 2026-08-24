from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
import httpx
from app.core.config import (
    CURRENCY,
    FRONTEND_BASE_URL,
    SAFEPAY_API_KEY,
    SAFEPAY_ENVIRONMENT,
    SAFEPAY_SECRET_KEY,
    SAFEPAY_API_BASE_URL
)
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product
from app import schemas
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_admin
from app.services import safepay

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=schemas.OrderResponse)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    new_order = Order(user_id=current_user.id, total_price=0.0)  # type: ignore
    db.add(new_order)
    db.flush()
    running_total = 0.0

    for item in order.items:
        if item.quantity <= 0:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Quantity for product {item.product_id} must be greater than zero",
            )

        # Lock the row for the duration of the transaction so concurrent
        # orders can't both read the same stock and oversell it.
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .with_for_update()
            .first()
        )

        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")

        if product.stock < item.quantity:  # type: ignore
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for product '{product.name}': "
                    f"requested {item.quantity}, available {product.stock}"
                ),
            )

        product.stock -= item.quantity  # type: ignore

        order_item = OrderItem(  # type: ignore
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
        )
        db.add(order_item)
        running_total += product.price * item.quantity  # type: ignore

    new_order.total_price = running_total  # type: ignore
    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/", response_model=list[schemas.OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@router.get("/all", response_model=list[schemas.OrderResponse])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    return db.query(Order).offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if bool(order.user_id != current_user.id) and current_user.role != "admin":  # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order


@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_update.status  # type: ignore
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}/payment", response_model=schemas.OrderResponse)
def update_payment_status(
    order_id: int,
    payment_update: schemas.PaymentStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.payment_status = payment_update.payment_status.value  # type: ignore
    db.commit()
    db.refresh(order)
    return order


@router.get("/safepay/config", response_model=schemas.SafepayConfig)
def get_safepay_config():
    return schemas.SafepayConfig(
        api_key=SAFEPAY_API_KEY,
        environment=SAFEPAY_ENVIRONMENT,
        currency=CURRENCY,
    )


@router.post("/{order_id}/safepay/confirm", response_model=schemas.OrderResponse)
def confirm_safepay_payment(
    order_id: int,
    payload: schemas.SafepayConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if bool(order.user_id != current_user.id) and current_user.role != "admin":  # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")
    if order.payment_status == "paid":  # type: ignore
        return order

    try:
        result = safepay.verify_payment(payload.tracker_token)
    except safepay.SafepayError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not safepay.payment_is_successful(result):
        raise HTTPException(status_code=400, detail="Safepay has not confirmed this payment yet")

    order.safepay_tracker_token = payload.tracker_token  # type: ignore
    order.payment_status = "paid"  # type: ignore
    db.commit()
    db.refresh(order)
    return order


@router.post("/webhook/safepay", include_in_schema=False)
async def safepay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_sfpy_signature: str | None = Header(default=None),
):
    raw_body = await request.body()
    if not safepay.verify_webhook_signature(raw_body, x_sfpy_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    data = payload.get("data", payload)
    tracker_token = data.get("token") or data.get("tracker") or data.get("order_id")

    if not tracker_token:
        raise HTTPException(status_code=400, detail="Missing tracker token in webhook payload")

    order = db.query(Order).filter(Order.safepay_tracker_token == tracker_token).first()
    if not order:
        return {"status": "ignored"}

    if safepay.payment_is_successful(payload):
        order.payment_status = "paid"  # type: ignore
        db.commit()

    return {"status": "ok"}


@router.post("/{order_id}/safepay/session")
def create_safepay_session(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    is_owner = bool(order.user_id == current_user.id)
    is_admin = bool(current_user.role == "admin")
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")

    if not SAFEPAY_API_KEY:
        raise HTTPException(status_code=500, detail="Safepay is not configured on the server.")

    raw_price = getattr(order, "total_price", 0.0)
    total_amount = float(raw_price or 0.0)
    amount_in_paisas = int(round(total_amount * 100))

    try:
        response = httpx.post(
            f"{SAFEPAY_API_BASE_URL}/order/v1/init",
            headers={
                "Content-Type": "application/json",
                "X-SFPY-MERCHANT-SECRET": SAFEPAY_SECRET_KEY,
            },
            json={
                "client": SAFEPAY_API_KEY,
                "amount": amount_in_paisas,
                "currency": CURRENCY.upper(),
                "environment": SAFEPAY_ENVIRONMENT,
            },
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Safepay: {exc}")

    if response.status_code >= 400:
        print(f"\n=== SAFEPAY ERROR ===\n{response.text}\n=====================\n")
        raise HTTPException(status_code=502, detail=f"Safepay error: {response.text}")

    data = response.json().get("data", response.json())
    tracker_token = data.get("token") or data.get("tracker")
    
    if not tracker_token:
        raise HTTPException(status_code=502, detail="Failed to retrieve tracker token from Safepay.")

    order.safepay_tracker_token = tracker_token
    db.commit()

    checkout_base = (
        "https://sandbox.api.getsafepay.com/components"
        if SAFEPAY_ENVIRONMENT == "sandbox"
        else "https://api.getsafepay.com/components"
    )
    
    checkout_url = f"{checkout_base}?beacon={tracker_token}&env={SAFEPAY_ENVIRONMENT}&public_key={SAFEPAY_API_KEY}&source=website"

    return {
        "checkout_url": checkout_url,
        "tracker_token": tracker_token
    }