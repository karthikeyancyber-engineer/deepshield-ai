from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.detection import (
    FaceDetectionRequest,
    FaceDetectionResponse,
    VoiceDetectionRequest,
    VoiceDetectionResponse,
    LipSyncRequest,
    LipSyncResponse,
    EmotionRequest,
    EmotionResponse,
    ErrorResponse,
)
from app.services.face_detection import FaceDetectionService
from app.services.voice_detection import VoiceDetectionService
from app.services.lipsync_detection import LipSyncDetectionService
from app.services.emotion_detection import EmotionDetectionService

router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post(
    "/face",
    response_model=FaceDetectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Detect faces in image",
    description="Analyze an image to detect faces, assess liveness, extract landmarks, and evaluate image quality.",
)
async def detect_face(
    request: FaceDetectionRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await FaceDetectionService.detect(db, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/voice",
    response_model=VoiceDetectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Detect and analyze voice",
    description="Analyze audio data to detect live voice, identify speakers, and assess audio quality.",
)
async def detect_voice(
    request: VoiceDetectionRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await VoiceDetectionService.detect(db, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/lipsync",
    response_model=LipSyncResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze lip-sync accuracy",
    description="Compare video and audio streams to measure lip-sync accuracy and detect deepfake indicators.",
)
async def detect_lipsync(
    request: LipSyncRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await LipSyncDetectionService.detect(db, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/emotion",
    response_model=EmotionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Detect emotions",
    description="Analyze facial expressions and voice to detect emotions with temporal consistency scoring.",
)
async def detect_emotion(
    request: EmotionRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await EmotionDetectionService.detect(db, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
