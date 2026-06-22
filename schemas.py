from pydantic import BaseModel
from typing import Optional

# Base properties shared across schemas
class ProductBase(BaseModel):
    name: str
    price: int

# Schema used for creating/updating a product (doesn't need an ID yet)
class ProductCreate(ProductBase):
    pass

# Schema used for returning a product from the database (includes the ID)
class Product(ProductBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
# ----------------------------------------------------------------------------------------------------
class CategoryBase(BaseModel):
    name:str
    description: Optional[str] = None

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
    email: str
    category_id: int  
class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    owner_id: int  

    class Config:
        from_attributes = True
#----------------------------------------------------------------------
class UserCreate(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    email:str

    class Config:
        from_attributes = True
# ------------------------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str