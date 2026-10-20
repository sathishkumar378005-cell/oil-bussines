from fastapi import APIRouter
from app.api.v1.endpoints import products, cart, orders, payments

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(cart.router, prefix="/cart", tags=["Shopping Cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders & Checkout"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments (Razorpay & Stripe)"])
