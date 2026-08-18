from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    extra_data = Column(JSON, nullable=True)

    employees = relationship("Employee", back_populates="category")
