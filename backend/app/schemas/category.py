from typing import Optional, Any

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    extra_data: Optional[Any] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
