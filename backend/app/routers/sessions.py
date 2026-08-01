from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.detection import DetectionSession
from app.schemas.detection import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a detection session",
    description="Initialize a new detection session to group related face, voice, lipsync, and emotion analyses.",
)
async def create_session(
    request: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    session = DetectionSession(
        session_name=request.session_name,
        user_id=request.user_id,
    )
    db.add(session)
    await db.flush()
    return session


@router.get(
    "/",
    response_model=list[SessionResponse],
    summary="List all sessions",
    description="Retrieve all detection sessions with pagination support.",
)
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DetectionSession).order_by(DetectionSession.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session by ID",
    description="Retrieve a specific detection session by its unique identifier.",
)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DetectionSession).where(DetectionSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": f"Session {session_id} not found", "code": "SESSION_NOT_FOUND"},
        )
    return session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="Delete a detection session and all associated detections.",
)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DetectionSession).where(DetectionSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": f"Session {session_id} not found", "code": "SESSION_NOT_FOUND"},
        )
    await db.delete(session)
