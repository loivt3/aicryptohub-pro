"""
Authentication Endpoints
Database-backed login with password verification
"""

from datetime import datetime
from typing import Optional
import hashlib

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.services.database import get_database_service

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
    """Login with email and password - verified from database"""
    db = get_database_service()
    
    try:
        with db.engine.connect() as conn:
            # Get user from database
            result = conn.execute(
                text("""
                    SELECT id, email, password_hash, name, role, is_active 
                    FROM admin_users 
                    WHERE email = :email
                """),
                {"email": request.email}
            )
            row = result.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            user_id, email, password_hash, name, role, is_active = row
            
            # Check if user is active
            if not is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is banned"
                )
            
            # Verify password (SHA256 hash)
            input_hash = hashlib.sha256(request.password.encode()).hexdigest()
            if input_hash != password_hash:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Update last login
            conn.execute(
                text("UPDATE admin_users SET last_login = NOW(), login_count = login_count + 1 WHERE id = :id"),
                {"id": user_id}
            )
            conn.commit()
            
            # Create access token
            access_token = create_access_token(
                data={"sub": str(user_id), "email": email, "role": role}
            )
            
            return TokenResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "role": role,
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user"""
    db = get_database_service()
    
    try:
        with db.engine.connect() as conn:
            # Check if email exists
            result = conn.execute(
                text("SELECT id FROM admin_users WHERE email = :email"),
                {"email": request.email}
            )
            if result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password
            password_hash = hashlib.sha256(request.password.encode()).hexdigest()
            
            # Insert user
            result = conn.execute(
                text("""
                    INSERT INTO admin_users (email, password_hash, name, role)
                    VALUES (:email, :password_hash, :name, 'user')
                    RETURNING id
                """),
                {
                    "email": request.email,
                    "password_hash": password_hash,
                    "name": request.name or request.email.split("@")[0],
                }
            )
            conn.commit()
            user_id = result.fetchone()[0]
            
            # Create access token
            access_token = create_access_token(
                data={"sub": str(user_id), "email": request.email, "role": "user"}
            )
            
            return TokenResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": user_id,
                    "email": request.email,
                    "name": request.name,
                    "role": "user",
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
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
