from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True,unique=True, autoincrement=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    extra_data = Column(JSON, nullable=True) 

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
    Owner = relationship("User", back_populates="employees")
    extra_data = Column(JSON, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String(100), unique=True, nullable=False,index=True)
    hashed_password = Column(String(255), nullable=False)
    employees = relationship("Employee", back_populates="Owner")
    extra_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)