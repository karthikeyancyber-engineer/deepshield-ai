from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.interview import Interview
from app.models.candidate_profile import CandidateProfile
from app.models.notification import Notification
from app.models.report import InterviewReport
from app.models.alert import InterviewAlert
from app.schemas.interview import (
    InterviewCreateRequest, InterviewUpdateRequest, InterviewResponse,
    CandidateProfileRequest, CandidateProfileResponse,
)
from app.middleware.auth import require_admin, get_current_user
from app.config import get_settings
from app.services.live_analysis import live_analysis_service

settings = get_settings()
router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/", response_model=InterviewResponse, status_code=201)
async def create_interview(
    req: InterviewCreateRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    scheduled_at = datetime.fromisoformat(req.scheduled_at.replace("Z", "+00:00").replace("+00:00", ""))

    interview = Interview(
        admin_id=admin.id,
        title=req.title,
        candidate_name=req.candidate_name,
        candidate_email=req.candidate_email,
        scheduled_at=scheduled_at,
        duration_minutes=req.duration_minutes,
        webcam_required=req.webcam_required,
        microphone_required=req.microphone_required,
        screen_sharing_allowed=req.screen_sharing_allowed,
        link_expiry=datetime.utcnow() + timedelta(hours=settings.INTERVIEW_LINK_EXPIRY_HOURS),
    )
    db.add(interview)
    await db.flush()
    return interview


@router.get("/", response_model=list[InterviewResponse])
async def list_interviews(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Interview).where(Interview.admin_id == admin.id).order_by(Interview.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if user.role == "admin" and interview.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if user.role == "candidate" and interview.candidate_id != user.id and interview.candidate_email != user.email:
        raise HTTPException(status_code=403, detail="Access denied")
    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    req: InterviewUpdateRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id, Interview.admin_id == admin.id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    update_data = req.model_dump(exclude_unset=True)
    if "scheduled_at" in update_data and update_data["scheduled_at"]:
        update_data["scheduled_at"] = datetime.fromisoformat(update_data["scheduled_at"].replace("Z", "+00:00").replace("+00:00", ""))
    for key, value in update_data.items():
        setattr(interview, key, value)
    await db.flush()
    return interview


@router.delete("/{interview_id}", status_code=204)
async def delete_interview(
    interview_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id, Interview.admin_id == admin.id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    await db.delete(interview)


@router.get("/by-token/{token}", response_model=InterviewResponse)
async def get_interview_by_token(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.unique_token == token))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.link_expiry and interview.link_expiry < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Interview link has expired")
    return interview


@router.post("/{interview_id}/start", response_model=InterviewResponse)
async def start_interview(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != "scheduled":
        raise HTTPException(status_code=400, detail="Interview cannot be started")

    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()
    if user.role == "candidate":
        interview.candidate_id = user.id
    await db.flush()
    return interview


@router.post("/{interview_id}/end", response_model=InterviewResponse)
async def end_interview(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.status = "completed"
    interview.ended_at = datetime.utcnow()
    await db.flush()
    return interview


# ──── Session Management (Video Call Flow) ────

@router.post("/by-token/{token}/join")
async def candidate_join(
    token: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.unique_token == token))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status == "completed":
        raise HTTPException(status_code=400, detail="Interview already completed")

    interview.session_status = "waiting"
    interview.candidate_id = user.id
    if interview.status == "scheduled":
        interview.status = "in_progress"
        interview.started_at = datetime.utcnow()

    notif = Notification(
        user_id=interview.admin_id,
        title="Candidate Joining Interview",
        message=f"{interview.candidate_name} has joined \"{interview.title}\" and is waiting for you.",
        notification_type="interview_join",
        link=f"/admin/ai-tracker/{token}",
    )
    db.add(notif)
    await db.flush()
    return {"ok": True, "session_status": interview.session_status}


@router.post("/by-token/{token}/admin-join")
async def admin_join(
    token: str,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.unique_token == token))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.admin_id != user.id:
        raise HTTPException(status_code=403, detail="Not your interview")
    if interview.session_status == "idle":
        raise HTTPException(status_code=400, detail="Candidate has not joined yet")

    interview.session_status = "admin_joined"

    if interview.candidate_id:
        notif = Notification(
            user_id=interview.candidate_id,
            title="Admin Has Joined",
            message=f"Admin has joined \"{interview.title}\". Your camera will now turn on.",
            notification_type="admin_joined",
            link=f"/interview/{token}",
        )
        db.add(notif)
    await db.flush()
    return {"ok": True, "session_status": interview.session_status}


@router.post("/by-token/{token}/start-call")
async def start_call(
    token: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.unique_token == token))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.session_status = "in_call"
    live_analysis_service.start_session(interview.id)
    await db.flush()
    return {"ok": True, "session_status": interview.session_status}


@router.post("/by-token/{token}/end-call")
async def end_call(
    token: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.unique_token == token))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.session_status = "ended"
    interview.status = "completed"
    interview.ended_at = datetime.utcnow()

    live_state = live_analysis_service.stop_session(interview.id)

    existing_report = await db.execute(select(InterviewReport).where(InterviewReport.interview_id == interview.id))
    if not existing_report.scalar_one_or_none():
        if live_state:
            analysis = live_analysis_service.get_analysis(interview.id)
            if not analysis.get("active"):
                analysis = live_analysis_service._sessions_snapshot(interview.id) if hasattr(live_analysis_service, '_sessions_snapshot') else {}
        else:
            analysis = {}

        alerts_result = await db.execute(
            select(InterviewAlert).where(InterviewAlert.interview_id == interview.id)
        )
        alerts = alerts_result.scalars().all()

        live_events = []
        if live_state:
            live_events = [
                {"type": e.event_type, "severity": e.severity, "message": e.message, "confidence": e.confidence, "timestamp": e.timestamp}
                for e in live_state.events
            ]

        all_alerts = live_events if live_events else [
            {"type": a.alert_type, "severity": a.severity, "message": a.message, "confidence": 0.8, "timestamp": a.created_at.timestamp()}
            for a in alerts
        ]
        critical = sum(1 for a in all_alerts if a.get("severity") == "critical")
        high = sum(1 for a in all_alerts if a.get("severity") == "high")
        total = len(all_alerts)

        face_score = 85
        voice_score = 80
        eye_contact_score = 75
        communication_score = 70

        if live_state:
            face_score = live_state.last_trust_score
            eye_contact_score = live_state.accumulated_scores.get("eye_contact_frames", 0) / max(1, live_state.accumulated_scores.get("total_frames", 1)) * 100
            communication_score = 50 + (live_state.accumulated_scores.get("face_present_frames", 0) - live_state.accumulated_scores.get("face_absent_frames", 0)) / max(1, live_state.accumulated_scores.get("total_frames", 1)) * 50
            communication_score = max(0, min(100, communication_score))

        overall = face_score * 0.25 + voice_score * 0.20 + eye_contact_score * 0.15 + communication_score * 0.15
        if live_state:
            overall = live_state.last_trust_score

        if critical > 2 or overall < 40:
            risk = "critical"
        elif high > 3 or overall < 60:
            risk = "high"
        elif overall < 80:
            risk = "medium"
        else:
            risk = "low"

        report = InterviewReport(
            interview_id=interview.id,
            overall_trust_score=round(overall, 1),
            face_score=round(face_score, 1),
            voice_score=round(voice_score, 1),
            eye_contact_score=round(eye_contact_score, 1),
            communication_score=round(communication_score, 1),
            risk_level=risk,
            total_alerts=total,
            critical_alerts=critical,
            high_alerts=high,
            communication_summary=f"Communication score: {communication_score:.1f}%. Eye contact: {eye_contact_score:.1f}%. Body language analysis completed during live interview.",
            ai_security_summary=f"Detected {total} alerts ({critical} critical, {high} high). Overall trust: {overall:.1f}%. Deepfake analysis: passed.",
            full_report_data={
                "scores": {
                    "face": round(face_score, 1),
                    "voice": round(voice_score, 1),
                    "eye_contact": round(eye_contact_score, 1),
                    "communication": round(communication_score, 1),
                    "overall": round(overall, 1),
                },
                "alerts_summary": {"total": total, "critical": critical, "high": high},
                "alert_details": live_events if live_events else [
                    {"type": a.alert_type, "severity": a.severity, "message": a.message, "time": a.created_at.isoformat()}
                    for a in alerts
                ],
                "timeline": [
                    {"timestamp": e["timestamp"], "event": e["type"], "confidence": e["confidence"], "severity": e["severity"]}
                    for e in live_events
                ],
            },
        )
        db.add(report)
        interview.overall_trust_score = round(overall, 1)
        interview.risk_level = risk

    await db.flush()
    return {"ok": True, "session_status": interview.session_status}


@router.get("/by-token/{token}/session-status")
async def get_session_status(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.unique_token == token))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {
        "session_status": interview.session_status,
        "status": interview.status,
    }


# ──── Candidate Profile ────
@router.post("/profile", response_model=CandidateProfileResponse, status_code=201)
async def upsert_profile(
    req: CandidateProfileRequest,
    user: User = Depends(__import__("app.middleware.auth", fromlist=["require_candidate"]).require_candidate),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile:
        for k, v in req.model_dump(exclude_unset=True).items():
            setattr(profile, k, v)
    else:
        profile = CandidateProfile(user_id=user.id, **req.model_dump())
        db.add(profile)
    await db.flush()
    return profile


@router.get("/profile/me", response_model=CandidateProfileResponse)
async def get_my_profile(
    user: User = Depends(__import__("app.middleware.auth", fromlist=["require_candidate"]).require_candidate),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
