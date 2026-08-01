from dataclasses import dataclass


@dataclass
class Anomaly:
    type: str
    severity: str
    description: str
    confidence: float
    evidence: dict
    recommendation: str


class AnomalyEngine:
    """Detect anomalies from detection results and generate recommendations."""

    def __init__(self):
        self.thresholds = {
            "face_confidence": 0.70,
            "voice_confidence": 0.65,
            "lipsync_score": 0.60,
            "emotion_consistency": 0.55,
            "deepfake_threshold": 0.50,
            "noise_snr": 10,
            "av_offset_ms": 100,
        }

    def detect_anomalies(
        self,
        face_data: dict | None = None,
        voice_data: dict | None = None,
        lipsync_data: dict | None = None,
        emotion_data: dict | None = None,
    ) -> list[dict]:
        anomalies = []

        if face_data:
            anomalies.extend(self._check_face_anomalies(face_data))
        if voice_data:
            anomalies.extend(self._check_voice_anomalies(voice_data))
        if lipsync_data:
            anomalies.extend(self._check_lipsync_anomalies(lipsync_data))
        if emotion_data:
            anomalies.extend(self._check_emotion_anomalies(emotion_data))

        return anomalies

    def _check_face_anomalies(self, data: dict) -> list[dict]:
        anomalies = []
        confidence = data.get("confidence", 1.0)
        is_live = data.get("is_live", True)
        liveness = data.get("liveness_score", 1.0)
        deepfake = data.get("deepfake", {})
        face_count = data.get("face_count", 1)

        if confidence < self.thresholds["face_confidence"]:
            anomalies.append({
                "type": "Low Face Confidence",
                "severity": "high" if confidence < 0.5 else "medium",
                "description": f"Face detection confidence is {confidence:.1%}, below {self.thresholds['face_confidence']:.0%} threshold.",
                "confidence": round((1 - confidence) * 100, 1),
                "evidence": {"detected_confidence": confidence},
                "recommendation": "Request clearer image or re-capture with better lighting.",
            })

        if not is_live or (liveness is not None and liveness < self.thresholds["deepfake_threshold"]):
            anomalies.append({
                "type": "Potential Deepfake",
                "severity": "critical",
                "description": f"Liveness score {liveness:.1%} suggests non-live face (deepfake risk).",
                "confidence": round((1 - (liveness or 0)) * 100, 1),
                "evidence": {"liveness_score": liveness, "is_live": is_live},
                "recommendation": "Initiate liveness challenge or verify via alternate channel.",
            })

        if deepfake.get("is_deepfake"):
            anomalies.append({
                "type": "Deepfake Artifact Detected",
                "severity": "critical",
                "description": "Spectral analysis indicates synthetic face generation.",
                "confidence": round((1 - deepfake.get("authenticity_score", 0)) * 100, 1),
                "evidence": deepfake,
                "recommendation": "Block session and escalate to security team.",
            })

        if face_count > 1:
            anomalies.append({
                "type": "Multiple Faces Detected",
                "severity": "medium",
                "description": f"{face_count} faces detected in frame. Expected single face.",
                "confidence": 75.0,
                "evidence": {"face_count": face_count},
                "recommendation": "Verify participant identity and ensure single-person session.",
            })

        return anomalies

    def _check_voice_anomalies(self, data: dict) -> list[dict]:
        anomalies = []
        confidence = data.get("confidence", 1.0)
        is_live = data.get("is_live", True)
        noise = data.get("noise", {})
        snr = noise.get("snr_db", 30)
        speaker_count = data.get("speaker_count", 1)

        if confidence < self.thresholds["voice_confidence"]:
            anomalies.append({
                "type": "Low Voice Confidence",
                "severity": "high" if confidence < 0.5 else "medium",
                "description": f"Voice authenticity score {confidence:.1%} is below threshold.",
                "confidence": round((1 - confidence) * 100, 1),
                "evidence": {"voice_confidence": confidence},
                "recommendation": "Use secondary voice verification method.",
            })

        if not is_live:
            anomalies.append({
                "type": "Synthetic Voice Detected",
                "severity": "critical",
                "description": "Voice analysis indicates potential TTS or voice cloning.",
                "confidence": round((1 - confidence) * 100, 1),
                "evidence": {"is_live": is_live},
                "recommendation": "Request voice challenge or use alternate authentication.",
            })

        if snr < self.thresholds["noise_snr"]:
            anomalies.append({
                "type": "High Background Noise",
                "severity": "low",
                "description": f"SNR is {snr:.1f} dB, indicating noisy environment.",
                "confidence": round(min(50, (self.thresholds["noise_snr"] - snr) * 5), 1),
                "evidence": {"snr_db": snr},
                "recommendation": "Request quieter environment for accurate analysis.",
            })

        if speaker_count > 1:
            anomalies.append({
                "type": "Multiple Speakers",
                "severity": "medium",
                "description": f"{speaker_count} speakers detected. Expected single speaker.",
                "confidence": 70.0,
                "evidence": {"speaker_count": speaker_count},
                "recommendation": "Verify all participants are authorized.",
            })

        return anomalies

    def _check_lipsync_anomalies(self, data: dict) -> list[dict]:
        anomalies = []
        sync_score = data.get("sync_score", 1.0)
        offset = abs(data.get("audio_visual_offset", 0))

        if sync_score < self.thresholds["lipsync_score"]:
            anomalies.append({
                "type": "Lip-Sync Mismatch",
                "severity": "high" if sync_score < 0.4 else "medium",
                "description": f"Lip-sync score {sync_score:.1%} indicates audio-visual desync.",
                "confidence": round((1 - sync_score) * 100, 1),
                "evidence": {"sync_score": sync_score},
                "recommendation": "Check for video relay attacks or stream injection.",
            })

        if offset * 1000 > self.thresholds["av_offset_ms"]:
            anomalies.append({
                "type": "Audio-Visual Drift",
                "severity": "medium",
                "description": f"A/V offset is {offset*1000:.0f}ms, exceeding {self.thresholds['av_offset_ms']}ms threshold.",
                "confidence": round(min(80, offset * 500), 1),
                "evidence": {"offset_ms": offset * 1000},
                "recommendation": "Investigate stream integrity and synchronization.",
            })

        return anomalies

    def _check_emotion_anomalies(self, data: dict) -> list[dict]:
        anomalies = []
        consistency = data.get("consistency_score", 1.0)
        dominant = data.get("dominant_emotion", "neutral")
        micro = data.get("micro_expressions", [])

        if consistency < self.thresholds["emotion_consistency"]:
            anomalies.append({
                "type": "Emotion Inconsistency",
                "severity": "medium",
                "description": f"Emotion consistency {consistency:.1%} suggests unnatural behavior.",
                "confidence": round((1 - consistency) * 100, 1),
                "evidence": {"consistency_score": consistency},
                "recommendation": "Review session for signs of impersonation.",
            })

        if len(micro) > 3:
            anomalies.append({
                "type": "Frequent Micro-Expressions",
                "severity": "medium",
                "description": f"{len(micro)} micro-expressions detected. Unusually high.",
                "confidence": 65.0,
                "evidence": {"micro_expression_count": len(micro)},
                "recommendation": "Analyze for stress indicators or deception patterns.",
            })

        if dominant in ["fearful", "angry"] and consistency > 0.8:
            anomalies.append({
                "type": "Sustained Negative Emotion",
                "severity": "low",
                "description": f"Sustained {dominant} emotion with high consistency.",
                "confidence": 55.0,
                "evidence": {"dominant_emotion": dominant, "consistency": consistency},
                "recommendation": "Monitor for escalation or security threat indicators.",
            })

        return anomalies

    def generate_recommendations(
        self,
        scores: dict,
        anomalies: list[dict],
    ) -> list[dict]:
        recs = []

        overall = scores.get("overall", 50)
        if overall < 40:
            recs.append({
                "title": "IMMEDIATE: Manual Verification Required",
                "description": "Overall trust score critically low. All detections indicate high risk.",
                "action": "Halt automated processes. Require in-person or secondary biometric verification.",
                "priority": "critical",
            })
        elif overall < 60:
            recs.append({
                "title": "Enhanced Verification Recommended",
                "description": "Trust score below acceptable threshold.",
                "action": "Request additional verification factors before proceeding.",
                "priority": "high",
            })
        elif overall < 80:
            recs.append({
                "title": "Monitor Session",
                "description": "Trust score acceptable but below optimal.",
                "action": "Continue monitoring. Flag for review if score drops.",
                "priority": "medium",
            })

        critical_anomalies = [a for a in anomalies if a.get("severity") == "critical"]
        if critical_anomalies:
            recs.append({
                "title": f"Address {len(critical_anomalies)} Critical Alert(s)",
                "description": "Critical security anomalies require immediate attention.",
                "action": "Isolate session, preserve evidence, and escalate to SOC team.",
                "priority": "critical",
            })

        if scores.get("face", 100) < 60:
            recs.append({
                "title": "Face Verification Escalation",
                "description": "Face biometrics failed validation.",
                "action": "Switch to liveness challenge with randomized prompts.",
                "priority": "high",
            })

        if scores.get("voice", 100) < 60:
            recs.append({
                "title": "Voice Authentication Review",
                "description": "Voice analysis failed validation.",
                "action": "Use passphrase challenge or verify via alternate channel.",
                "priority": "high",
            })

        if scores.get("lipsync", 100) < 50:
            recs.append({
                "title": "Anti-Spoofing Investigation",
                "description": "Lip-sync analysis suggests video manipulation.",
                "action": "Check for video injection, relay attacks, or deepfake overlays.",
                "priority": "high",
            })

        if not recs:
            recs.append({
                "title": "All Systems Normal",
                "description": "No significant security concerns detected.",
                "action": "Continue standard monitoring protocols.",
                "priority": "low",
            })

        return recs
