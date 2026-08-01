from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.detection import (
    DetectionSession,
    FaceDetection,
    VoiceDetection,
    LipSyncDetection,
    EmotionDetection,
    TrustScore,
)
from app.schemas.detection import ReportRequest
from app.services.pdf_generator import PDFReportGenerator
from app.services.anomaly_engine import AnomalyEngine

router = APIRouter(prefix="/report", tags=["Reports"])
_pdf_gen = PDFReportGenerator()
_anomaly_engine = AnomalyEngine()


def _safe(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


@router.post(
    "/generate-pdf",
    summary="Generate downloadable PDF report",
    description="Generate a professional cybersecurity PDF report with trust scores, anomalies, and recommendations.",
)
async def generate_pdf_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DetectionSession).where(DetectionSession.id == request.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )

    face_result = await db.execute(
        select(FaceDetection).where(FaceDetection.session_id == request.session_id)
    )
    faces = face_result.scalars().all()

    voice_result = await db.execute(
        select(VoiceDetection).where(VoiceDetection.session_id == request.session_id)
    )
    voices = voice_result.scalars().all()

    lipsync_result = await db.execute(
        select(LipSyncDetection).where(LipSyncDetection.session_id == request.session_id)
    )
    lipsyncs = lipsync_result.scalars().all()

    emotion_result = await db.execute(
        select(EmotionDetection).where(EmotionDetection.session_id == request.session_id)
    )
    emotions = emotion_result.scalars().all()

    trust_result = await db.execute(
        select(TrustScore)
        .where(TrustScore.session_id == request.session_id)
        .order_by(TrustScore.created_at.desc())
        .limit(1)
    )
    trust = trust_result.scalar_one_or_none()

    scores = {
        "overall": trust.overall_score if trust else 0,
        "face": trust.face_score if trust else 0,
        "voice": trust.voice_score if trust else 0,
        "lipsync": trust.lipsync_score if trust else 0,
        "emotion": trust.emotion_score if trust else 0,
        "identity": trust.identity_score if trust else 0,
        "behavior": trust.behavior_score if trust else 0,
    }

    face_meta = faces[-1].extra_data if faces else {}
    voice_meta = voices[-1].extra_data if voices else {}
    lipsync_meta = lipsyncs[-1].extra_data if lipsyncs else {}
    emotion_meta = emotions[-1].extra_data if emotions else {}

    face_anomalies_input = {
        "confidence": faces[-1].confidence if faces else 1.0,
        "is_live": faces[-1].is_live if faces else True,
        "liveness_score": faces[-1].liveness_score if faces else 1.0,
        "face_count": faces[-1].face_count if faces else 1,
        "deepfake": _safe(face_meta, "deepfake", default={}),
    }
    voice_anomalies_input = {
        "confidence": voices[-1].confidence if voices else 1.0,
        "is_live": voices[-1].is_live if voices else True,
        "noise": _safe(voice_meta, "noise", default={}),
        "speaker_count": voices[-1].speaker_count if voices else 1,
    }
    lipsync_anomalies_input = {
        "sync_score": lipsyncs[-1].sync_score if lipsyncs else 1.0,
        "audio_visual_offset": lipsyncs[-1].audio_visual_offset if lipsyncs else 0,
    }
    emotion_anomalies_input = {
        "consistency_score": emotions[-1].consistency_score if emotions else 1.0,
        "dominant_emotion": emotions[-1].dominant_emotion if emotions else "neutral",
        "micro_expressions": _safe(emotion_meta, "micro_expressions", default=[]),
    }

    anomalies = _anomaly_engine.detect_anomalies(
        face_anomalies_input,
        voice_anomalies_input,
        lipsync_anomalies_input,
        emotion_anomalies_input,
    )

    recommendations = _anomaly_engine.generate_recommendations(scores, anomalies)

    critical_count = sum(1 for a in anomalies if a.get("severity") == "critical")
    high_count = sum(1 for a in anomalies if a.get("severity") == "high")
    if critical_count > 0:
        overall_severity = "critical"
    elif high_count > 0:
        overall_severity = "high"
    elif any(a.get("severity") == "medium" for a in anomalies):
        overall_severity = "medium"
    else:
        overall_severity = "low"

    severity_data = {
        "overall": overall_severity,
        "critical_count": critical_count,
        "high_count": high_count,
        "total_anomalies": len(anomalies),
        "factors": [
            {"factor": a["type"], "severity": a["severity"], "reason": a["description"]}
            for a in anomalies
        ],
    }

    xai_data = {}
    if trust and trust.risk_factors:
        xai_data = trust.risk_factors.get("xai", {})

    participants = []
    if session.user_id:
        participants.append(session.user_id)

    pdf_data = {
        "session_id": request.session_id,
        "meeting": {
            "date": session.created_at.strftime("%Y-%m-%d %H:%M:%S") if session.created_at else "N/A",
            "duration": f"{len(faces) + len(voices) + len(lipsyncs) + len(emotions)} detections",
            "participants": participants if participants else ["System"],
            "type": request.report_type or "Security Verification",
            "location": "Virtual Session",
            "organizer": session.user_id or "DeepShield AI",
        },
        "scores": scores,
        "anomalies": anomalies,
        "severity": severity_data,
        "recommendations": recommendations,
        "xai": xai_data,
    }

    pdf_bytes = _pdf_gen.generate(pdf_data)

    filename = f"deepshield_report_{request.session_id[:8]}_{session.created_at.strftime('%Y%m%d')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post(
    "/preview",
    summary="Preview report data as JSON",
    description="Return the report data structure before PDF generation.",
)
async def preview_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DetectionSession).where(DetectionSession.id == request.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )

    face_result = await db.execute(
        select(FaceDetection).where(FaceDetection.session_id == request.session_id)
    )
    faces = face_result.scalars().all()

    voice_result = await db.execute(
        select(VoiceDetection).where(VoiceDetection.session_id == request.session_id)
    )
    voices = voice_result.scalars().all()

    lipsync_result = await db.execute(
        select(LipSyncDetection).where(LipSyncDetection.session_id == request.session_id)
    )
    lipsyncs = lipsync_result.scalars().all()

    emotion_result = await db.execute(
        select(EmotionDetection).where(EmotionDetection.session_id == request.session_id)
    )
    emotions = emotion_result.scalars().all()

    trust_result = await db.execute(
        select(TrustScore)
        .where(TrustScore.session_id == request.session_id)
        .order_by(TrustScore.created_at.desc())
        .limit(1)
    )
    trust = trust_result.scalar_one_or_none()

    scores = {
        "overall": trust.overall_score if trust else 0,
        "face": trust.face_score if trust else 0,
        "voice": trust.voice_score if trust else 0,
        "lipsync": trust.lipsync_score if trust else 0,
        "emotion": trust.emotion_score if trust else 0,
        "identity": trust.identity_score if trust else 0,
        "behavior": trust.behavior_score if trust else 0,
    }

    anomalies = _anomaly_engine.detect_anomalies(
        {"confidence": faces[-1].confidence if faces else 1.0, "is_live": faces[-1].is_live if faces else True, "liveness_score": faces[-1].liveness_score if faces else 1.0, "face_count": faces[-1].face_count if faces else 1, "deepfake": _safe(faces[-1].extra_data if faces else {}, "deepfake", default={})},
        {"confidence": voices[-1].confidence if voices else 1.0, "is_live": voices[-1].is_live if voices else True, "noise": _safe(voices[-1].extra_data if voices else {}, "noise", default={}), "speaker_count": voices[-1].speaker_count if voices else 1},
        {"sync_score": lipsyncs[-1].sync_score if lipsyncs else 1.0, "audio_visual_offset": lipsyncs[-1].audio_visual_offset if lipsyncs else 0},
        {"consistency_score": emotions[-1].consistency_score if emotions else 1.0, "dominant_emotion": emotions[-1].dominant_emotion if emotions else "neutral", "micro_expressions": _safe(emotions[-1].extra_data if emotions else {}, "micro_expressions", default=[])},
    )

    recommendations = _anomaly_engine.generate_recommendations(scores, anomalies)

    return {
        "session_id": request.session_id,
        "meeting": {
            "date": session.created_at.isoformat() if session.created_at else "N/A",
            "participants": [session.user_id] if session.user_id else ["System"],
        },
        "scores": scores,
        "anomalies": anomalies,
        "severity": {"overall": "critical" if any(a["severity"] == "critical" for a in anomalies) else "high" if any(a["severity"] == "high" for a in anomalies) else "medium" if any(a["severity"] == "medium" for a in anomalies) else "low"},
        "recommendations": recommendations,
        "detection_counts": {
            "faces": len(faces),
            "voices": len(voices),
            "lipsyncs": len(lipsyncs),
            "emotions": len(emotions),
        },
    }
