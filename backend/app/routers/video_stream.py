import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.live_analysis import live_analysis_service

router = APIRouter(prefix="/video", tags=["Video Streaming"])


def _get_interview_data(interview_id: str) -> dict:
    return {}


class FrameRequest(BaseModel):
    frame: str
    candidate_name: str = ""


class AdminFrameRequest(BaseModel):
    frame: str


class ClientEventRequest(BaseModel):
    event_type: str
    details: dict = {}


@router.post("/{interview_id}/frame")
async def send_frame(
    interview_id: str,
    req: FrameRequest,
    user: User = Depends(get_current_user),
):
    result = live_analysis_service.analyze_frame(interview_id, req.frame)
    return {"ok": True, "analysis": result}


@router.get("/{interview_id}/frame")
async def get_frame(
    interview_id: str,
    user: User = Depends(get_current_user),
):
    state = live_analysis_service.get_state(interview_id)
    if not state:
        return {"frame": None, "active": False}
    return {"frame": None, "active": True, "candidate_name": ""}


@router.post("/{interview_id}/admin-frame")
async def send_admin_frame(
    interview_id: str,
    req: AdminFrameRequest,
    user: User = Depends(get_current_user),
):
    return {"ok": True}


@router.get("/{interview_id}/admin-frame")
async def get_admin_frame(
    interview_id: str,
    user: User = Depends(get_current_user),
):
    return {"frame": None, "active": False}


@router.post("/{interview_id}/event")
async def send_client_event(
    interview_id: str,
    req: ClientEventRequest,
    user: User = Depends(get_current_user),
):
    result = live_analysis_service.add_client_event(interview_id, req.event_type, req.details)
    return result


@router.get("/{interview_id}/analysis")
async def get_analysis(
    interview_id: str,
    user: User = Depends(get_current_user),
):
    result = live_analysis_service.get_analysis(interview_id)
    return result


@router.delete("/{interview_id}/cleanup")
async def cleanup(
    interview_id: str,
    user: User = Depends(get_current_user),
):
    live_analysis_service.stop_session(interview_id)
    return {"ok": True}
