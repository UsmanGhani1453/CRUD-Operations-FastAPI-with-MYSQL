"""
Importing every model module here (rather than leaving it to each caller)
guarantees SQLAlchemy's mapper registry is fully populated before
`Base.metadata.create_all()` or Alembic's autogenerate run - relationships
declared with string class names (e.g. relationship("Employee")) only
resolve once the target module has actually been imported somewhere.
"""
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.employee import Employee
from app.models.order import Order, OrderItem

__all__ = ["User", "Category", "Product", "Employee", "Order", "OrderItem"]
