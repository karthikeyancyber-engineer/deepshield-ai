from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.interview import Interview
from app.models.report import InterviewReport
from app.models.alert import InterviewAlert
from app.models.meeting_log import MeetingLog
from app.schemas.interview import (
    AlertCreateRequest, AlertResponse, ReportResponse,
    ReportGenerateRequest, MeetingLogResponse,
)
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/live", tags=["Live Interview"])


@router.post("/alert", response_model=AlertResponse, status_code=201)
async def create_alert(
    interview_id: str,
    req: AlertCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    alert = InterviewAlert(
        interview_id=interview_id,
        alert_type=req.alert_type,
        severity=req.severity,
        message=req.message,
        confidence=req.confidence,
        extra_data=req.extra_data,
    )
    db.add(alert)
    await db.flush()
    return alert


@router.get("/alerts/{interview_id}", response_model=list[AlertResponse])
async def get_alerts(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewAlert)
        .where(InterviewAlert.interview_id == interview_id)
        .order_by(InterviewAlert.created_at.desc())
    )
    return result.scalars().all()


@router.post("/log", response_model=MeetingLogResponse, status_code=201)
async def create_log(
    interview_id: str,
    event_type: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    data: dict = None,
):
    log = MeetingLog(interview_id=interview_id, event_type=event_type, data=data)
    db.add(log)
    await db.flush()
    return log


@router.get("/logs/{interview_id}", response_model=list[MeetingLogResponse])
async def get_logs(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MeetingLog)
        .where(MeetingLog.interview_id == interview_id)
        .order_by(MeetingLog.timestamp.asc())
    )
    return result.scalars().all()


@router.post("/report/{interview_id}", response_model=ReportResponse, status_code=201)
async def generate_report(
    interview_id: str,
    req: ReportGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    existing = await db.execute(select(InterviewReport).where(InterviewReport.interview_id == interview_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Report already exists for this interview")

    alerts_result = await db.execute(
        select(InterviewAlert).where(InterviewAlert.interview_id == interview_id)
    )
    alerts = alerts_result.scalars().all()

    critical = sum(1 for a in alerts if a.severity == "critical")
    high = sum(1 for a in alerts if a.severity == "high")
    total = len(alerts)

    weights = {"face": 0.25, "voice": 0.20, "eye_contact": 0.15, "behavior": 0.15}
    overall = (
        req.face_score * weights["face"]
        + req.voice_score * weights["voice"]
        + req.eye_contact_score * weights["eye_contact"]
        + req.communication_score * weights["behavior"]
    )

    if critical > 2 or overall < 40:
        risk = "critical"
    elif high > 3 or overall < 60:
        risk = "high"
    elif overall < 80:
        risk = "medium"
    else:
        risk = "low"

    report = InterviewReport(
        interview_id=interview_id,
        overall_trust_score=round(overall, 1),
        face_score=req.face_score,
        voice_score=req.voice_score,
        eye_contact_score=req.eye_contact_score,
        communication_score=req.communication_score,
        risk_level=risk,
        total_alerts=total,
        critical_alerts=critical,
        high_alerts=high,
        communication_summary=req.communication_summary or f"Communication score: {req.communication_score}%",
        ai_security_summary=f"Detected {total} alerts ({critical} critical, {high} high). Overall trust: {overall:.1f}%.",
        full_report_data={
            "scores": {
                "face": req.face_score,
                "voice": req.voice_score,
                "eye_contact": req.eye_contact_score,
                "communication": req.communication_score,
                "overall": round(overall, 1),
            },
            "alerts_summary": {"total": total, "critical": critical, "high": high},
            "alert_details": [
                {"type": a.alert_type, "severity": a.severity, "message": a.message, "time": a.created_at.isoformat()}
                for a in alerts
            ],
        },
    )
    db.add(report)

    interview.overall_trust_score = round(overall, 1)
    interview.risk_level = risk
    interview.status = "completed"
    interview.ended_at = interview.started_at

    await db.flush()
    return report


@router.get("/report/{interview_id}", response_model=ReportResponse)
async def get_report(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(InterviewReport).where(InterviewReport.interview_id == interview_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
