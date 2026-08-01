from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import os
import uuid
from app.database import get_db
from app.models.user import User
from app.models.interview_request import InterviewRequest
from app.models.notification import Notification
from app.models.interview import Interview
from app.schemas.interview import (
    InterviewRequestCreate,
    InterviewRequestResponse,
    InterviewRequestReview,
)
from app.middleware.auth import require_admin, require_candidate, get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/interview-requests", tags=["Interview Requests"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(require_candidate),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    ext = ".pdf"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {"filename": filename, "original_name": file.filename, "path": f"/uploads/resumes/{filename}"}


@router.post("/", response_model=InterviewRequestResponse, status_code=201)
async def create_interview_request(
    req: InterviewRequestCreate,
    user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    request = InterviewRequest(
        candidate_id=user.id,
        candidate_name=user.full_name,
        candidate_email=user.email,
        title=req.title,
        preferred_date=req.preferred_date or "",
        preferred_time=req.preferred_time or "",
        duration_minutes=req.duration_minutes,
        notes=req.notes,
        resume_path=req.resume_path,
    )
    db.add(request)
    await db.flush()

    admins = await db.execute(select(User).where(User.role == "admin"))
    for admin in admins.scalars().all():
        notif = Notification(
            user_id=admin.id,
            title="New Interview Request",
            message=f"{user.full_name} requested an interview: {req.title}"
                    + (f" (Resume uploaded)" if req.resume_path else ""),
            notification_type="interview_request",
            link="/admin/interview-requests",
        )
        db.add(notif)

    await db.flush()
    return request


@router.get("/my", response_model=list[InterviewRequestResponse])
async def my_requests(
    user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewRequest)
        .where(InterviewRequest.candidate_id == user.id)
        .order_by(InterviewRequest.created_at.desc())
    )
    return result.scalars().all()


@router.get("/admin/all", response_model=list[InterviewRequestResponse])
async def all_requests(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewRequest).order_by(InterviewRequest.created_at.desc())
    )
    return result.scalars().all()


@router.get("/admin/count")
async def pending_count(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewRequest).where(InterviewRequest.status == "pending")
    )
    return {"count": len(result.scalars().all())}


@router.put("/{request_id}/review", response_model=InterviewRequestResponse)
async def review_request(
    request_id: str,
    req: InterviewRequestReview,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewRequest).where(InterviewRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = req.status
    request.reviewed_by = admin.id
    request.review_note = req.review_note
    request.reviewed_at = datetime.utcnow()

    interview_token = ""
    if req.status == "approved" and req.scheduled_at:
        interview = Interview(
            admin_id=admin.id,
            candidate_id=request.candidate_id,
            title=request.title,
            candidate_name=request.candidate_name,
            candidate_email=request.candidate_email,
            scheduled_at=datetime.fromisoformat(req.scheduled_at.replace("Z", "+00:00").replace("+00:00", "")),
            duration_minutes=request.duration_minutes,
            link_expiry=datetime.utcnow().replace(hour=23, minute=59, second=59),
        )
        db.add(interview)
        await db.flush()
        interview_token = interview.unique_token

    notif = Notification(
        user_id=request.candidate_id,
        title=f"Interview Request {req.status.title()}",
        message=f"Your interview request '{request.title}' has been {req.status}."
                + (f" Join at /interview/{interview_token}" if interview_token else ""),
        notification_type="interview_update",
        link=f"/interview/{interview_token}" if interview_token else "/dashboard/interview-history",
    )
    db.add(notif)
    await db.flush()
    return request
