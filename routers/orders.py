from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
import database
from dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=schemas.OrderResponse)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    new_order = models.Order(user_id=current_user.id, total_price=0.0)  # type: ignore
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
            db.query(models.Product)
            .filter(models.Product.id == item.product_id)
            .with_for_update()
            .first()
        )

        if not product:
            db.rollback()
            raise HTTPException(
                status_code=404, detail=f"Product ID {item.product_id} not found"
            )

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

        order_item = models.OrderItem(  # type: ignore
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
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()


@router.get("/all", response_model=list[schemas.OrderResponse])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    admin_user: models.User = Depends(get_current_admin),
):
    return db.query(models.Order).offset(skip).limit(limit).all()


@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(database.get_db),
    admin_user: models.User = Depends(get_current_admin),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_update.status  # type: ignore
    db.commit()
    db.refresh(order)

    return order
