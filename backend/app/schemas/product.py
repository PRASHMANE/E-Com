from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int

    model_config = ConfigDict(
        from_attributes=True
    )