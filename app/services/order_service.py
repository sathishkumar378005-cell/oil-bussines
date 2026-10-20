import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus, PaymentGateway
from app.models.payment import PaymentTransaction, TransactionStatus
from app.schemas.order import OrderCheckoutRequest
from app.services.cart_service import CartService
from app.core.config import settings


class OrderService:

    @staticmethod
    def generate_order_number() -> str:
        date_str = datetime.utcnow().strftime("%Y%m%d")
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"LO-{date_str}-{unique_suffix}"

    @staticmethod
    def create_order_from_cart(session: Session, request: OrderCheckoutRequest) -> Order:
        """
        Secure checkout:
        1. Fetch active cart.
        2. Validate items and inventory.
        3. Authoritatively compute prices directly from database products (immune to client tampering).
        4. Decrement inventory stock.
        5. Create Order and OrderItems.
        6. Empty Cart.
        """
        cart = CartService.get_or_create_cart(session, request.session_id)
        
        statement = select(CartItem).where(CartItem.cart_id == cart.id)
        cart_items = session.exec(statement).all()

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your cart is empty. Please add products before checking out."
            )

        # Validate stock and calculate totals
        subtotal = 0.0
        order_items_to_create = []

        for item in cart_items:
            product = session.get(Product, item.product_id)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID {item.product_id} is no longer available."
                )
            
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, In cart: {item.quantity}"
                )

            # Deduct stock safely
            product.stock_quantity -= item.quantity
            session.add(product)

            # Compute line total securely
            line_total = round(product.price * item.quantity, 2)
            subtotal += line_total

            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                volume_ml=product.volume_ml,
                unit_price=product.price,
                quantity=item.quantity,
                line_total=line_total
            )
            order_items_to_create.append(order_item)

        subtotal = round(subtotal, 2)
        tax_amount = round((subtotal * settings.TAX_RATE_PERCENTAGE) / 100.0, 2)
        shipping_fee = 0.0 if subtotal >= settings.FREE_SHIPPING_THRESHOLD else settings.DEFAULT_SHIPPING_FEE
        total_amount = round(subtotal + tax_amount + shipping_fee, 2)

        addr = request.shipping_address
        order = Order(
            order_number=OrderService.generate_order_number(),
            customer_name=addr.customer_name,
            customer_email=addr.customer_email,
            customer_phone=addr.customer_phone,
            address_line1=addr.address_line1,
            address_line2=addr.address_line2,
            city=addr.city,
            state=addr.state,
            postal_code=addr.postal_code,
            country=addr.country,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            currency=settings.DEFAULT_CURRENCY,
            status=OrderStatus.PENDING,
            payment_gateway=request.payment_gateway,
            notes=request.notes
        )

        session.add(order)
        session.flush()  # get order.id

        # Associate order items
        for oi in order_items_to_create:
            oi.order_id = order.id
            session.add(oi)

        # Clear cart now that order is created
        CartService.clear_cart(session, cart.id)

        session.commit()
        session.refresh(order)
        return order

    @staticmethod
    def get_order_by_number(session: Session, order_number: str) -> Order:
        statement = select(Order).where(Order.order_number == order_number)
        order = session.exec(statement).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_number} not found."
            )
        return order

    @staticmethod
    def record_payment_success(
        session: Session,
        order: Order,
        gateway: str,
        gateway_order_id: Optional[str],
        gateway_payment_id: str,
        signature: Optional[str] = None,
        raw_payload: Optional[str] = None
    ) -> Order:
        """
        Record successful payment and advance order status.
        Protects against duplicate processing (idempotency).
        """
        if order.status == OrderStatus.PAID:
            return order  # Already processed safely

        order.status = OrderStatus.PAID
        order.gateway_order_id = gateway_order_id or order.gateway_order_id
        order.gateway_payment_id = gateway_payment_id
        order.updated_at = datetime.utcnow()
        session.add(order)

        # Add audit transaction record
        tx = PaymentTransaction(
            order_id=order.id,
            gateway=gateway,
            gateway_order_id=gateway_order_id,
            gateway_payment_id=gateway_payment_id,
            amount=order.total_amount,
            currency=order.currency,
            status=TransactionStatus.SUCCESS,
            signature=signature,
            raw_payload=raw_payload
        )
        session.add(tx)
        session.commit()
        session.refresh(order)
        return order

    @staticmethod
    def record_payment_failure(
        session: Session,
        order: Order,
        gateway: str,
        error_message: str,
        raw_payload: Optional[str] = None
    ) -> Order:
        order.status = OrderStatus.FAILED
        order.updated_at = datetime.utcnow()
        session.add(order)

        tx = PaymentTransaction(
            order_id=order.id,
            gateway=gateway,
            gateway_order_id=order.gateway_order_id,
            gateway_payment_id=order.gateway_payment_id,
            amount=order.total_amount,
            currency=order.currency,
            status=TransactionStatus.FAILED,
            error_message=error_message,
            raw_payload=raw_payload
        )
        session.add(tx)
        session.commit()
        session.refresh(order)
        return order
