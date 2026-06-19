from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.core.permissions import require_role


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(
        require_role("admin")
    )
):
    return {
        "message": "Welcome admin",
        "email": current_user.email
    }