from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    extra_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="customer")

    employees = relationship("Employee", back_populates="owner")
