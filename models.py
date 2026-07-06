from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Boolean, DateTime

from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True,unique=True, autoincrement=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    extra_data = Column(JSON, nullable=True)
    stock = Column(Integer, nullable=False, default=0)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    employees = relationship("Employee", back_populates="category")
    owner_id = Column(Integer, ForeignKey("users.id"))
    extra_data = Column(JSON, nullable=True)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="employees")
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="employees")
    extra_data = Column(JSON, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String(100), unique=True, nullable=False,index=True)
    hashed_password = Column(String(255), nullable=False)
    employees = relationship("Employee", back_populates="owner")
    extra_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="customer")

class Order(Base):
        __tablename__ = "orders"

        id = Column(Integer,primary_key=True,index=True)
        user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable = False)
        total_price = Column(Float,nullable=False,default=0.0)
        status = Column(String(50),default="PENDING")
        created_at = Column(DateTime,default=datetime.utcnow)

        owner = relationship("User")
        items = relationship("OrderItem",back_populates="order",cascade="all,delete-orphan")

class OrderItem(Base):
        __tablename__ = "order_items"

        id = Column(Integer,primary_key=True,index=True)
        order_id = Column(Integer,ForeignKey("orders.id",ondelete="CASCADE"),nullable = False)
        product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
        quantity = Column(Integer,nullable=False, default=1)
        unit_price = Column(Float,nullable=False)

        order = relationship("Order", back_populates="items")
        product = relationship("Product")
