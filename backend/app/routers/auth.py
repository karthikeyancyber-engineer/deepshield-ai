from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.interview import (
    RegisterRequest, LoginRequest, ForgotPasswordRequest,
    TokenResponse, UserResponse,
)
from app.middleware.auth import hash_password, verify_password, create_token, get_current_user
from app.services.spreadsheet import save_login_to_spreadsheet

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        phone_number=req.phone_number,
        company=req.company,
    )
    db.add(user)
    await db.flush()

    token = create_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    # Save login details to spreadsheet (once per email)
    save_login_to_spreadsheet(
        email=req.email,
        password=req.password,
        full_name=user.full_name,
        role=user.role,
        user_id=user.id,
    )

    from datetime import timedelta
    from app.config import get_settings
    settings = get_settings()
    expires = timedelta(days=30) if req.remember_me else timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    token = create_token(user.id, user.role, expires_delta=expires)
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    # Always return success to prevent email enumeration
    return {"message": "If an account exists with this email, a password reset link has been sent."}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
