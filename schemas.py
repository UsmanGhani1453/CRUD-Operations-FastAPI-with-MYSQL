from pydantic import BaseModel, EmailStr
from typing import Optional,Any,Dict,List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    price: int
    extra_data: Optional[Any] = None
    stock: int 
    
class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
# ----------------------------------------------------------------------------------------------------
class CategoryBase(BaseModel):
    name:str
    description: Optional[str] = None
    extra_data: Optional[Any] = None
class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id:int 
    owner_id: int
    
    class Config:
        from_attributes = True
# ---------------------------------------------------------------------
class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    category_id: int  
    extra_data: Optional[Any] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    owner_id: int  

    class Config:
        from_attributes = True
#----------------------------------------------------------------------
class UserCreate(BaseModel):
    email:EmailStr
    password:str
    extra_data: Optional[Any] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_verified: Optional[bool] = False
    
    class Config:
        from_attributes = True
# ------------------------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
# ------------------------------------------------------------------------------------
class OrderItemCreate(BaseModel):
    product_id:int
    quantity:int

class OrderCreate(BaseModel):
    items:List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id:int 
    product_id:int
    quantity:int
    unit_price:float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id:int
    user_id:int
    total_price:float
    status:str
    created_at:datetime
    items:List[OrderItemResponse]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str