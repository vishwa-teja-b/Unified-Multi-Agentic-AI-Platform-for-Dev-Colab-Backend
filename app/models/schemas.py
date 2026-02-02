from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ==================== Request Schemas ====================

class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    otp: str
    new_password: str = Field(..., min_length=8, max_length=100)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== Response Schemas ====================

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
