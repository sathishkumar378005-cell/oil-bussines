from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentGateway(str, Enum):
    RAZORPAY = "RAZORPAY"
    STRIPE = "STRIPE"
    COD = "COD"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True, max_length=64)
    
    # Customer Details
    customer_name: str = Field(max_length=255)
    customer_email: str = Field(index=True, max_length=255)
    customer_phone: str = Field(max_length=20)
    
    # Shipping Address
    address_line1: str = Field(max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: str = Field(max_length=100)
    state: str = Field(max_length=100)
    postal_code: str = Field(max_length=20)
    country: str = Field(default="India", max_length=100)

    # Financial Breakdown
    subtotal: float = Field(default=0.0)
    tax_amount: float = Field(default=0.0)
    shipping_fee: float = Field(default=0.0)
    total_amount: float = Field(default=0.0)
    currency: str = Field(default="INR", max_length=10)

    # Status & Payment
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    payment_gateway: Optional[PaymentGateway] = Field(default=None)
    gateway_order_id: Optional[str] = Field(default=None, index=True, max_length=128)
    gateway_payment_id: Optional[str] = Field(default=None, index=True, max_length=128)
    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    items: List["OrderItem"] = Relationship(back_populates="order", cascade_delete=True)
    transactions: List["PaymentTransaction"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    product_name: str = Field(max_length=255)
    volume_ml: int = Field(default=1000)
    unit_price: float = Field(default=0.0)
    quantity: int = Field(default=1, ge=1)
    line_total: float = Field(default=0.0)

    # Relationships
    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="order_items")
