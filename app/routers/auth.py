from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from datetime import datetime
from app.models.schemas import UserRegisterRequest, UserLoginRequest, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.config.jwt_config import create_access_token, create_refresh_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.config.security import hash_password, verify_password
from app.models.schemas import UserResponse, TokenResponse, MessageResponse, AuthResponse
from app.models.User import User
from app.services.mail_service import send_mail, generate_otp, generate_otp_expiry_time
from app.models.password_reset_token import PasswordResetToken
from app.db.mysql_connection import get_session


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=MessageResponse)
def register(data : UserRegisterRequest, session : Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = User(
        email = data.email,
        username = data.username,
        hashed_password = hash_password(data.password)
    )

    session.add(user)
    session.commit()

    return MessageResponse(
        message="User registered successfully",
        success=True
    )

@router.post("/login", response_model=AuthResponse)
def login(data : UserLoginRequest, session : Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, existing.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(existing.id)
    refresh_token = create_refresh_token(existing.id)

    return AuthResponse(
        user=UserResponse(
            id=existing.id,
            email=existing.email,
            username=existing.username,
            is_active=existing.is_active,
            created_at=existing.created_at
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(data : RefreshTokenRequest, session : Session = Depends(get_session)):
    try:
        payload = decode_token(data.refresh_token)
    except Exception as e:
        print(f"❌ Token decode error: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

    user = session.exec(select(User).where(User.id == payload["sub"])).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data : ForgotPasswordRequest, session : Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    email = user.email

    otp = str(generate_otp())

    expires_at = generate_otp_expiry_time()

    token = PasswordResetToken(
        user_id = user.id,
        otp = otp,
        expires_at = expires_at
    )

    session.add(token)
    session.commit()

    await send_mail(email, otp)

    return MessageResponse(
        message="OTP sent successfully",
        success=True
    )

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data : ResetPasswordRequest, session : Session = Depends(get_session)):
    token = session.exec(select(PasswordResetToken).where(PasswordResetToken.otp == data.otp)).first()

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if token.is_used:
        raise HTTPException(
            status_code=400,
            detail="OTP already used"
        )

    if token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    user = session.exec(select(User).where(User.id == token.user_id)).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.hashed_password = hash_password(data.new_password)
    token.is_used = True

    session.add(user)
    session.add(token)
    session.commit()

    return MessageResponse(
        message="Password reset successfully",
        success=True
    )
# def logout():


