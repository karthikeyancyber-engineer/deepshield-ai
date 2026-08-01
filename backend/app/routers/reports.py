from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.interview import Interview
from app.models.report import InterviewReport
from app.models.alert import InterviewAlert
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.pdf_generator import InterviewPDFGenerator
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])
_pdf = InterviewPDFGenerator()


@router.get("/list")
async def list_reports(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role == "admin":
        result = await db.execute(
            select(InterviewReport)
            .join(Interview, InterviewReport.interview_id == Interview.id)
            .where(Interview.admin_id == user.id)
            .order_by(InterviewReport.created_at.desc())
        )
    else:
        result = await db.execute(
            select(InterviewReport)
            .join(Interview, InterviewReport.interview_id == Interview.id)
            .where(Interview.candidate_id == user.id)
            .order_by(InterviewReport.created_at.desc())
        )
    reports = result.scalars().all()
    output = []
    for r in reports:
        interview_r = await db.execute(select(Interview).where(Interview.id == r.interview_id))
        interview = interview_r.scalar_one_or_none()
        output.append({
            "id": r.id,
            "interview_id": r.interview_id,
            "interview_title": interview.title if interview else "N/A",
            "candidate_name": interview.candidate_name if interview else "N/A",
            "overall_trust_score": r.overall_trust_score,
            "risk_level": r.risk_level,
            "total_alerts": r.total_alerts,
            "created_at": r.created_at.isoformat(),
        })
    return output


@router.get("/pdf/{interview_id}")
async def download_pdf(
    interview_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    interview_r = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = interview_r.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    report_r = await db.execute(select(InterviewReport).where(InterviewReport.interview_id == interview_id))
    report = report_r.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    alerts_r = await db.execute(
        select(InterviewAlert).where(InterviewAlert.interview_id == interview_id).order_by(InterviewAlert.created_at)
    )
    alerts = alerts_r.scalars().all()

    pdf_data = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "interview": {
            "title": interview.title,
            "candidate_name": interview.candidate_name,
            "candidate_email": interview.candidate_email,
            "scheduled_at": interview.scheduled_at.strftime("%Y-%m-%d %H:%M") if interview.scheduled_at else "N/A",
            "duration_minutes": interview.duration_minutes,
            "status": interview.status,
        },
        "scores": {
            "face": report.face_score,
            "voice": report.voice_score,
            "eye_contact": report.eye_contact_score,
            "communication": report.communication_score,
            "overall": report.overall_trust_score,
        },
        "alerts": [
            {
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "time": a.created_at.strftime("%H:%M:%S") if a.created_at else "",
            }
            for a in alerts
        ],
        "recommendations": [
            f"Risk Level: {report.risk_level.upper()}",
            f"Total Alerts: {report.total_alerts} ({report.critical_alerts} critical, {report.high_alerts} high)",
            report.ai_security_summary or "",
        ],
        "ai_summary": report.ai_security_summary or "No AI summary available.",
    }

    pdf_bytes = _pdf.generate(pdf_data)
    filename = f"interview_report_{interview.candidate_name.replace(' ', '_')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
