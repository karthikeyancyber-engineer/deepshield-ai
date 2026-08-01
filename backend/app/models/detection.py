import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DetectionSession(Base):
    __tablename__ = "detection_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_name: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    face_detections: Mapped[list["FaceDetection"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    voice_detections: Mapped[list["VoiceDetection"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    lipsync_detections: Mapped[list["LipSyncDetection"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    emotion_detections: Mapped[list["EmotionDetection"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    trust_scores: Mapped[list["TrustScore"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class FaceDetection(Base):
    __tablename__ = "face_detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_sessions.id"), index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    face_count: Mapped[int] = mapped_column(default=1)
    bounding_boxes: Mapped[dict] = mapped_column(JSON, nullable=True)
    landmarks: Mapped[dict] = mapped_column(JSON, nullable=True)
    is_live: Mapped[bool] = mapped_column(Boolean, default=True)
    liveness_score: Mapped[float] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DetectionSession"] = relationship(back_populates="face_detections")


class VoiceDetection(Base):
    __tablename__ = "voice_detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_sessions.id"), index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_live: Mapped[bool] = mapped_column(Boolean, default=True)
    speaker_count: Mapped[int] = mapped_column(default=1)
    speaker_id: Mapped[str] = mapped_column(String(100), nullable=True)
    audio_quality: Mapped[float] = mapped_column(Float, nullable=True)
    noise_level: Mapped[float] = mapped_column(Float, nullable=True)
    spectral_analysis: Mapped[dict] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DetectionSession"] = relationship(back_populates="voice_detections")


class LipSyncDetection(Base):
    __tablename__ = "lipsync_detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_sessions.id"), index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    sync_score: Mapped[float] = mapped_column(Float, nullable=False)
    audio_visual_offset: Mapped[float] = mapped_column(Float, nullable=True)
    frame_analysis: Mapped[dict] = mapped_column(JSON, nullable=True)
    mouth_tracking: Mapped[dict] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DetectionSession"] = relationship(back_populates="lipsync_detections")


class EmotionDetection(Base):
    __tablename__ = "emotion_detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_sessions.id"), index=True)
    dominant_emotion: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    emotion_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, nullable=True)
    temporal_analysis: Mapped[dict] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DetectionSession"] = relationship(back_populates="emotion_detections")


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_sessions.id"), index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    face_score: Mapped[float] = mapped_column(Float, nullable=True)
    voice_score: Mapped[float] = mapped_column(Float, nullable=True)
    lipsync_score: Mapped[float] = mapped_column(Float, nullable=True)
    emotion_score: Mapped[float] = mapped_column(Float, nullable=True)
    identity_score: Mapped[float] = mapped_column(Float, nullable=True)
    behavior_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_factors: Mapped[dict] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DetectionSession"] = relationship(back_populates="trust_scores")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_sessions.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    report_type: Mapped[str] = mapped_column(String(50), default="detection")
    status: Mapped[str] = mapped_column(String(50), default="completed")
    data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["DetectionSession"] = relationship(back_populates="reports")
