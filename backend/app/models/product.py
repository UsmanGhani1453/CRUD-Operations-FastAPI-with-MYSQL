from sqlalchemy import Column, Integer, String, ForeignKey, JSON

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    extra_data = Column(JSON, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    image_url = Column(String(255), nullable=True)
