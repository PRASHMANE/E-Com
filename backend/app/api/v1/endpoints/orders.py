from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post(
    "/checkout",
    response_model=OrderResponse
)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == current_user.id
        )
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total = Decimal("0.00")

    for item in cart_items:
        if item.quantity > item.product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.product.name}"
            )

        total += item.quantity * item.product.price

    order = Order(
        user_id=current_user.id,
        total_amount=total
    )

    db.add(order)
    db.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        db.add(order_item)

        item.product.stock -= item.quantity

    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(order)

    return order

@router.get(
    "/",
    response_model=list[OrderResponse]
)
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .all()
    )

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order