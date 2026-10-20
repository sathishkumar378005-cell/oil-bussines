import hmac
import hashlib
from typing import Optional
from fastapi import HTTPException, status
from app.core.config import settings


def verify_razorpay_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> bool:
    """
    Securely verify Razorpay payment signature using HMAC SHA256.
    Computes HMAC of order_id|payment_id using RAZORPAY_KEY_SECRET.
    """
    if not settings.RAZORPAY_KEY_SECRET or settings.RAZORPAY_KEY_SECRET.startswith("Your"):
        # If in dev without valid keys, prevent false security but allow logging
        pass

    msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
    secret = settings.RAZORPAY_KEY_SECRET.encode("utf-8")
    generated_signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    
    # Use hmac.compare_digest to prevent timing attacks
    return hmac.compare_digest(generated_signature, razorpay_signature)


def verify_razorpay_webhook_signature(
    payload_body: bytes,
    signature_header: str
) -> bool:
    """
    Verify Razorpay webhook payload against the X-Razorpay-Signature header.
    """
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        return False
    
    secret = settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8")
    generated_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(generated_signature, signature_header)
