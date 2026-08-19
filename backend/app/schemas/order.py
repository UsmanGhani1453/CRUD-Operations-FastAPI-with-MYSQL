from enum import Enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    payment_status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderWithPaymentResponse(OrderResponse):
    """
    Returned only from order creation. `client_secret` is the Stripe
    PaymentIntent client secret the frontend needs to collect card details
    and confirm the charge - it's short-lived and tied to this one intent,
    safe to expose to the browser (that's what it's designed for).
    """
    client_secret: Optional[str] = None


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
