from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class TransactionStatus(str, Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentTransaction(SQLModel, table=True):
    __tablename__ = "payment_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    gateway: str = Field(max_length=50)  # RAZORPAY / STRIPE
    gateway_order_id: Optional[str] = Field(default=None, index=True, max_length=128)
    gateway_payment_id: Optional[str] = Field(default=None, index=True, max_length=128)
    amount: float
    currency: str = Field(default="INR", max_length=10)
    status: TransactionStatus = Field(default=TransactionStatus.INITIATED)
    signature: Optional[str] = None
    raw_payload: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    order: Optional["Order"] = Relationship(back_populates="transactions")
