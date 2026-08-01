from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.detection import (
    TrustScore,
    DetectionSession,
    FaceDetection,
    VoiceDetection,
    LipSyncDetection,
    EmotionDetection,
)
from app.schemas.detection import TrustScoreRequest, TrustScoreResponse
from app.ai_engine.trust_calculator import TrustCalculator
from app.ai_engine.xai_formatter import XAIFormatter

_trust_calculator = TrustCalculator()
_xai = XAIFormatter()


class TrustScoreService:
    """Service for computing composite trust scores with explainability."""

    @staticmethod
    async def compute(
        db: AsyncSession, request: TrustScoreRequest
    ) -> TrustScoreResponse:
        result = await db.execute(
            select(DetectionSession).where(DetectionSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {request.session_id} not found")

        face_result = await db.execute(
            select(FaceDetection)
            .where(FaceDetection.session_id == request.session_id)
            .order_by(FaceDetection.created_at.desc())
            .limit(1)
        )
        face_det = face_result.scalar_one_or_none()

        voice_result = await db.execute(
            select(VoiceDetection)
            .where(VoiceDetection.session_id == request.session_id)
            .order_by(VoiceDetection.created_at.desc())
            .limit(1)
        )
        voice_det = voice_result.scalar_one_or_none()

        lipsync_result = await db.execute(
            select(LipSyncDetection)
            .where(LipSyncDetection.session_id == request.session_id)
            .order_by(LipSyncDetection.created_at.desc())
            .limit(1)
        )
        lipsync_det = lipsync_result.scalar_one_or_none()

        emotion_result = await db.execute(
            select(EmotionDetection)
            .where(EmotionDetection.session_id == request.session_id)
            .order_by(EmotionDetection.created_at.desc())
            .limit(1)
        )
        emotion_det = emotion_result.scalar_one_or_none()

        face_conf = face_det.confidence if face_det else None
        voice_conf = voice_det.confidence if voice_det else None
        lipsync_sc = lipsync_det.sync_score if lipsync_det else None
        emotion_sc = emotion_det.consistency_score if emotion_det else None

        trust = _trust_calculator.calculate(
            face_confidence=face_conf,
            voice_confidence=voice_conf,
            lipsync_score=lipsync_sc,
            emotion_consistency=emotion_sc,
        )

        xai_output = _xai.format_trust_score({
            "overall_score": trust.overall_score,
            "face_score": trust.face_score,
            "voice_score": trust.voice_score,
            "lipsync_score": trust.lipsync_score,
            "emotion_score": trust.emotion_score,
            "identity_score": trust.identity_score,
            "behavior_score": trust.behavior_score,
            "risk_level": trust.risk_level,
            "risk_factors": trust.risk_factors,
            "confidence_breakdown": trust.confidence_breakdown,
            "explanations": [
                {"feature": e["feature"], "value": e["value"], "weight": e["weight"], "contribution": e["contribution"], "explanation": e["explanation"]}
                for e in trust.explanations
            ],
        })

        db_trust = TrustScore(
            session_id=request.session_id,
            overall_score=trust.overall_score,
            face_score=trust.face_score,
            voice_score=trust.voice_score,
            lipsync_score=trust.lipsync_score,
            emotion_score=trust.emotion_score,
            identity_score=trust.identity_score,
            behavior_score=trust.behavior_score,
            risk_level=trust.risk_level,
            risk_factors={
                "factors": trust.risk_factors,
                "xai": {
                    "summary": xai_output.summary,
                    "human_readable": xai_output.human_readable,
                    "feature_importance": xai_output.feature_importance,
                    "confidence_intervals": xai_output.confidence_intervals,
                },
            },
        )
        db.add(db_trust)
        await db.flush()

        return TrustScoreResponse(
            id=db_trust.id,
            session_id=db_trust.session_id,
            overall_score=db_trust.overall_score,
            face_score=db_trust.face_score,
            voice_score=db_trust.voice_score,
            lipsync_score=db_trust.lipsync_score,
            emotion_score=db_trust.emotion_score,
            identity_score=db_trust.identity_score,
            behavior_score=db_trust.behavior_score,
            risk_level=db_trust.risk_level,
            risk_factors=db_trust.risk_factors,
            created_at=db_trust.created_at,
        )
