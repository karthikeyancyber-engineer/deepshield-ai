from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# ──── OTP ────
class SendOTPRequest(BaseModel):
    email: str = Field(..., min_length=5)
    purpose: str = Field(..., pattern="^(registration|password_reset)$")


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str = Field(..., min_length=6, max_length=6)
    purpose: str = Field(..., pattern="^(registration|password_reset)$")


class OTPResponse(BaseModel):
    message: str
    cooldown_seconds: int = 60


class VerifyOTPResponse(BaseModel):
    message: str
    verified: bool
    remaining_attempts: int


# ──── Auth ────
class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None
    company: Optional[str] = None
    role: str = Field("candidate", pattern="^(admin|candidate)$")


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    full_name: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone_number: Optional[str] = None
    company: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ──── Candidate Profile ────
class CandidateProfileRequest(BaseModel):
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    skills: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None


class CandidateProfileResponse(BaseModel):
    id: str
    user_id: str
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    skills: Optional[str] = None
    resume_path: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──── Interview ────
class InterviewCreateRequest(BaseModel):
    candidate_name: str = Field(..., min_length=1)
    candidate_email: str
    title: str = Field(..., min_length=1)
    scheduled_at: str
    duration_minutes: int = Field(30, ge=5, le=180)
    webcam_required: bool = True
    microphone_required: bool = True
    screen_sharing_allowed: bool = False


class InterviewUpdateRequest(BaseModel):
    title: Optional[str] = None
    scheduled_at: Optional[str] = None
    duration_minutes: Optional[int] = None
    webcam_required: Optional[bool] = None
    microphone_required: Optional[bool] = None
    screen_sharing_allowed: Optional[bool] = None


class InterviewResponse(BaseModel):
    id: str
    admin_id: str
    candidate_id: Optional[str] = None
    title: str
    candidate_name: str
    candidate_email: str
    unique_token: str
    scheduled_at: datetime
    duration_minutes: int
    webcam_required: bool
    microphone_required: bool
    screen_sharing_allowed: bool
    status: str
    session_status: str = "idle"
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    overall_trust_score: Optional[float] = None
    risk_level: Optional[str] = None
    link_expiry: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──── Alert ────
class AlertResponse(BaseModel):
    id: str
    interview_id: str
    alert_type: str
    severity: str
    message: str
    confidence: float
    extra_data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreateRequest(BaseModel):
    alert_type: str
    severity: str = "low"
    message: str
    confidence: float = 0.0
    extra_data: Optional[dict] = None


# ──── Report ────
class ReportResponse(BaseModel):
    id: str
    interview_id: str
    overall_trust_score: float
    face_score: float
    voice_score: float
    eye_contact_score: float
    communication_score: float
    risk_level: str
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    communication_summary: Optional[str] = None
    ai_security_summary: Optional[str] = None
    full_report_data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    face_score: float = 0
    voice_score: float = 0
    eye_contact_score: float = 0
    communication_score: float = 0
    communication_summary: Optional[str] = None


# ──── Meeting Log ────
class MeetingLogResponse(BaseModel):
    id: str
    interview_id: str
    event_type: str
    timestamp: datetime
    data: Optional[dict] = None

    class Config:
        from_attributes = True


# ──── Interview Request ────
class InterviewRequestCreate(BaseModel):
    title: str = Field(..., min_length=1)
    preferred_date: str = ""
    preferred_time: str = ""
    duration_minutes: int = Field(30, ge=5, le=180)
    notes: str = ""
    resume_path: str | None = None


class InterviewRequestResponse(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    title: str
    preferred_date: str
    preferred_time: str
    duration_minutes: int
    notes: str
    resume_path: str | None = None
    status: str
    reviewed_by: str | None = None
    review_note: str = ""
    reviewed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewRequestReview(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    review_note: str = ""
    scheduled_at: str | None = None


# ──── Notification ────
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    link: str
    created_at: datetime

    class Config:
        from_attributes = True


# ──── Generic ────
class HealthResponse(BaseModel):
    status: str
    version: str
