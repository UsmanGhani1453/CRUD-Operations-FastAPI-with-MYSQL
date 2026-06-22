from pydantic import BaseModel
from typing import Optional,Any,Dict

# Base properties shared across schemas
class ProductBase(BaseModel):
    name: str
    price: int
    extra_data: Optional[Any] = None
    
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
    email: str
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
    email:str
    password:str
    extra_data: Optional[Any] = None

class UserResponse(BaseModel):
    id:int
    email:str

    class Config:
        from_attributes = True
# ------------------------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str