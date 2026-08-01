import base64
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.detection import VoiceDetection, DetectionSession
from app.schemas.detection import VoiceDetectionRequest, VoiceDetectionResponse
from app.ai_engine.voice_analyzer import VoiceAnalyzer
from app.ai_engine.xai_formatter import XAIFormatter

_voice_analyzer = VoiceAnalyzer()
_xai = XAIFormatter()


class VoiceDetectionService:
    """Service for voice authenticity detection."""

    @staticmethod
    async def detect(
        db: AsyncSession, request: VoiceDetectionRequest
    ) -> VoiceDetectionResponse:
        result = _voice_analyzer.analyze(request.audio_data, request.sample_rate)

        xai_output = _xai.format_detection("voice_detection", {
            "confidence": result.confidence,
            "explanations": result.explanations,
        })

        session_id = request.session_id
        if not session_id:
            session = DetectionSession(session_name="Auto-created voice session")
            db.add(session)
            await db.flush()
            session_id = session.id

        detection = VoiceDetection(
            session_id=session_id,
            confidence=round(result.confidence, 4),
            is_live=result.is_live,
            speaker_count=result.speaker_count,
            speaker_id=result.speaker_id,
            audio_quality=result.audio_quality.get("f0", {}).get("f0_mean", 0),
            noise_level=result.noise_analysis.get("snr_db", 0),
            spectral_analysis=result.spectral_features,
            metadata={
                "authenticity_score": result.authenticity_score,
                "prosody": result.prosody_features,
                "noise": result.noise_analysis,
                "xai": {
                    "summary": xai_output.summary,
                    "human_readable": xai_output.human_readable,
                    "feature_importance": xai_output.feature_importance,
                    "confidence_intervals": xai_output.confidence_intervals,
                },
                "latency_ms": result.latency_ms,
            },
        )
        db.add(detection)
        await db.flush()

        return VoiceDetectionResponse(
            id=detection.id,
            session_id=detection.session_id,
            confidence=detection.confidence,
            is_live=detection.is_live,
            speaker_count=detection.speaker_count,
            speaker_id=detection.speaker_id,
            audio_quality=detection.audio_quality,
            noise_level=detection.noise_level,
            spectral_analysis=detection.spectral_analysis,
            created_at=detection.created_at,
        )
