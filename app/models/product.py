from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    slug: str = Field(unique=True, index=True, max_length=255)
    category: str = Field(index=True, max_length=100)  # e.g., "Wood Pressed Oils", "Organic Cold Pressed", "Lamp Oil"
    description: str
    benefits: Optional[str] = None
    volume_ml: int = Field(default=1000)  # 500, 1000, 5000 ml
    price: float = Field(default=0.0)
    compare_at_price: Optional[float] = None
    stock_quantity: int = Field(default=0)
    sku: str = Field(unique=True, index=True, max_length=100)
    image_url: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")
