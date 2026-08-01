from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.interview import Interview
from app.models.report import InterviewReport
from app.models.alert import InterviewAlert
from app.middleware.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/users")
async def list_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get("/dashboard")
async def admin_dashboard(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total_interviews = await db.execute(
        select(func.count(Interview.id)).where(Interview.admin_id == admin.id)
    )
    total_reports = await db.execute(
        select(func.count(InterviewReport.id))
        .join(Interview, InterviewReport.interview_id == Interview.id)
        .where(Interview.admin_id == admin.id)
    )
    scheduled = await db.execute(
        select(func.count(Interview.id)).where(Interview.admin_id == admin.id, Interview.status == "scheduled")
    )
    in_progress = await db.execute(
        select(func.count(Interview.id)).where(Interview.admin_id == admin.id, Interview.status == "in_progress")
    )
    completed = await db.execute(
        select(func.count(Interview.id)).where(Interview.admin_id == admin.id, Interview.status == "completed")
    )

    recent_interviews = await db.execute(
        select(Interview).where(Interview.admin_id == admin.id).order_by(Interview.created_at.desc()).limit(5)
    )

    avg_trust = await db.execute(
        select(func.avg(InterviewReport.overall_trust_score))
        .join(Interview, InterviewReport.interview_id == Interview.id)
        .where(Interview.admin_id == admin.id)
    )

    total_alerts = await db.execute(
        select(func.count(InterviewAlert.id))
        .join(Interview, InterviewAlert.interview_id == Interview.id)
        .where(Interview.admin_id == admin.id)
    )

    total_users = await db.execute(select(func.count(User.id)))

    return {
        "total_users": total_users.scalar() or 0,
        "total_interviews": total_interviews.scalar() or 0,
        "total_reports": total_reports.scalar() or 0,
        "scheduled": scheduled.scalar() or 0,
        "in_progress": in_progress.scalar() or 0,
        "completed": completed.scalar() or 0,
        "avg_trust_score": round(avg_trust.scalar() or 0, 1),
        "total_alerts": total_alerts.scalar() or 0,
        "recent_interviews": [
            {
                "id": i.id,
                "title": i.title,
                "candidate_name": i.candidate_name,
                "status": i.status,
                "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
                "overall_trust_score": i.overall_trust_score,
            }
            for i in (recent_interviews.scalars().all())
        ],
    }
