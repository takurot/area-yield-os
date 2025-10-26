"""User models"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """User model as stored in database"""
    uid: str
    hashed_password: str
    role: str = "user"
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True


class User(UserBase):
    """User model for API responses"""
    uid: str
    role: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    uid: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

