"""
Authentication endpoints — login, logout, me, forgot-password.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth.service import verify_password, create_access_token, get_current_user
from app.config.auth_config import ACCESS_TOKEN_EXPIRE_MINUTES, REMEMBER_ME_EXPIRE_DAYS
from app.init_db import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username:    str           # accepts email OR user_name
    password:    str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         dict


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(
            or_(
                User.email     == payload.username,
                User.user_name == payload.username,
            )
        )
    ).scalars().first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.active_status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Contact an administrator.",
        )

    expire = (
        timedelta(days=REMEMBER_ME_EXPIRE_DAYS)
        if payload.remember_me
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    token = create_access_token({"sub": str(user.id)}, expires_delta=expire)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":        user.id,
            "user_name": user.user_name,
            "email":     user.email,
            "role":      user.role,
            "team":      user.team,
        },
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id":        current_user.id,
        "user_name": current_user.user_name,
        "email":     current_user.email,
        "role":      current_user.role,
        "team":      current_user.team,
    }


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Always return success to prevent email enumeration
    # In production: generate a reset token and send an email
    db.execute(select(User).where(User.email == payload.email))  # no-op, validates DB
    return {
        "message": "If that email is registered, a password reset link has been sent."
    }


@router.post("/logout")
def logout():
    # JWT is stateless — the client clears the token.
    # In production: maintain a token denylist / redis store.
    return {"message": "Logged out successfully"}
