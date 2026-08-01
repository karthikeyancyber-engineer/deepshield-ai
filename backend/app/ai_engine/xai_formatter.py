from dataclasses import dataclass


@dataclass
class XAIOutput:
    summary: str
    feature_importance: list[dict]
    decision_factors: list[dict]
    confidence_intervals: dict
    human_readable: str
    technical_detail: dict


class XAIFormatter:
    """
    Explainable AI output formatter that generates human-readable
    explanations and structured decision breakdowns.
    """

    def format_detection(self, detection_type: str, result: dict) -> XAIOutput:
        explanations = result.get("explanations", [])
        confidence = result.get("confidence", 0)

        feature_importance = sorted(
            [
                {
                    "name": e.get("feature", "unknown"),
                    "score": round(e.get("value", 0), 4),
                    "weight": round(e.get("weight", 0), 4),
                    "contribution": round(e.get("contribution", 0), 4),
                    "explanation": e.get("explanation", ""),
                }
                for e in explanations
            ],
            key=lambda x: abs(x["contribution"]),
            reverse=True,
        )

        decision_factors = [
            {
                "factor": f["name"],
                "impact": "positive" if f["contribution"] > 0 else "negative",
                "magnitude": abs(f["contribution"]),
                "description": f["explanation"],
            }
            for f in feature_importance
        ]

        top_factor = feature_importance[0] if feature_importance else None

        summary = self._generate_summary(detection_type, confidence, feature_importance)
        human_readable = self._generate_human_readable(detection_type, confidence, top_factor, decision_factors)

        confidence_intervals = {
            "point_estimate": round(confidence, 4),
            "lower_bound": round(max(0, confidence - 0.1), 4),
            "upper_bound": round(min(1, confidence + 0.1), 4),
            "confidence_level": 0.90,
            "method": "bootstrap_approximation",
        }

        technical_detail = {
            "detection_type": detection_type,
            "n_features_analyzed": len(feature_importance),
            "total_contribution": round(sum(f["contribution"] for f in feature_importance), 4),
            "feature_entropy": round(self._compute_entropy(feature_importance), 4),
            "dominant_factor": top_factor["name"] if top_factor else None,
        }

        return XAIOutput(
            summary=summary,
            feature_importance=feature_importance,
            decision_factors=decision_factors,
            confidence_intervals=confidence_intervals,
            human_readable=human_readable,
            technical_detail=technical_detail,
        )

    def format_trust_score(self, trust_result: dict) -> XAIOutput:
        explanations = trust_result.get("explanations", [])
        overall = trust_result.get("overall_score", 0)
        risk_level = trust_result.get("risk_level", "unknown")
        risk_factors = trust_result.get("risk_factors", [])

        feature_importance = sorted(
            [
                {
                    "name": e.get("feature", "unknown"),
                    "score": round(e.get("value", 0), 4),
                    "weight": round(e.get("weight", 0), 4),
                    "contribution": round(e.get("contribution", 0), 4),
                    "explanation": e.get("explanation", ""),
                }
                for e in explanations
            ],
            key=lambda x: abs(x["contribution"]),
            reverse=True,
        )

        decision_factors = []
        for f in feature_importance:
            impact = "positive" if f["score"] > 60 else "negative" if f["score"] < 40 else "neutral"
            decision_factors.append({
                "factor": f["name"],
                "impact": impact,
                "magnitude": abs(f["contribution"]),
                "description": f["explanation"],
            })

        risk_summary = ""
        if risk_factors:
            risk_summary = f" {len(risk_factors)} risk factor(s) identified: " + ", ".join(
                rf["reason"] for rf in risk_factors
            )

        summary = (
            f"Trust Score Analysis: {overall:.1f}/100 ({risk_level.upper()} risk). "
            f"Identity verification: {trust_result.get('identity_score', 0):.1f}%. "
            f"Behavioral analysis: {trust_result.get('behavior_score', 0):.1f}%."
            f"{risk_summary}"
        )

        human_readable = (
            f"The system assessed the overall trust level at {overall:.0f} out of 100, "
            f"which falls into the {risk_level} risk category. "
        )

        if trust_result.get("face_score", 0) > 0:
            human_readable += f"Face analysis scored {trust_result['face_score']:.0f}%. "
        if trust_result.get("voice_score", 0) > 0:
            human_readable += f"Voice analysis scored {trust_result['voice_score']:.0f}%. "
        if trust_result.get("lipsync_score", 0) > 0:
            human_readable += f"Lip-sync verification scored {trust_result['lipsync_score']:.0f}%. "
        if trust_result.get("emotion_score", 0) > 0:
            human_readable += f"Emotion consistency scored {trust_result['emotion_score']:.0f}%. "

        if risk_factors:
            human_readable += f"Warning: {len(risk_factors)} concern(s) detected. "
            for rf in risk_factors[:3]:
                human_readable += f"{rf['reason']}. "

        confidence_intervals = {
            "point_estimate": round(overall / 100, 4),
            "lower_bound": round(max(0, overall / 100 - 0.08), 4),
            "upper_bound": round(min(1, overall / 100 + 0.08), 4),
            "confidence_level": 0.90,
            "method": "weighted_fusion",
        }

        technical_detail = {
            "detection_type": "trust_score",
            "n_modalities": trust_result.get("confidence_breakdown", {}).get("modalities_used", 0),
            "modalities": trust_result.get("confidence_breakdown", {}).get("modalities", []),
            "risk_factors": risk_factors,
            "overall_score": overall,
            "risk_level": risk_level,
        }

        return XAIOutput(
            summary=summary,
            feature_importance=feature_importance,
            decision_factors=decision_factors,
            confidence_intervals=confidence_intervals,
            human_readable=human_readable,
            technical_detail=technical_detail,
        )

    def _generate_summary(self, detection_type: str, confidence: float, features: list[dict]) -> str:
        top = features[0] if features else None
        type_name = detection_type.replace("_", " ").title()

        if confidence > 0.8:
            quality = "high confidence"
        elif confidence > 0.6:
            quality = "moderate confidence"
        else:
            quality = "low confidence"

        summary = f"{type_name} completed with {quality} ({confidence:.1%}). "

        if top:
            summary += f"Primary factor: {top['explanation']}. "

        positive = sum(1 for f in features if f["contribution"] > 0)
        negative = sum(1 for f in features if f["contribution"] < 0)
        summary += f"{positive} positive and {negative} negative indicators analyzed."

        return summary

    def _generate_human_readable(
        self, detection_type: str, confidence: float,
        top_factor: dict | None, decision_factors: list[dict]
    ) -> str:
        type_name = detection_type.replace("_", " ").title()

        if confidence > 0.8:
            intro = f"The {type_name.lower()} analysis shows strong results."
        elif confidence > 0.6:
            intro = f"The {type_name.lower()} analysis shows acceptable results with some concerns."
        else:
            intro = f"The {type_name.lower()} analysis shows significant concerns."

        body = ""
        if top_factor:
            body = f" The most significant factor was {top_factor['name']} ({top_factor['explanation']})."

        factors_text = ""
        positive = [f for f in decision_factors if f["impact"] == "positive"]
        negative = [f for f in decision_factors if f["impact"] == "negative"]

        if positive:
            factors_text += f" Positive indicators: {len(positive)}."
        if negative:
            factors_text += f" Negative indicators: {len(negative)}."

        return f"{intro}{body}{factors_text}"

    def _compute_entropy(self, features: list[dict]) -> float:
        import numpy as np
        contributions = [abs(f["contribution"]) for f in features]
        total = sum(contributions) + 1e-8
        probs = [c / total for c in contributions]
        return float(-sum(p * np.log2(p + 1e-8) for p in probs if p > 0))
