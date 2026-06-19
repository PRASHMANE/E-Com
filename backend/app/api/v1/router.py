from fastapi import APIRouter

from app.api.v1.endpoints import auth, users
from app.api.v1.endpoints import (
    auth,
    categories,
    products,
    users,
)
from app.api.v1.endpoints import wishlist
from app.api.v1.endpoints import cart
from app.api.v1.endpoints import orders
from app.api.v1.endpoints import reviews
from app.api.v1.endpoints import addresses

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(wishlist.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(reviews.router)
api_router.include_router(addresses.router)