from typing import Optional
from fastapi import APIRouter, Depends, Header, Query, status
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.cart import CartRead, CartItemCreate, CartItemUpdate
from app.services.cart_service import CartService

router = APIRouter()


def resolve_session_id(
    session_id: Optional[str] = Query(None, description="Cart session identifier"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID", description="Cart session header")
) -> str:
    """Helper to extract session_id from query parameter or header."""
    sid = session_id or x_session_id
    if not sid:
        # Default fallback session ID for quick tests if omitted
        return "default-guest-session"
    return sid


@router.get("/", response_model=CartRead, summary="Get current cart and totals")
def get_cart(
    session_id: str = Depends(resolve_session_id),
    db: Session = Depends(get_session)
):
    """Fetches the user's shopping cart, items, subtotal, tax, and shipping."""
    return CartService.get_cart_view(db, session_id)


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED, summary="Add item to cart")
def add_to_cart(
    item_in: CartItemCreate,
    session_id: str = Depends(resolve_session_id),
    db: Session = Depends(get_session)
):
    """Adds a cold pressed oil product to the cart with stock verification."""
    CartService.add_item(db, session_id, item_in.product_id, item_in.quantity)
    return CartService.get_cart_view(db, session_id)


@router.put("/items/{item_id}", response_model=CartRead, summary="Update cart item quantity")
def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    session_id: str = Depends(resolve_session_id),
    db: Session = Depends(get_session)
):
    """Updates the quantity of an item inside the user's cart."""
    CartService.update_item_quantity(db, session_id, item_id, item_update.quantity)
    return CartService.get_cart_view(db, session_id)


@router.delete("/items/{item_id}", response_model=CartRead, summary="Remove item from cart")
def remove_cart_item(
    item_id: int,
    session_id: str = Depends(resolve_session_id),
    db: Session = Depends(get_session)
):
    """Deletes an individual item line from the cart."""
    CartService.remove_item(db, session_id, item_id)
    return CartService.get_cart_view(db, session_id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Clear entire cart")
def clear_cart(
    session_id: str = Depends(resolve_session_id),
    db: Session = Depends(get_session)
):
    """Empties all items in the cart."""
    cart = CartService.get_or_create_cart(db, session_id)
    CartService.clear_cart(db, cart.id)
    return None
