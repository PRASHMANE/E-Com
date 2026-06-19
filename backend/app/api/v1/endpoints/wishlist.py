from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.models.wishlist import WishlistItem
from app.schemas.wishlist import WishlistCreate

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)


@router.post("/")
def add_to_wishlist(
    payload: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = (
        db.query(Product)
        .filter(Product.id == payload.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing = (
        db.query(WishlistItem)
        .filter(
            WishlistItem.user_id == current_user.id,
            WishlistItem.product_id == payload.product_id
        )
        .first()
    )

    if existing:
        return {"message": "Already in wishlist"}

    item = WishlistItem(
        user_id=current_user.id,
        product_id=payload.product_id
    )

    db.add(item)
    db.commit()

    return {"message": "Added to wishlist"}


@router.get("/")
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = (
        db.query(WishlistItem)
        .filter(
            WishlistItem.user_id == current_user.id
        )
        .all()
    )

    return items

@router.delete("/{product_id}")
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = (
        db.query(WishlistItem)
        .filter(
            WishlistItem.user_id == current_user.id,
            WishlistItem.product_id == product_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db.delete(item)
    db.commit()

    return {"message": "Removed from wishlist"}