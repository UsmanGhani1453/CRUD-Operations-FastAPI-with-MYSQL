from typing import Optional, Any

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0)
    extra_data: Optional[Any] = None
    stock: int = Field(ge=0)
    image_url: Optional[str] = Field(default=None, max_length=255)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
