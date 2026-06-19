from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
)

router = APIRouter(
    prefix="/products/{product_id}/reviews",
    tags=["Reviews"]
)


@router.post(
    "/",
    response_model=ReviewResponse
)
def create_review(
    product_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing = (
        db.query(Review)
        .filter(
            Review.user_id == current_user.id,
            Review.product_id == product_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Review already exists"
        )

    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=payload.rating,
        comment=payload.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review

@router.get(
    "/",
    response_model=list[ReviewResponse]
)
def list_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .all()
    )