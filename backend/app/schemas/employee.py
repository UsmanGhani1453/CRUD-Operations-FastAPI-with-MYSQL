from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field


class EmployeeBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
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
