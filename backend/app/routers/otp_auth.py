import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.otp import OTP
from app.schemas.interview import (
    SendOTPRequest, VerifyOTPRequest, ResetPasswordRequest, RegisterRequest,
    OTPResponse, VerifyOTPResponse, TokenResponse,
)
from app.services.otp_service import create_otp, verify_otp, is_email_verified
from app.services.email_service import send_otp_email
from app.middleware.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["OTP Auth"])


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(req: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """Send OTP to email for registration or password reset."""
    # For registration: check email not already taken
    if req.purpose == "registration":
        existing = await db.execute(select(User).where(User.email == req.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

    # For password reset: check email exists
    if req.purpose == "password_reset":
        result = await db.execute(select(User).where(User.email == req.email))
        if not result.scalar_one_or_none():
            # Return success to prevent email enumeration
            return OTPResponse(message="If an account exists with this email, an OTP has been sent.", cooldown_seconds=60)

    # Create OTP (handles rate limiting)
    otp_result = await create_otp(db, req.email, req.purpose)

    if "error" in otp_result:
        raise HTTPException(status_code=429, detail=otp_result["error"])

    # Send email (run in thread to avoid blocking)
    email_result = await asyncio.to_thread(send_otp_email, req.email, otp_result["otp"], req.purpose)
    if not email_result["success"]:
        # Dev mode: return OTP in response so user can test without email
        return OTPResponse(
            message=f"Email failed ({email_result['error']}). Dev mode OTP: {otp_result['otp']}",
            cooldown_seconds=otp_result["cooldown_seconds"],
        )

    return OTPResponse(
        message="OTP sent successfully to your email",
        cooldown_seconds=otp_result["cooldown_seconds"],
    )


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp_code(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify OTP code for registration or password reset."""
    result = await verify_otp(db, req.email, req.otp, req.purpose)

    if not result["verified"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return VerifyOTPResponse(
        message="OTP verified successfully",
        verified=True,
        remaining_attempts=result["remaining_attempts"],
    )


@router.post("/register-with-otp", response_model=TokenResponse, status_code=201)
async def register_with_otp(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register user after OTP verification."""
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check email verified
    if not await is_email_verified(db, req.email, "registration"):
        raise HTTPException(status_code=400, detail="Email not verified. Please verify your OTP first.")

    # Check not already registered
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


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password after OTP verification."""
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check email verified
    if not await is_email_verified(db, req.email, "password_reset"):
        raise HTTPException(status_code=400, detail="Email not verified. Please verify your OTP first.")

    # Find user
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password
    user.hashed_password = hash_password(req.password)
    await db.flush()

    return {"message": "Password reset successfully. You can now log in."}
