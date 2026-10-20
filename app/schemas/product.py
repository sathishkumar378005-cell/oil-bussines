from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., max_length=255, examples=["Pure Wood Pressed Cold Pressed Groundnut Oil"])
    slug: str = Field(..., max_length=255, examples=["wood-pressed-groundnut-oil-1l"])
    category: str = Field(..., max_length=100, examples=["Cold Pressed Oils"])
    description: str = Field(..., examples=["100% pure, natural, extracted using traditional wooden ghani/vaagai marachekku."])
    benefits: Optional[str] = Field(None, examples=["Rich in monounsaturated fats, vitamin E, and natural antioxidants."])
    volume_ml: int = Field(default=1000, examples=[1000])
    price: float = Field(..., gt=0, examples=[320.0])
    compare_at_price: Optional[float] = Field(None, examples=[380.0])
    stock_quantity: int = Field(default=50, ge=0)
    sku: str = Field(..., max_length=100, examples=["LATHA-GND-1L"])
    image_url: Optional[str] = Field(None, examples=["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5"])
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    volume_ml: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)
    compare_at_price: Optional[float] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductRead]
