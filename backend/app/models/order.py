from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_price = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Payment tracking. payment_status is separate from `status` (order
    # fulfillment) on purpose - an order can be PENDING fulfillment while
    # already "paid", or CANCELLED after being paid (needing a refund).
    # There's no online payment integration - orders are paid manually
    # (e.g. cash/transfer on delivery) and an admin marks them "paid".
    payment_status = Column(String(20), default="unpaid", nullable=False)

    owner = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all,delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
