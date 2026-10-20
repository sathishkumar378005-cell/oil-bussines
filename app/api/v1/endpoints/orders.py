from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCheckoutRequest, OrderRead
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED, summary="Create order from cart")
def checkout_cart(
    request: OrderCheckoutRequest,
    session: Session = Depends(get_session)
):
    """
    Initiates checkout:
    1. Validates and locks product prices from database (tamper-proof).
    2. Validates and reduces inventory stock.
    3. Calculates tax, shipping, and total.
    4. Creates order record and clears cart.
    """
    order = OrderService.create_order_from_cart(session, request)
    # Eager load items
    statement = select(OrderItem).where(OrderItem.order_id == order.id)
    order.items = session.exec(statement).all()
    return order


@router.get("/{order_number}", response_model=OrderRead, summary="Get order by order number")
def get_order(
    order_number: str,
    session: Session = Depends(get_session)
):
    """Fetches full order details, tracking status, and line items."""
    order = OrderService.get_order_by_number(session, order_number)
    statement = select(OrderItem).where(OrderItem.order_id == order.id)
    order.items = session.exec(statement).all()
    return order


@router.get("/", response_model=List[OrderRead], summary="List orders")
def list_orders(
    customer_email: Optional[str] = Query(None, description="Filter orders by customer email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Retrieves orders with optional customer email filtering and pagination."""
    statement = select(Order).order_by(Order.created_at.desc())
    if customer_email:
        statement = statement.where(Order.customer_email == customer_email)
    
    statement = statement.offset(skip).limit(limit)
    orders = session.exec(statement).all()
    for o in orders:
        item_stmt = select(OrderItem).where(OrderItem.order_id == o.id)
        o.items = session.exec(item_stmt).all()
    return orders
