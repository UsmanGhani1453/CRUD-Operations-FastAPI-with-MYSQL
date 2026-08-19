from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product
from app import schemas
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_admin

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

    # No online payment integration - the order is placed as "unpaid" and
    # gets paid manually (e.g. cash/transfer on delivery). An admin marks
    # it "paid" later via PUT /orders/{id}/payment.
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
    """
    Used by the frontend's order history screen.
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


@router.put("/{order_id}/payment", response_model=schemas.OrderResponse)
def update_payment_status(
    order_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """
    Manually mark an order as paid/unpaid (e.g. cash or bank transfer on
    delivery, confirmed by an admin) - there's no online payment provider.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.payment_status = payment_update.payment_status.value  # type: ignore
    db.commit()
    db.refresh(order)

    return order
