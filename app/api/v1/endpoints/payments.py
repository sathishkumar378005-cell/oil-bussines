import json
import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlmodel import Session
from app.core.database import get_session
from app.models.order import Order, OrderStatus, PaymentGateway
from app.schemas.payment import (
    RazorpayCreateOrderRequest,
    RazorpayCreateOrderResponse,
    RazorpayVerifyPaymentRequest,
    StripeCreateIntentRequest,
    StripeCreateIntentResponse,
    PaymentStatusResponse,
)
from app.services.order_service import OrderService
from app.services.razorpay_service import RazorpayService
from app.services.stripe_service import StripeService

logger = logging.getLogger(__name__)
router = APIRouter()


# =====================================================================
#                          RAZORPAY ENDPOINTS
# =====================================================================

@router.post(
    "/razorpay/create-order",
    response_model=RazorpayCreateOrderResponse,
    summary="Create Razorpay Order for Checkout"
)
def create_razorpay_order(
    request: RazorpayCreateOrderRequest,
    db: Session = Depends(get_session)
):
    """
    Creates an official Razorpay order with the exact order total (converted to paise).
    Validates that the order exists and is in PENDING status.
    """
    order = OrderService.get_order_by_number(db, request.order_number)
    
    if order.status == OrderStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order has already been paid."
        )

    order.payment_gateway = PaymentGateway.RAZORPAY
    order.status = OrderStatus.PAYMENT_INITIATED
    db.add(order)
    db.commit()

    razorpay_data = RazorpayService.create_order(order)
    
    # Store razorpay order ID on the order
    order.gateway_order_id = razorpay_data["razorpay_order_id"]
    db.add(order)
    db.commit()

    return razorpay_data


@router.post(
    "/razorpay/verify",
    response_model=PaymentStatusResponse,
    summary="Verify Razorpay Payment Signature"
)
def verify_razorpay_payment(
    request: RazorpayVerifyPaymentRequest,
    db: Session = Depends(get_session)
):
    """
    Validates Razorpay HMAC SHA256 payment signature.
    Prevents tampering and marks the order as PAID only when verification passes.
    """
    order = OrderService.get_order_by_number(db, request.order_number)

    is_valid = RazorpayService.verify_payment(
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature
    )

    if not is_valid:
        OrderService.record_payment_failure(
            session=db,
            order=order,
            gateway="RAZORPAY",
            error_message="Invalid payment signature",
            raw_payload=json.dumps(request.model_dump())
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment signature verification failed. Possible tampering detected."
        )

    # Record success and transition state
    OrderService.record_payment_success(
        session=db,
        order=order,
        gateway="RAZORPAY",
        gateway_order_id=request.razorpay_order_id,
        gateway_payment_id=request.razorpay_payment_id,
        signature=request.razorpay_signature,
        raw_payload=json.dumps(request.model_dump())
    )

    return PaymentStatusResponse(
        success=True,
        message="Payment verified successfully. Order confirmed!",
        order_number=order.order_number,
        order_status=order.status.value,
        payment_gateway="RAZORPAY",
        transaction_id=request.razorpay_payment_id
    )


@router.post("/razorpay/webhook", summary="Razorpay Webhook Handler")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(..., alias="X-Razorpay-Signature"),
    db: Session = Depends(get_session)
):
    """
    Listens to server-to-server Razorpay webhooks (e.g. payment.captured, payment.failed)
    with cryptographic HMAC signature verification.
    """
    body = await request.body()
    
    if not RazorpayService.verify_webhook(body, x_razorpay_signature):
        logger.warning("Razorpay webhook signature verification failed.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature."
        )

    payload = json.loads(body.decode("utf-8"))
    event = payload.get("event")
    logger.info(f"Received verified Razorpay webhook event: {event}")

    if event == "payment.captured":
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        notes = payment_entity.get("notes", {})
        order_number = notes.get("order_number") or payment_entity.get("description")
        payment_id = payment_entity.get("id")
        rp_order_id = payment_entity.get("order_id")

        if order_number:
            try:
                order = OrderService.get_order_by_number(db, order_number)
                OrderService.record_payment_success(
                    session=db,
                    order=order,
                    gateway="RAZORPAY",
                    gateway_order_id=rp_order_id,
                    gateway_payment_id=payment_id,
                    raw_payload=json.dumps(payload)
                )
            except Exception as e:
                logger.error(f"Error processing captured payment for {order_number}: {e}")

    return {"status": "ok"}


# =====================================================================
#                          STRIPE ENDPOINTS
# =====================================================================

@router.post(
    "/stripe/create-intent",
    response_model=StripeCreateIntentResponse,
    summary="Create Stripe PaymentIntent for Checkout"
)
def create_stripe_intent(
    request: StripeCreateIntentRequest,
    db: Session = Depends(get_session)
):
    """
    Generates a Stripe PaymentIntent for the client to confirm via Stripe Elements.
    Calculates exact amount in cents/paise directly on server.
    """
    order = OrderService.get_order_by_number(db, request.order_number)

    if order.status == OrderStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order has already been paid."
        )

    order.payment_gateway = PaymentGateway.STRIPE
    order.status = OrderStatus.PAYMENT_INITIATED
    db.add(order)
    db.commit()

    intent_data = StripeService.create_payment_intent(order)

    order.gateway_order_id = intent_data["payment_intent_id"]
    db.add(order)
    db.commit()

    return intent_data


@router.post("/stripe/webhook", summary="Stripe Webhook Handler")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    db: Session = Depends(get_session)
):
    """
    Listens to Stripe asynchronous events (payment_intent.succeeded, payment_intent.payment_failed)
    with strict signature verification.
    """
    body = await request.body()
    event = StripeService.verify_webhook_event(body, stripe_signature)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature."
        )

    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        order_number = data_object.get("metadata", {}).get("order_number")
        payment_intent_id = data_object.get("id")
        
        if order_number:
            try:
                order = OrderService.get_order_by_number(db, order_number)
                OrderService.record_payment_success(
                    session=db,
                    order=order,
                    gateway="STRIPE",
                    gateway_order_id=payment_intent_id,
                    gateway_payment_id=payment_intent_id,
                    raw_payload=json.dumps(event)
                )
            except Exception as e:
                logger.error(f"Error handling Stripe payment_intent.succeeded for {order_number}: {e}")

    elif event_type == "payment_intent.payment_failed":
        order_number = data_object.get("metadata", {}).get("order_number")
        last_error = data_object.get("last_payment_error", {}).get("message", "Payment failed")
        if order_number:
            try:
                order = OrderService.get_order_by_number(db, order_number)
                OrderService.record_payment_failure(
                    session=db,
                    order=order,
                    gateway="STRIPE",
                    error_message=last_error,
                    raw_payload=json.dumps(event)
                )
            except Exception as e:
                logger.error(f"Error handling Stripe payment_failed for {order_number}: {e}")

    return {"status": "success"}
