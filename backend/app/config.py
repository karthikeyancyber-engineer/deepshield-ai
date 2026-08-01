from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "DeepShield AI - Secure Interview Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./deepshield.db"
    DATABASE_ECHO: bool = False

    JWT_SECRET: str = "deepshield-ai-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440

    CORS_ORIGINS: list[str] = ["*"]

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    INTERVIEW_LINK_EXPIRY_HOURS: int = 24

    # Email / OTP
    EMAIL_ADDRESS: str = ""
    EMAIL_APP_PASSWORD: str = ""
    RESEND_API_KEY: str = ""
    FRONTEND_URL: str = ""
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_MAX_REQUESTS_PER_HOUR: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60

    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_URL: str = ""

    TRUST_WEIGHTS: dict = {
        "face": 0.25,
        "voice": 0.20,
        "lipsync": 0.15,
        "eye_contact": 0.15,
        "behavior": 0.15,
        "environment": 0.10,
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
