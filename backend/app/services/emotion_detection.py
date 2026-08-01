import base64
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.detection import EmotionDetection, DetectionSession
from app.schemas.detection import EmotionRequest, EmotionResponse
from app.ai_engine.emotion_analyzer import EmotionAnalyzer
from app.ai_engine.xai_formatter import XAIFormatter

_emotion_analyzer = EmotionAnalyzer()
_xai = XAIFormatter()


class EmotionDetectionService:
    """Service for emotion detection with temporal consistency."""

    @staticmethod
    async def detect(
        db: AsyncSession, request: EmotionRequest
    ) -> EmotionResponse:
        if not request.image_data:
            raise ValueError("image_data is required for emotion detection")

        result = _emotion_analyzer.analyze(request.image_data)

        xai_output = _xai.format_detection("emotion_detection", {
            "confidence": result.confidence,
            "explanations": result.explanations,
        })

        session_id = request.session_id
        if not session_id:
            session = DetectionSession(session_name="Auto-created emotion session")
            db.add(session)
            await db.flush()
            session_id = session.id

        detection = EmotionDetection(
            session_id=session_id,
            dominant_emotion=result.dominant_emotion,
            confidence=round(result.confidence, 4),
            emotion_scores=result.emotion_scores,
            consistency_score=result.consistency_score,
            temporal_analysis=result.temporal_analysis,
            metadata={
                "micro_expressions": result.micro_expressions,
                "valence_arousal": result.valence_arousal,
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

        return EmotionResponse(
            id=detection.id,
            session_id=detection.session_id,
            confidence=detection.confidence,
            dominant_emotion=detection.dominant_emotion,
            emotion_scores=detection.emotion_scores,
            consistency_score=detection.consistency_score,
            temporal_analysis=detection.temporal_analysis,
            created_at=detection.created_at,
        )
