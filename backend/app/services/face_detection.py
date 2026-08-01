import base64
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.detection import FaceDetection, DetectionSession
from app.schemas.detection import FaceDetectionRequest, FaceDetectionResponse
from app.ai_engine.face_analyzer import FaceAnalyzer
from app.ai_engine.deepfake_detector import DeepfakeDetector
from app.ai_engine.xai_formatter import XAIFormatter

_face_analyzer = FaceAnalyzer()
_deepfake_detector = DeepfakeDetector()
_xai = XAIFormatter()


class FaceDetectionService:
    """Service combining face analysis with deepfake detection."""

    @staticmethod
    async def detect(
        db: AsyncSession, request: FaceDetectionRequest
    ) -> FaceDetectionResponse:
        face_result = _face_analyzer.analyze(request.image_data)
        deepfake_result = _deepfake_detector.detect(request.image_data)

        combined_confidence = (
            face_result.confidence * 0.5 +
            deepfake_result.authenticity_score * 0.5
        )

        xai_output = _xai.format_detection("face_detection", {
            "confidence": combined_confidence,
            "explanations": face_result.explanations + deepfake_result.explanations,
        })

        session_id = request.session_id
        if not session_id:
            session = DetectionSession(session_name="Auto-created face session")
            db.add(session)
            await db.flush()
            session_id = session.id

        detection = FaceDetection(
            session_id=session_id,
            confidence=round(combined_confidence, 4),
            face_count=face_result.face_count,
            bounding_boxes={"faces": face_result.bounding_boxes},
            landmarks={"landmarks": face_result.landmarks},
            is_live=deepfake_result.authenticity_score >= 0.5,
            liveness_score=deepfake_result.authenticity_score,
            quality_score=face_result.quality_score,
            metadata={
                "deepfake": {
                    "is_deepfake": deepfake_result.is_deepfake,
                    "authenticity_score": deepfake_result.authenticity_score,
                    "artifacts": deepfake_result.visual_artifacts,
                },
                "face_analysis": {
                    "symmetry": face_result.symmetry_score,
                    "blur": face_result.blur_score,
                    "illumination": face_result.illumination_score,
                    "pose": face_result.pose_angles,
                },
                "xai": {
                    "summary": xai_output.summary,
                    "human_readable": xai_output.human_readable,
                    "feature_importance": xai_output.feature_importance,
                    "confidence_intervals": xai_output.confidence_intervals,
                },
                "latency_ms": face_result.latency_ms + deepfake_result.latency_ms,
            },
        )
        db.add(detection)
        await db.flush()

        return FaceDetectionResponse(
            id=detection.id,
            session_id=detection.session_id,
            confidence=detection.confidence,
            face_count=detection.face_count,
            bounding_boxes=detection.bounding_boxes,
            landmarks=detection.landmarks,
            is_live=detection.is_live,
            liveness_score=detection.liveness_score,
            quality_score=detection.quality_score,
            created_at=detection.created_at,
        )
