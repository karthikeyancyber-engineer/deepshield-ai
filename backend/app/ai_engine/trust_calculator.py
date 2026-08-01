import numpy as np
from dataclasses import dataclass
from app.ai_engine.base import Timer, normalize


@dataclass
class TrustScoreResult:
    overall_score: float
    face_score: float
    voice_score: float
    lipsync_score: float
    emotion_score: float
    identity_score: float
    behavior_score: float
    risk_level: str
    risk_factors: list[dict]
    confidence_breakdown: dict
    explanations: list[dict]
    latency_ms: float


class TrustCalculator:
    """
    Composite trust score calculator using weighted fusion
    of all detection modalities with explainable output.
    """

    DEFAULT_WEIGHTS = {
        "face": 0.30,
        "voice": 0.25,
        "lipsync": 0.25,
        "emotion": 0.20,
    }

    RISK_THRESHOLDS = {
        "low": 80,
        "moderate": 60,
        "elevated": 40,
        "critical": 0,
    }

    def __init__(self, weights: dict | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def _normalize_score(self, value: float | None, max_val: float = 1.0) -> float | None:
        if value is None:
            return None
        return round(float(np.clip(value / max_val, 0.0, 1.0)) * 100, 2)

    def _compute_identity_score(self, face: float | None, voice: float | None) -> float:
        if face is not None and voice is not None:
            return face * 0.6 + voice * 0.4
        if face is not None:
            return face
        if voice is not None:
            return voice
        return 50.0

    def _compute_behavior_score(self, emotion: float | None, lipsync: float | None) -> float:
        if emotion is not None and lipsync is not None:
            return emotion * 0.5 + lipsync * 0.5
        if emotion is not None:
            return emotion
        if lipsync is not None:
            return lipsync
        return 50.0

    def _determine_risk_level(self, score: float) -> str:
        for level, threshold in self.RISK_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "critical"

    def _identify_risk_factors(
        self, face: float | None, voice: float | None,
        lipsync: float | None, emotion: float | None
    ) -> list[dict]:
        factors = []

        checks = [
            ("face", face, 70, "Face authenticity below threshold"),
            ("voice", voice, 65, "Voice authenticity below threshold"),
            ("lipsync", lipsync, 60, "Lip-sync verification failed"),
            ("emotion", emotion, 55, "Emotion consistency low"),
        ]

        for name, value, threshold, reason in checks:
            if value is not None and value < threshold:
                factors.append({
                    "factor": name,
                    "score": value,
                    "threshold": threshold,
                    "severity": "high" if value < threshold * 0.7 else "medium",
                    "reason": reason,
                    "recommendation": f"Review {name} detection results manually",
                })

        return factors

    def _build_confidence_breakdown(
        self, face: float | None, voice: float | None,
        lipsync: float | None, emotion: float | None
    ) -> dict:
        available = []
        if face is not None: available.append(("face", face, self.weights["face"]))
        if voice is not None: available.append(("voice", voice, self.weights["voice"]))
        if lipsync is not None: available.append(("lipsync", lipsync, self.weights["lipsync"]))
        if emotion is not None: available.append(("emotion", emotion, self.weights["emotion"]))

        total_weight = sum(w for _, _, w in available)

        return {
            "modalities_used": len(available),
            "modalities": [
                {
                    "name": name,
                    "raw_score": score,
                    "weight": weight,
                    "normalized_weight": round(weight / (total_weight + 1e-8), 4),
                    "weighted_contribution": round(score * weight / (total_weight + 1e-8), 2),
                }
                for name, score, weight in available
            ],
            "total_weight": round(total_weight, 4),
        }

    def _generate_explanations(
        self, overall: float, face: float | None, voice: float | None,
        lipsync: float | None, emotion: float | None, identity: float,
        behavior: float, risk_level: str
    ) -> list[dict]:
        explanations = []

        explanations.append({
            "feature": "overall_trust",
            "value": overall,
            "weight": 1.0,
            "contribution": overall,
            "explanation": f"Overall trust score: {overall:.1f}/100 — Risk level: {risk_level.upper()}",
        })

        if face is not None:
            explanations.append({
                "feature": "face_trust",
                "value": face,
                "weight": self.weights["face"],
                "contribution": round(face * self.weights["face"], 2),
                "explanation": f"Face authenticity: {face:.1f}% — {'Trusted' if face > 70 else 'Suspicious'}",
            })

        if voice is not None:
            explanations.append({
                "feature": "voice_trust",
                "value": voice,
                "weight": self.weights["voice"],
                "contribution": round(voice * self.weights["voice"], 2),
                "explanation": f"Voice authenticity: {voice:.1f}% — {'Human voice detected' if voice > 65 else 'Potential synthetic voice'}",
            })

        if lipsync is not None:
            explanations.append({
                "feature": "lipsync_trust",
                "value": lipsync,
                "weight": self.weights["lipsync"],
                "contribution": round(lipsync * self.weights["lipsync"], 2),
                "explanation": f"Lip-sync accuracy: {lipsync:.1f}% — {'Audio-visual match' if lipsync > 60 else 'Sync mismatch detected'}",
            })

        if emotion is not None:
            explanations.append({
                "feature": "emotion_trust",
                "value": emotion,
                "weight": self.weights["emotion"],
                "contribution": round(emotion * self.weights["emotion"], 2),
                "explanation": f"Emotion consistency: {emotion:.1f}% — {'Natural expression' if emotion > 55 else 'Inconsistent emotions'}",
            })

        explanations.append({
            "feature": "identity_verification",
            "value": identity,
            "weight": 0.5,
            "contribution": round(identity * 0.5, 2),
            "explanation": f"Identity score: {identity:.1f}% — Combines face and voice biometrics",
        })

        explanations.append({
            "feature": "behavioral_analysis",
            "value": behavior,
            "weight": 0.5,
            "contribution": round(behavior * 0.5, 2),
            "explanation": f"Behavior score: {behavior:.1f}% — Combines emotion and lip-sync patterns",
        })

        return explanations

    def calculate(
        self,
        face_confidence: float | None = None,
        voice_confidence: float | None = None,
        lipsync_score: float | None = None,
        emotion_consistency: float | None = None,
        weights: dict | None = None,
    ) -> TrustScoreResult:
        with Timer() as timer:
            w = weights or self.weights

            face = self._normalize_score(face_confidence) if face_confidence is not None else None
            voice = self._normalize_score(voice_confidence) if voice_confidence is not None else None
            lipsync = self._normalize_score(lipsync_score) if lipsync_score is not None else None
            emotion = self._normalize_score(emotion_consistency) if emotion_consistency is not None else None

            identity = self._compute_identity_score(face, voice)
            behavior = self._compute_behavior_score(emotion, lipsync)

            scores = []
            weights_used = []
            if face is not None:
                scores.append(face)
                weights_used.append(w["face"])
            if voice is not None:
                scores.append(voice)
                weights_used.append(w["voice"])
            if lipsync is not None:
                scores.append(lipsync)
                weights_used.append(w["lipsync"])
            if emotion is not None:
                scores.append(emotion)
                weights_used.append(w["emotion"])

            if not scores:
                overall = 50.0
            else:
                total_w = sum(weights_used)
                overall = round(sum(s * wt for s, wt in zip(scores, weights_used)) / total_w, 2)

            risk_level = self._determine_risk_level(overall)
            risk_factors = self._identify_risk_factors(face, voice, lipsync, emotion)
            confidence_breakdown = self._build_confidence_breakdown(face, voice, lipsync, emotion)
            explanations = self._generate_explanations(
                overall, face, voice, lipsync, emotion, identity, behavior, risk_level
            )

        return TrustScoreResult(
            overall_score=overall,
            face_score=face or 0.0,
            voice_score=voice or 0.0,
            lipsync_score=lipsync or 0.0,
            emotion_score=emotion or 0.0,
            identity_score=round(identity, 2),
            behavior_score=round(behavior, 2),
            risk_level=risk_level,
            risk_factors=risk_factors,
            confidence_breakdown=confidence_breakdown,
            explanations=explanations,
            latency_ms=round(timer.elapsed_ms, 2),
        )
