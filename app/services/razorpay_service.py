import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import razorpay
from app.core.config import settings
from app.core.security import verify_razorpay_payment_signature, verify_razorpay_webhook_signature
from app.models.order import Order

logger = logging.getLogger(__name__)


class RazorpayService:

    @classmethod
    def get_client(cls) -> Optional[razorpay.Client]:
        """Returns the Razorpay client if configured, otherwise None for mock/dev fallback."""
        if (
            settings.RAZORPAY_KEY_ID 
            and not settings.RAZORPAY_KEY_ID.startswith("Your")
            and settings.RAZORPAY_KEY_SECRET 
            and not settings.RAZORPAY_KEY_SECRET.startswith("Your")
        ):
            return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return None

    @classmethod
    def create_order(cls, order: Order) -> Dict[str, Any]:
        """
        Creates an official Razorpay order.
        Amount must be provided in the lowest currency unit (paise for INR).
        """
        amount_in_paise = int(round(order.total_amount * 100))
        
        client = cls.get_client()
        if client:
            try:
                order_data = {
                    "amount": amount_in_paise,
                    "currency": order.currency,
                    "receipt": order.order_number,
                    "notes": {
                        "customer_name": order.customer_name,
                        "customer_email": order.customer_email,
                        "customer_phone": order.customer_phone,
                        "order_number": order.order_number
                    }
                }
                rp_order = client.order.create(data=order_data)
                return {
                    "key_id": settings.RAZORPAY_KEY_ID,
                    "razorpay_order_id": rp_order["id"],
                    "amount_in_paise": amount_in_paise,
                    "currency": order.currency,
                    "order_number": order.order_number,
                    "customer_name": order.customer_name,
                    "customer_email": order.customer_email,
                    "customer_phone": order.customer_phone
                }
            except Exception as e:
                logger.error(f"Razorpay order creation error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Razorpay gateway error: {str(e)}"
                )
        else:
            # Development / Mock Mode fallback when keys not yet replaced
            mock_order_id = f"order_mock_{order.order_number.replace('-', '_')}"
            logger.warning(f"Using mock Razorpay order: {mock_order_id} (Configure RAZORPAY_KEY_ID in .env for live mode)")
            return {
                "key_id": settings.RAZORPAY_KEY_ID,
                "razorpay_order_id": mock_order_id,
                "amount_in_paise": amount_in_paise,
                "currency": order.currency,
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone
            }

    @classmethod
    def verify_payment(
        cls,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verifies the signature sent by Razorpay Checkout.
        Uses constant-time comparison to prevent timing attacks.
        """
        client = cls.get_client()
        if client:
            try:
                params = {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature
                }
                client.utility.verify_payment_signature(params)
                return True
            except razorpay.errors.SignatureVerificationError:
                return False
            except Exception as e:
                logger.error(f"Error in Razorpay signature verification: {str(e)}")
                return False
        else:
            # Dev mock fallback check
            return verify_razorpay_payment_signature(
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature
            ) or razorpay_signature.startswith("mock_sig")

    @classmethod
    def verify_webhook(cls, body: bytes, signature: str) -> bool:
        """Verifies webhook signature using Webhook Secret."""
        return verify_razorpay_webhook_signature(body, signature)
