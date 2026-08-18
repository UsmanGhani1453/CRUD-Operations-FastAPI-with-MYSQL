from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    extra_data: Optional[Any] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_verified: Optional[bool] = False
    role: str = "customer"

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
