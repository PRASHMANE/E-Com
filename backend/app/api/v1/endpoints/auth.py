from sqlalchemy.orm import Session
import time
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate

from app.core.redis import redis_client
from app.services.email_service import send_verification_email
from app.utils.otp import generate_otp


from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.otp import generate_otp
from app.services.email_service import (
    send_password_reset_email,
)
from app.core.redis import redis_client

from app.schemas.token import (
    Token,
    RefreshTokenRequest
)
from app.core.security import (
    decode_token,
)

from app.schemas.user import (
    UserCreate,
    VerifyOTP,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate OTP
    otp = generate_otp()

    # Store OTP in Redis for 10 minutes
    redis_client.setex(
        f"verify:{user.email}",
        600,
        otp
    )

    # Send OTP email
    send_verification_email(
        user.email,
        otp
    )

    return {
        "message": "Registration successful. Please verify your email."
    }

@router.post(
    "/login",
    response_model=Token
)
def login(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        payload.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )


    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Verify your email first"
        )

    return Token(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email)
    )




@router.post("/verify-email")
def verify_email(
    payload: VerifyOTP,
    db: Session = Depends(get_db)
):
    stored_otp = redis_client.get(
        f"verify:{payload.email}"
    )

    if stored_otp != payload.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    user.is_verified = True

    db.commit()

    redis_client.delete(
        f"verify:{payload.email}"
    )

    return {
        "message": "Email verified successfully"
    }





@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if not user:
        return {
            "message": (
                "If the email exists, an OTP has been sent."
            )
        }

    otp = generate_otp()

    redis_client.setex(
        f"reset:{user.email}",
        600,
        otp
    )

    send_password_reset_email(
        user.email,
        otp
    )

    return {
        "message": (
            "If the email exists, an OTP has been sent."
        )
    }


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    stored_otp = redis_client.get(
        f"reset:{payload.email}"
    )

    if stored_otp != payload.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.hashed_password = hash_password(
        payload.new_password
    )

    db.commit()

    redis_client.delete(
        f"reset:{payload.email}"
    )

    return {
        "message": "Password reset successful"
    }


@router.post(
    "/refresh",
    response_model=Token
)
def refresh_token(
    payload: RefreshTokenRequest
):
    token_data = decode_token(
        payload.refresh_token
    )

    if token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    email = token_data["sub"]

    return Token(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email)
    )


@router.post(
    "/refresh",
    response_model=Token
)
def refresh_token(
    payload: RefreshTokenRequest
):
    token_data = decode_token(
        payload.refresh_token
    )

    if token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    email = token_data["sub"]

    return Token(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email)
    )


@router.post("/logout")
def logout(
    payload: RefreshTokenRequest
):
    token_data = decode_token(
        payload.refresh_token
    )

    exp = token_data["exp"]

    ttl = exp - int(time.time())

    redis_client.setex(
        f"blacklist:{payload.refresh_token}",
        ttl,
        "revoked"
    )

    return {
        "message": "Logged out successfully"
    }