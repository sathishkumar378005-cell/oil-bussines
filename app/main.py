import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api_router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("latha_oils_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database tables and seed if necessary."""
    logger.info("Initializing Latha Oils database schema...")
    init_db()
    logger.info("Database schema initialized successfully.")
    yield
    logger.info("Shutting down Latha Oils API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Latha Oils - E-Commerce Backend API 🛢️🍃
    
    Production-ready backend for pure cold-pressed and wood-pressed edible oils.
    
    ### Key Features:
    * **Tamper-Proof Checkout & Server Calculations**: All product totals, taxes (GST 5%), and shipping fees are calculated authoritatively on the server.
    * **Dual Payment Gateways**: Full support for both **Razorpay** (UPI, NetBanking, Cards) and **Stripe** (International & domestic cards).
    * **Cryptographic Security**: HMAC-SHA256 signature verification for payments and webhooks with constant-time equality checks.
    * **Inventory & Cart Management**: Atomic inventory stock reservation and guest session-based carting.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "supported_gateways": ["RAZORPAY", "STRIPE"]
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
