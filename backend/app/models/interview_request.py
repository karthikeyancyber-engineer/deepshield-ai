import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class InterviewRequest(Base):
    __tablename__ = "interview_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_email: Mapped[str] = mapped_column(String(255), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_date: Mapped[str] = mapped_column(String(20), nullable=True, default="")
    preferred_time: Mapped[str] = mapped_column(String(20), nullable=True, default="")
    duration_minutes: Mapped[int] = mapped_column(default=30)
    notes: Mapped[str] = mapped_column(Text, default="")
    resume_path: Mapped[str] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_by: Mapped[str] = mapped_column(String(36), nullable=True)
    review_note: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
