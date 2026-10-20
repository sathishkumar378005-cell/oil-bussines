import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import stripe
from app.core.config import settings
from app.models.order import Order

logger = logging.getLogger(__name__)


class StripeService:

    @classmethod
    def is_configured(cls) -> bool:
        return bool(
            settings.STRIPE_API_KEY 
            and not settings.STRIPE_API_KEY.startswith("sk_test_Your")
        )

    @classmethod
    def create_payment_intent(cls, order: Order) -> Dict[str, Any]:
        """
        Creates a Stripe PaymentIntent for the given order.
        Amount is in the smallest currency unit (cents/paise).
        """
        amount_smallest_unit = int(round(order.total_amount * 100))
        currency = order.currency.lower()

        if cls.is_configured():
            stripe.api_key = settings.STRIPE_API_KEY
            try:
                intent = stripe.PaymentIntent.create(
                    amount=amount_smallest_unit,
                    currency=currency,
                    metadata={
                        "order_number": order.order_number,
                        "customer_name": order.customer_name,
                        "customer_email": order.customer_email
                    },
                    description=f"Latha Oils - Order {order.order_number}"
                )
                return {
                    "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                    "client_secret": intent.client_secret,
                    "payment_intent_id": intent.id,
                    "amount_in_cents": amount_smallest_unit,
                    "currency": currency.upper(),
                    "order_number": order.order_number
                }
            except Exception as e:
                logger.error(f"Stripe PaymentIntent creation failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Stripe gateway error: {str(e)}"
                )
        else:
            # Dev mock fallback
            mock_id = f"pi_mock_{order.order_number.replace('-', '_')}"
            logger.warning(f"Using mock Stripe PaymentIntent: {mock_id} (Configure STRIPE_API_KEY in .env for live mode)")
            return {
                "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                "client_secret": f"{mock_id}_secret_mock",
                "payment_intent_id": mock_id,
                "amount_in_cents": amount_smallest_unit,
                "currency": currency.upper(),
                "order_number": order.order_number
            }

    @classmethod
    def verify_webhook_event(cls, payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        """
        Verifies and parses a Stripe webhook event using the webhook signature.
        """
        if cls.is_configured() and settings.STRIPE_WEBHOOK_SECRET and not settings.STRIPE_WEBHOOK_SECRET.startswith("whsec_Your"):
            stripe.api_key = settings.STRIPE_API_KEY
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
                return event
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Invalid Stripe webhook signature: {e}")
                return None
            except Exception as e:
                logger.error(f"Stripe webhook construct event error: {e}")
                return None
        return None
