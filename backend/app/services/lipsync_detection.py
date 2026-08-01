import base64
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.detection import LipSyncDetection, DetectionSession
from app.schemas.detection import LipSyncRequest, LipSyncResponse
from app.ai_engine.lipsync_analyzer import LipSyncAnalyzer
from app.ai_engine.xai_formatter import XAIFormatter

_lipsync_analyzer = LipSyncAnalyzer()
_xai = XAIFormatter()


class LipSyncDetectionService:
    """Service for lip-sync verification."""

    @staticmethod
    async def detect(
        db: AsyncSession, request: LipSyncRequest
    ) -> LipSyncResponse:
        result = _lipsync_analyzer.analyze(
            request.video_data, request.audio_data, request.frame_rate
        )

        xai_output = _xai.format_detection("lipsync_detection", {
            "confidence": result.confidence,
            "explanations": result.explanations,
        })

        session_id = request.session_id
        if not session_id:
            session = DetectionSession(session_name="Auto-created lipsync session")
            db.add(session)
            await db.flush()
            session_id = session.id

        detection = LipSyncDetection(
            session_id=session_id,
            confidence=round(result.confidence, 4),
            sync_score=result.sync_score,
            audio_visual_offset=result.audio_visual_offset,
            frame_analysis=result.frame_analysis,
            mouth_tracking=result.mouth_tracking,
            metadata={
                "correlation_metrics": result.correlation_metrics,
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

        return LipSyncResponse(
            id=detection.id,
            session_id=detection.session_id,
            confidence=detection.confidence,
            sync_score=detection.sync_score,
            audio_visual_offset=detection.audio_visual_offset,
            frame_analysis=detection.frame_analysis,
            mouth_tracking=detection.mouth_tracking,
            created_at=detection.created_at,
        )
