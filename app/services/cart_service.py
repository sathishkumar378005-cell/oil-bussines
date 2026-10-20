from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.core.config import settings
from app.schemas.cart import CartRead, CartItemRead


class CartService:

    @staticmethod
    def get_or_create_cart(session: Session, session_id: str) -> Cart:
        statement = select(Cart).where(Cart.session_id == session_id)
        cart = session.exec(statement).first()
        if not cart:
            cart = Cart(session_id=session_id)
            session.add(cart)
            session.commit()
            session.refresh(cart)
        return cart

    @staticmethod
    def add_item(session: Session, session_id: str, product_id: int, quantity: int = 1) -> Cart:
        cart = CartService.get_or_create_cart(session, session_id)

        # Check product validity and stock
        product = session.get(Product, product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found or is currently unavailable."
            )
        
        if product.stock_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({quantity}) exceeds available stock ({product.stock_quantity}) for {product.name}."
            )

        # Check if item already exists in cart
        statement = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        cart_item = session.exec(statement).first()

        if cart_item:
            new_qty = cart_item.quantity + quantity
            if product.stock_quantity < new_qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot add more. Total in cart ({new_qty}) exceeds stock ({product.stock_quantity})."
                )
            cart_item.quantity = new_qty
            session.add(cart_item)
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(cart_item)

        session.commit()
        session.refresh(cart)
        return cart

    @staticmethod
    def update_item_quantity(session: Session, session_id: str, item_id: int, quantity: int) -> Cart:
        cart = CartService.get_or_create_cart(session, session_id)
        cart_item = session.get(CartItem, item_id)
        if not cart_item or cart_item.cart_id != cart.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in your cart."
            )

        product = session.get(Product, cart_item.product_id)
        if product and product.stock_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({quantity}) exceeds available stock ({product.stock_quantity})."
            )

        cart_item.quantity = quantity
        session.add(cart_item)
        session.commit()
        session.refresh(cart)
        return cart

    @staticmethod
    def remove_item(session: Session, session_id: str, item_id: int) -> Cart:
        cart = CartService.get_or_create_cart(session, session_id)
        cart_item = session.get(CartItem, item_id)
        if cart_item and cart_item.cart_id == cart.id:
            session.delete(cart_item)
            session.commit()
            session.refresh(cart)
        return cart

    @staticmethod
    def clear_cart(session: Session, cart_id: int) -> None:
        statement = select(CartItem).where(CartItem.cart_id == cart_id)
        items = session.exec(statement).all()
        for item in items:
            session.delete(item)
        session.commit()

    @staticmethod
    def get_cart_view(session: Session, session_id: str) -> CartRead:
        cart = CartService.get_or_create_cart(session, session_id)
        
        items_read = []
        subtotal = 0.0
        item_count = 0

        # Load product details for items
        statement = select(CartItem).where(CartItem.cart_id == cart.id)
        cart_items = session.exec(statement).all()

        for item in cart_items:
            product = session.get(Product, item.product_id)
            if product:
                item_total = round(product.price * item.quantity, 2)
                subtotal += item_total
                item_count += item.quantity
                
                # Format product schema
                items_read.append(
                    CartItemRead(
                        id=item.id,
                        product_id=product.id,
                        quantity=item.quantity,
                        product=product,
                        item_subtotal=item_total
                    )
                )

        subtotal = round(subtotal, 2)
        # Tax Calculation (e.g. 5% GST for cold pressed oils)
        estimated_tax = round((subtotal * settings.TAX_RATE_PERCENTAGE) / 100.0, 2)
        
        # Shipping fee logic
        if subtotal == 0 or subtotal >= settings.FREE_SHIPPING_THRESHOLD:
            estimated_shipping = 0.0
        else:
            estimated_shipping = settings.DEFAULT_SHIPPING_FEE

        estimated_total = round(subtotal + estimated_tax + estimated_shipping, 2)

        return CartRead(
            id=cart.id,
            session_id=cart.session_id,
            items=items_read,
            item_count=item_count,
            subtotal=subtotal,
            estimated_tax=estimated_tax,
            estimated_shipping=estimated_shipping,
            estimated_total=estimated_total
        )
