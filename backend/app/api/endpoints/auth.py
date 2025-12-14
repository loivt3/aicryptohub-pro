"""
Authentication Endpoints
Supabase Auth / JWT Custom
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login with email and password"""
    # TODO: Verify credentials from database
    # For now, mock response
    
    access_token = create_access_token(
        data={"sub": "user_123", "email": request.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": "user_123",
            "email": request.email,
        }
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user"""
    # TODO: Check if email exists, create user in database
    
    hashed_password = get_password_hash(request.password)
    
    access_token = create_access_token(
        data={"sub": "user_new", "email": request.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": "user_new",
            "email": request.email,
            "name": request.name,
        }
    )


@router.post("/refresh")
async def refresh_token():
    """Refresh access token"""
    # TODO: Implement refresh token logic
    return {"message": "Not implemented"}


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"success": True, "message": "Logged out"}
