"""
Re-exports every schema at the package level so routes can do
`from app import schemas` and reference `schemas.Product`, matching the
ergonomics of the original single-file schemas.py.
"""
from app.schemas.product import ProductBase, ProductCreate, Product
from app.schemas.category import CategoryBase, CategoryCreate, Category
from app.schemas.employee import EmployeeBase, EmployeeCreate, Employee
from app.schemas.user import UserCreate, UserResponse, Token
from app.schemas.order import (
    OrderItemCreate,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    OrderStatus,
    OrderStatusUpdate,
)

__all__ = [
    "ProductBase", "ProductCreate", "Product",
    "CategoryBase", "CategoryCreate", "Category",
    "EmployeeBase", "EmployeeCreate", "Employee",
    "UserCreate", "UserResponse", "Token",
    "OrderItemCreate", "OrderCreate", "OrderItemResponse", "OrderResponse",
    "OrderStatus", "OrderStatusUpdate",
]
