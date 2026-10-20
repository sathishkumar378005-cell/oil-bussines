import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.core.database import get_session
from app.models.product import Product

# Use in-memory SQLite for testing
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(test_engine)
    # Seed one test product
    with Session(test_engine) as session:
        p = Product(
            name="Test Cold Pressed Groundnut Oil",
            slug="test-groundnut-oil",
            category="Cold Pressed Oils",
            description="Pure test oil",
            volume_ml=1000,
            price=300.0,
            stock_quantity=20,
            sku="TEST-GND-1L",
            is_active=True
        )
        session.add(p)
        session.commit()
    yield
    SQLModel.metadata.drop_all(test_engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_products_list():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["sku"] == "TEST-GND-1L"


def test_cart_and_checkout_flow():
    session_id = "test-session-12345"
    
    # 1. Add item to cart
    add_resp = client.post(
        f"/api/v1/cart/items?session_id={session_id}",
        json={"product_id": 1, "quantity": 2}
    )
    assert add_resp.status_code == 201
    cart_data = add_resp.json()
    assert cart_data["item_count"] == 2
    assert cart_data["subtotal"] == 600.0  # 2 * 300.0

    # 2. Checkout order
    checkout_payload = {
        "session_id": session_id,
        "shipping_address": {
            "customer_name": "Ramesh Kumar",
            "customer_email": "ramesh@example.com",
            "customer_phone": "9876543210",
            "address_line1": "12, Gandhi Street",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "postal_code": "600001",
            "country": "India"
        },
        "payment_gateway": "RAZORPAY"
    }
    order_resp = client.post("/api/v1/orders/checkout", json=checkout_payload)
    assert order_resp.status_code == 201
    order_data = order_resp.json()
    order_num = order_data["order_number"]
    assert order_data["status"] == "PENDING"
    assert order_data["subtotal"] == 600.0
    assert order_data["tax_amount"] == 30.0  # 5% of 600
    assert order_data["total_amount"] == 690.0  # 600 + 30 + 60 (shipping below 999 threshold)

    # 3. Create Razorpay Order
    rzp_create_resp = client.post(
        "/api/v1/payments/razorpay/create-order",
        json={"order_number": order_num}
    )
    assert rzp_create_resp.status_code == 200
    rzp_data = rzp_create_resp.json()
    assert rzp_data["amount_in_paise"] == 69000  # 690 * 100 paise
    assert "razorpay_order_id" in rzp_data

    # 4. Attempt fraudulent signature verification -> Must fail!
    fake_verify_resp = client.post(
        "/api/v1/payments/razorpay/verify",
        json={
            "order_number": order_num,
            "razorpay_order_id": rzp_data["razorpay_order_id"],
            "razorpay_payment_id": "pay_fake123",
            "razorpay_signature": "invalid_forged_signature"
        }
    )
    assert fake_verify_resp.status_code == 400
    assert "tampering detected" in fake_verify_resp.json()["detail"]

    # 5. Successful mock signature verification
    valid_verify_resp = client.post(
        "/api/v1/payments/razorpay/verify",
        json={
            "order_number": order_num,
            "razorpay_order_id": rzp_data["razorpay_order_id"],
            "razorpay_payment_id": "pay_test123",
            "razorpay_signature": "mock_sig_valid"
        }
    )
    assert valid_verify_resp.status_code == 200
    assert valid_verify_resp.json()["order_status"] == "PAID"


def test_stripe_intent_flow():
    session_id = "test-stripe-session"
    client.post(f"/api/v1/cart/items?session_id={session_id}", json={"product_id": 1, "quantity": 4})
    
    checkout_payload = {
        "session_id": session_id,
        "shipping_address": {
            "customer_name": "Anita Devi",
            "customer_email": "anita@example.com",
            "customer_phone": "9876543211",
            "address_line1": "45 Lake View Road",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560001",
            "country": "India"
        },
        "payment_gateway": "STRIPE"
    }
    order_resp = client.post("/api/v1/orders/checkout", json=checkout_payload)
    order_data = order_resp.json()
    order_num = order_data["order_number"]

    stripe_resp = client.post("/api/v1/payments/stripe/create-intent", json={"order_number": order_num})
    assert stripe_resp.status_code == 200
    s_data = stripe_resp.json()
    assert "client_secret" in s_data
    assert s_data["currency"] == "INR"
