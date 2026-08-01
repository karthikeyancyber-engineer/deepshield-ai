from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

try:
    from livekit.api import AccessToken, VideoGrants
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False

from app.database import get_db
from app.models.user import User
from app.models.interview import Interview
from app.middleware.auth import get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/livekit", tags=["LiveKit"])


class LiveKitTokenRequest(BaseModel):
    room: str
    identity: str
    name: str = ""


class LiveKitTokenResponse(BaseModel):
    token: str
    ws_url: str


def generate_livekit_token(identity: str, room: str, name: str = "") -> str:
    if not LIVEKIT_AVAILABLE:
        raise HTTPException(status_code=500, detail="LiveKit SDK not installed")
    token = (
        AccessToken(
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET,
        )
        .with_identity(identity)
        .with_name(name or identity)
        .with_grants(
            VideoGrants(
                room=room,
                room_join=True,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
    )
    return token.to_jwt()


@router.post("/token", response_model=LiveKitTokenResponse)
async def get_livekit_token(
    req: LiveKitTokenRequest,
    user: User = Depends(get_current_user),
):
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="LiveKit not configured")

    token = generate_livekit_token(
        identity=req.identity,
        room=req.room,
        name=req.name or user.full_name,
    )
    return LiveKitTokenResponse(token=token, ws_url=settings.LIVEKIT_URL)


@router.post("/join/{token_str}", response_model=LiveKitTokenResponse)
async def join_interview_room(
    token_str: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Interview).where(Interview.unique_token == token_str)
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.link_expiry:
        expiry = interview.link_expiry.replace(tzinfo=None) if interview.link_expiry.tzinfo else interview.link_expiry
        if expiry < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Interview link has expired")

    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="LiveKit not configured")

    identity = f"{user.id}_{user.role}"
    room_name = f"interview_{interview.id}"

    if user.role == "candidate":
        interview.candidate_id = user.id
        if interview.status == "scheduled":
            interview.status = "in_progress"
            interview.started_at = datetime.utcnow()
        interview.session_status = "waiting"
    elif user.role == "admin":
        interview.session_status = "admin_joined"

    await db.flush()

    token = generate_livekit_token(
        identity=identity,
        room=room_name,
        name=user.full_name,
    )

    return LiveKitTokenResponse(token=token, ws_url=settings.LIVEKIT_URL)
