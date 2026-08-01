import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.otp import OTP
from app.config import get_settings

settings = get_settings()


def generate_otp() -> str:
    """Generate a secure 6-digit OTP."""
    return f"{secrets.randbelow(900000) + 100000}"


def hash_otp(otp: str) -> str:
    """Hash OTP using SHA-256 for secure storage."""
    return hashlib.sha256(otp.encode()).hexdigest()


def get_otp_expiry() -> datetime:
    """Get OTP expiry datetime."""
    return datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)


async def create_otp(db: AsyncSession, email: str, purpose: str) -> dict:
    """
    Create a new OTP. Handles rate limiting and cooldown.
    Returns dict with otp code, cooldown info, and any errors.
    """
    # Check rate limit: max requests per hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(OTP).where(
            OTP.email == email,
            OTP.purpose == purpose,
            OTP.created_at >= one_hour_ago,
        )
    )
    recent_otps = result.scalars().all()
    if len(recent_otps) >= settings.OTP_MAX_REQUESTS_PER_HOUR:
        return {"error": "Too many OTP requests. Please try again later.", "cooldown_seconds": 3600}

    # Check cooldown (60 seconds between requests)
    result = await db.execute(
        select(OTP).where(
            OTP.email == email,
            OTP.purpose == purpose,
        ).order_by(OTP.created_at.desc()).limit(1)
    )
    last_otp = result.scalar_one_or_none()
    if last_otp:
        elapsed = (datetime.utcnow() - last_otp.last_request_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            remaining = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            return {"error": f"Please wait {remaining} seconds before requesting a new OTP.", "cooldown_seconds": remaining}

    # Invalidate any existing unverified OTPs for this email+purpose
    await db.execute(
        delete(OTP).where(
            OTP.email == email,
            OTP.purpose == purpose,
            OTP.verified == False,
        )
    )

    # Create new OTP
    plain_otp = generate_otp()
    otp_record = OTP(
        email=email,
        otp_hash=hash_otp(plain_otp),
        purpose=purpose,
        expires_at=get_otp_expiry(),
        attempts=0,
        max_attempts=settings.OTP_MAX_ATTEMPTS,
        verified=False,
        request_count=(len(recent_otps) + 1),
        last_request_at=datetime.utcnow(),
    )
    db.add(otp_record)
    await db.flush()

    return {"otp": plain_otp, "cooldown_seconds": settings.OTP_RESEND_COOLDOWN_SECONDS}


async def verify_otp(db: AsyncSession, email: str, otp_code: str, purpose: str) -> dict:
    """
    Verify an OTP code. Returns dict with verification result.
    """
    # Find the latest unverified OTP for this email+purpose
    result = await db.execute(
        select(OTP).where(
            OTP.email == email,
            OTP.purpose == purpose,
            OTP.verified == False,
        ).order_by(OTP.created_at.desc()).limit(1)
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        return {"verified": False, "error": "No OTP found. Please request a new one.", "remaining_attempts": 0}

    # Check expiry
    if datetime.utcnow() > otp_record.expires_at:
        return {"verified": False, "error": "OTP has expired. Please request a new one.", "remaining_attempts": 0}

    # Check max attempts
    if otp_record.attempts >= otp_record.max_attempts:
        return {"verified": False, "error": "Maximum verification attempts exceeded. Please request a new OTP.", "remaining_attempts": 0}

    # Increment attempts
    otp_record.attempts += 1
    remaining = otp_record.max_attempts - otp_record.attempts

    # Verify hash
    if hash_otp(otp_code) != otp_record.otp_hash:
        return {"verified": False, "error": f"Invalid OTP. {remaining} attempts remaining.", "remaining_attempts": remaining}

    # Mark as verified
    otp_record.verified = True
    await db.flush()

    return {"verified": True, "remaining_attempts": remaining}


async def is_email_verified(db: AsyncSession, email: str, purpose: str) -> bool:
    """Check if an email has been verified for a given purpose."""
    result = await db.execute(
        select(OTP).where(
            OTP.email == email,
            OTP.purpose == purpose,
            OTP.verified == True,
        ).order_by(OTP.created_at.desc()).limit(1)
    )
    otp_record = result.scalar_one_or_none()
    if not otp_record:
        return False
    # Check if verification is still valid (within expiry window)
    if datetime.utcnow() > otp_record.expires_at:
        return False
    return True


async def cleanup_expired_otps(db: AsyncSession):
    """Delete expired OTP records."""
    await db.execute(
        delete(OTP).where(OTP.expires_at < datetime.utcnow())
    )
    await db.flush()
