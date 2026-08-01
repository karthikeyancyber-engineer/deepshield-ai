import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_email: Mapped[str] = mapped_column(String(255), nullable=False)

    unique_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(default=30)

    webcam_required: Mapped[bool] = mapped_column(Boolean, default=True)
    microphone_required: Mapped[bool] = mapped_column(Boolean, default=True)
    screen_sharing_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    session_status: Mapped[str] = mapped_column(String(20), default="idle")
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    overall_trust_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=True)

    link_expiry: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
