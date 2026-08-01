from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ──────────────────────── Base ────────────────────────
class DetectionBase(BaseModel):
    session_id: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")


# ──────────────────────── Face ────────────────────────
class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class FaceDetectionRequest(BaseModel):
    session_id: Optional[str] = None
    image_data: str = Field(..., description="Base64 encoded image data")
    detect_liveness: bool = Field(True, description="Enable liveness detection")
    detect_landmarks: bool = Field(True, description="Enable facial landmark detection")


class FaceDetectionResponse(DetectionBase):
    id: str
    face_count: int
    bounding_boxes: Optional[dict] = None
    landmarks: Optional[dict] = None
    is_live: bool
    liveness_score: Optional[float] = None
    quality_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── Voice ────────────────────────
class VoiceDetectionRequest(BaseModel):
    session_id: Optional[str] = None
    audio_data: str = Field(..., description="Base64 encoded audio data")
    sample_rate: int = Field(16000, description="Audio sample rate in Hz")
    detect_speakers: bool = Field(True, description="Enable speaker diarization")


class VoiceDetectionResponse(DetectionBase):
    id: str
    is_live: bool
    speaker_count: int
    speaker_id: Optional[str] = None
    audio_quality: Optional[float] = None
    noise_level: Optional[float] = None
    spectral_analysis: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── LipSync ────────────────────────
class LipSyncRequest(BaseModel):
    session_id: Optional[str] = None
    video_data: str = Field(..., description="Base64 encoded video data")
    audio_data: str = Field(..., description="Base64 encoded audio data")
    frame_rate: float = Field(30.0, description="Video frame rate")
    analyze_offset: bool = Field(True, description="Analyze audio-visual offset")


class LipSyncResponse(DetectionBase):
    id: str
    sync_score: float
    audio_visual_offset: Optional[float] = None
    frame_analysis: Optional[dict] = None
    mouth_tracking: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── Emotion ────────────────────────
class EmotionRequest(BaseModel):
    session_id: Optional[str] = None
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    analyze_temporal: bool = Field(True, description="Enable temporal emotion tracking")


class EmotionResponse(DetectionBase):
    id: str
    dominant_emotion: str
    emotion_scores: dict
    consistency_score: Optional[float] = None
    temporal_analysis: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── Trust Score ────────────────────────
class TrustScoreRequest(BaseModel):
    session_id: str = Field(..., description="Detection session ID")
    include_breakdown: bool = Field(True, description="Include detailed score breakdown")


class TrustScoreResponse(BaseModel):
    id: str
    session_id: str
    overall_score: float = Field(..., ge=0, le=100)
    face_score: Optional[float] = None
    voice_score: Optional[float] = None
    lipsync_score: Optional[float] = None
    emotion_score: Optional[float] = None
    identity_score: Optional[float] = None
    behavior_score: Optional[float] = None
    risk_level: str
    risk_factors: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── Report ────────────────────────
class ReportRequest(BaseModel):
    session_id: str = Field(..., description="Detection session ID")
    title: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field("detection", description="Report type: detection, summary, incident")


class ReportResponse(BaseModel):
    id: str
    session_id: str
    title: str
    summary: Optional[str] = None
    report_type: str
    status: str
    data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── Session ────────────────────────
class SessionCreate(BaseModel):
    session_name: Optional[str] = None
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    session_name: Optional[str] = None
    user_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────── Generic ────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
