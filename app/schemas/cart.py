from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductRead


class CartItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=50)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, le=50)


class CartItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductRead] = None
    item_subtotal: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class CartRead(BaseModel):
    id: int
    session_id: str
    items: List[CartItemRead] = []
    item_count: int = 0
    subtotal: float = 0.0
    estimated_tax: float = 0.0
    estimated_shipping: float = 0.0
    estimated_total: float = 0.0

    model_config = ConfigDict(from_attributes=True)
