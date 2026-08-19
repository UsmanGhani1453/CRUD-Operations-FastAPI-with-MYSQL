from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product
from app import schemas
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_admin
from app.services import payments

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=schemas.OrderWithPaymentResponse)
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

    # Create the Stripe PaymentIntent up front. The order and its stock
    # decrement commit either way; client_secret is what the frontend uses
    # to collect card details on the next screen. If Stripe isn't
    # configured on this server, the order still goes through as "unpaid"
    # rather than blocking checkout entirely.
    client_secret = None
    try:
        intent = payments.create_payment_intent(running_total, new_order.id)
        new_order.stripe_payment_intent_id = intent.id  # type: ignore
        client_secret = intent.client_secret
    except HTTPException as exc:
        if exc.status_code != 503:
            db.rollback()
            raise
        # Payments not configured - proceed without one. Order stays
        # "unpaid"; an admin can still see/fulfill it manually.

    db.commit()
    db.refresh(new_order)

    response = schemas.OrderWithPaymentResponse.model_validate(new_order)
    response.client_secret = client_secret
    return response


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
    """
    Used by the frontend's payment/confirmation screen to poll for the
    webhook having flipped payment_status to "paid" after Stripe confirms
    the charge.
    """
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
