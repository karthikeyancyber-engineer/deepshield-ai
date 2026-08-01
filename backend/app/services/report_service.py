from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.detection import (
    Report,
    DetectionSession,
    FaceDetection,
    VoiceDetection,
    LipSyncDetection,
    EmotionDetection,
    TrustScore,
)
from app.schemas.detection import ReportRequest, ReportResponse
from app.ai_engine.xai_formatter import XAIFormatter

_xai = XAIFormatter()


class ReportService:
    """Service for generating explainable detection reports."""

    @staticmethod
    async def generate(
        db: AsyncSession, request: ReportRequest
    ) -> ReportResponse:
        result = await db.execute(
            select(DetectionSession).where(DetectionSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {request.session_id} not found")

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

        xai_explanations = []
        all_latencies = []

        for f in faces:
            meta = f.extra_data or {}
            xai = meta.get("xai", {})
            if xai:
                xai_explanations.append({"modality": "face", "xai": xai})
            lat = meta.get("latency_ms", 0)
            if lat: all_latencies.append(lat)

        for v in voices:
            meta = v.extra_data or {}
            xai = meta.get("xai", {})
            if xai:
                xai_explanations.append({"modality": "voice", "xai": xai})
            lat = meta.get("latency_ms", 0)
            if lat: all_latencies.append(lat)

        for l in lipsyncs:
            meta = l.extra_data or {}
            xai = meta.get("xai", {})
            if xai:
                xai_explanations.append({"modality": "lipsync", "xai": xai})
            lat = meta.get("latency_ms", 0)
            if lat: all_latencies.append(lat)

        for e in emotions:
            meta = e.extra_data or {}
            xai = meta.get("xai", {})
            if xai:
                xai_explanations.append({"modality": "emotion", "xai": xai})
            lat = meta.get("latency_ms", 0)
            if lat: all_latencies.append(lat)

        trust_xai = None
        if trust and trust.risk_factors:
            trust_xai = trust.risk_factors.get("xai", {})

        report_data = {
            "session": {
                "id": session.id,
                "name": session.session_name,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
            },
            "summary": {
                "total_face_detections": len(faces),
                "total_voice_detections": len(voices),
                "total_lipsync_detections": len(lipsyncs),
                "total_emotion_detections": len(emotions),
                "total_processing_time_ms": round(sum(all_latencies), 2),
                "avg_latency_ms": round(sum(all_latencies) / max(len(all_latencies), 1), 2),
            },
            "face_analysis": [
                {
                    "id": f.id,
                    "confidence": f.confidence,
                    "face_count": f.face_count,
                    "is_live": f.is_live,
                    "liveness_score": f.liveness_score,
                    "quality_score": f.quality_score,
                    "metadata": f.extra_data,
                    "timestamp": f.created_at.isoformat(),
                }
                for f in faces
            ],
            "voice_analysis": [
                {
                    "id": v.id,
                    "confidence": v.confidence,
                    "is_live": v.is_live,
                    "speaker_count": v.speaker_count,
                    "spectral_analysis": v.spectral_analysis,
                    "metadata": v.extra_data,
                    "timestamp": v.created_at.isoformat(),
                }
                for v in voices
            ],
            "lipsync_analysis": [
                {
                    "id": l.id,
                    "confidence": l.confidence,
                    "sync_score": l.sync_score,
                    "audio_visual_offset": l.audio_visual_offset,
                    "metadata": l.extra_data,
                    "timestamp": l.created_at.isoformat(),
                }
                for l in lipsyncs
            ],
            "emotion_analysis": [
                {
                    "id": e.id,
                    "dominant_emotion": e.dominant_emotion,
                    "confidence": e.confidence,
                    "emotion_scores": e.emotion_scores,
                    "consistency_score": e.consistency_score,
                    "metadata": e.extra_data,
                    "timestamp": e.created_at.isoformat(),
                }
                for e in emotions
            ],
            "trust_assessment": {
                "overall_score": trust.overall_score if trust else None,
                "risk_level": trust.risk_level if trust else None,
                "face_score": trust.face_score if trust else None,
                "voice_score": trust.voice_score if trust else None,
                "lipsync_score": trust.lipsync_score if trust else None,
                "emotion_score": trust.emotion_score if trust else None,
                "identity_score": trust.identity_score if trust else None,
                "behavior_score": trust.behavior_score if trust else None,
                "risk_factors": trust.risk_factors if trust else None,
            }
            if trust
            else None,
            "explainable_ai": {
                "per_modality": xai_explanations,
                "trust_xai": trust_xai,
                "model_version": "1.0.0",
                "explanation_method": "feature_contribution_analysis",
            },
        }

        summary_text = (
            f"Detection report for session '{session.session_name or session.id}'. "
            f"Analyzed {len(faces)} face, {len(voices)} voice, {len(lipsyncs)} lipsync, "
            f"and {len(emotions)} emotion detections. "
            f"Overall trust score: {trust.overall_score if trust else 'N/A'} "
            f"({trust.risk_level if trust else 'unknown'} risk). "
            f"Total processing time: {sum(all_latencies):.1f}ms."
        )

        report = Report(
            session_id=request.session_id,
            title=request.title,
            summary=summary_text,
            report_type=request.report_type,
            status="completed",
            data=report_data,
        )
        db.add(report)
        await db.flush()

        return ReportResponse(
            id=report.id,
            session_id=report.session_id,
            title=report.title,
            summary=report.summary,
            report_type=report.report_type,
            status=report.status,
            data=report.data,
            created_at=report.created_at,
        )
