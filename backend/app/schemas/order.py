from enum import Enum
from datetime import datetime
from typing import List

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


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"


class PaymentStatusUpdate(BaseModel):
    payment_status: PaymentStatus


class SafepayConfig(BaseModel):
    """Public config the frontend needs to render the Safepay button widget."""

    api_key: str
    environment: str
    currency: str


class SafepayConfirmRequest(BaseModel):
    """
    Sent by the frontend after the Safepay button widget's onPayment
    callback fires, so we can verify the payment server-side before
    trusting it.
    """

    tracker_token: str
