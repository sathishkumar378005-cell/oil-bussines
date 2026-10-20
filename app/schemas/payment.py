from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# ===================== RAZORPAY SCHEMAS =====================

class RazorpayCreateOrderRequest(BaseModel):
    order_number: str = Field(..., description="Latha Oils order number")


class RazorpayCreateOrderResponse(BaseModel):
    key_id: str
    razorpay_order_id: str
    amount_in_paise: int
    currency: str
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str


class RazorpayVerifyPaymentRequest(BaseModel):
    order_number: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ===================== STRIPE SCHEMAS =====================

class StripeCreateIntentRequest(BaseModel):
    order_number: str = Field(..., description="Latha Oils order number")


class StripeCreateIntentResponse(BaseModel):
    publishable_key: str
    client_secret: str
    payment_intent_id: str
    amount_in_cents: int
    currency: str
    order_number: str


# ===================== GENERAL PAYMENT STATUS =====================

class PaymentStatusResponse(BaseModel):
    success: bool
    message: str
    order_number: str
    order_status: str
    payment_gateway: str
    transaction_id: Optional[str] = None
