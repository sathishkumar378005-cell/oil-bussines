import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Latha Oils - Organic & Cold Pressed Oils E-Commerce API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Configuration (MySQL default, with SQLite dev fallback)
    # Format: mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>?charset=utf8mb4
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/latha_oils?charset=utf8mb4"

    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "https://lathaoils.com",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str = "super-secret-development-key-change-in-production"
    
    # Razorpay Settings
    RAZORPAY_KEY_ID: str = "rzp_test_YourKeyHere"
    RAZORPAY_KEY_SECRET: str = "YourRazorpaySecretHere"
    RAZORPAY_WEBHOOK_SECRET: str = "YourRazorpayWebhookSecretHere"

    # Stripe Settings
    STRIPE_API_KEY: str = "sk_test_YourStripeSecretKeyHere"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_YourStripePublishableKeyHere"
    STRIPE_WEBHOOK_SECRET: str = "whsec_YourStripeWebhookSecretHere"

    # Currencies & Business Settings
    DEFAULT_CURRENCY: str = "INR"
    TAX_RATE_PERCENTAGE: float = 5.0  # 5% GST on edible cold pressed oils in India
    FREE_SHIPPING_THRESHOLD: float = 999.0
    DEFAULT_SHIPPING_FEE: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
