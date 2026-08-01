import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id"), unique=True, index=True)

    overall_trust_score: Mapped[float] = mapped_column(Float, default=0)
    face_score: Mapped[float] = mapped_column(Float, default=0)
    voice_score: Mapped[float] = mapped_column(Float, default=0)
    eye_contact_score: Mapped[float] = mapped_column(Float, default=0)
    communication_score: Mapped[float] = mapped_column(Float, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")

    total_alerts: Mapped[int] = mapped_column(default=0)
    critical_alerts: Mapped[int] = mapped_column(default=0)
    high_alerts: Mapped[int] = mapped_column(default=0)

    communication_summary: Mapped[str] = mapped_column(Text, nullable=True)
    ai_security_summary: Mapped[str] = mapped_column(Text, nullable=True)
    full_report_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
