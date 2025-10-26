"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
import structlog

from app.core.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
)
from app.core.config import settings
from app.models.user import UserCreate, UserLogin, Token, User

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    # TODO: Check if user already exists in database
    # TODO: Create user in database

    logger.info("user_registration_attempt", email=user_data.email)

    # Mock response for now
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User registration not yet implemented. Use Firebase Authentication.",
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password"""
    # TODO: Verify user credentials against database

    logger.info("user_login_attempt", email=credentials.email)

    # Mock response for now
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email/password login not yet implemented. Use Firebase Authentication.",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"uid": current_user.get("uid"), "email": current_user.get("email")},
        expires_delta=access_token_expires,
    )

    logger.info("token_refreshed", uid=current_user.get("uid"))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "uid": current_user.get("uid"),
        "email": current_user.get("email"),
        "role": current_user.get("role", "user"),
    }
