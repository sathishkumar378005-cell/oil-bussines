from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.order import OrderStatus, PaymentGateway


class ShippingAddressSchema(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=255)
    customer_email: EmailStr
    customer_phone: str = Field(..., pattern=r"^[0-9+\-\s]{10,15}$")
    address_line1: str = Field(..., min_length=5, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=5, max_length=20)
    country: str = Field(default="India", max_length=100)


class OrderCheckoutRequest(BaseModel):
    session_id: str = Field(..., description="The user or visitor's active cart session ID")
    shipping_address: ShippingAddressSchema
    payment_gateway: PaymentGateway = Field(default=PaymentGateway.RAZORPAY)
    notes: Optional[str] = None


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    volume_ml: int
    unit_price: float
    quantity: int
    line_total: float

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    postal_code: str
    country: str
    subtotal: float
    tax_amount: float
    shipping_fee: float
    total_amount: float
    currency: str
    status: OrderStatus
    payment_gateway: Optional[PaymentGateway]
    gateway_order_id: Optional[str]
    gateway_payment_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []

    model_config = ConfigDict(from_attributes=True)
