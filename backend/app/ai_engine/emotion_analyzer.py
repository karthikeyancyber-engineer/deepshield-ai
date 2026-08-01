import cv2
import numpy as np
import base64
from dataclasses import dataclass
from app.ai_engine.base import Timer, normalize, exponential_moving_average


EMOTION_LABELS = ["angry", "disgusted", "fearful", "happy", "sad", "surprised", "neutral"]


@dataclass
class EmotionAnalysisResult:
    confidence: float
    dominant_emotion: str
    emotion_scores: dict
    consistency_score: float
    temporal_analysis: dict
    micro_expressions: list[dict]
    valence_arousal: dict
    explanations: list[dict]
    latency_ms: float


class EmotionAnalyzer:
    """
    Facial emotion recognition with temporal consistency analysis
    using skin color segmentation, geometric features, and
    histogram-based emotion classification.
    """

    def __init__(self):
        self.emotion_templates = self._build_emotion_templates()
        self.history_window = 15

    def _build_emotion_templates(self) -> dict:
        return {
            "happy": {
                "mouth_width_ratio": (1.2, 2.0),
                "mouth_height_ratio": (0.6, 1.5),
                "eye_openness_ratio": (0.8, 1.3),
                "eyebrow_position": (0.3, 0.7),
            },
            "sad": {
                "mouth_width_ratio": (0.4, 0.9),
                "mouth_height_ratio": (0.2, 0.6),
                "eye_openness_ratio": (0.5, 0.9),
                "eyebrow_position": (0.6, 1.0),
            },
            "angry": {
                "mouth_width_ratio": (0.8, 1.4),
                "mouth_height_ratio": (0.3, 0.8),
                "eye_openness_ratio": (0.6, 1.0),
                "eyebrow_position": (0.1, 0.4),
            },
            "surprised": {
                "mouth_width_ratio": (0.7, 1.2),
                "mouth_height_ratio": (1.0, 2.0),
                "eye_openness_ratio": (1.2, 1.8),
                "eyebrow_position": (0.0, 0.3),
            },
            "fearful": {
                "mouth_width_ratio": (0.7, 1.1),
                "mouth_height_ratio": (0.5, 1.0),
                "eye_openness_ratio": (1.1, 1.6),
                "eyebrow_position": (0.1, 0.4),
            },
            "disgusted": {
                "mouth_width_ratio": (0.6, 1.0),
                "mouth_height_ratio": (0.4, 0.9),
                "eye_openness_ratio": (0.5, 0.9),
                "eyebrow_position": (0.3, 0.6),
            },
            "neutral": {
                "mouth_width_ratio": (0.8, 1.2),
                "mouth_height_ratio": (0.3, 0.6),
                "eye_openness_ratio": (0.8, 1.2),
                "eyebrow_position": (0.4, 0.7),
            },
        }

    def _decode_image(self, image_data: str) -> np.ndarray:
        raw = base64.b64decode(image_data)
        arr = np.frombuffer(raw, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
        return img

    def _extract_geometric_features(self, frame: np.ndarray) -> dict:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))

        if len(faces) == 0:
            return self._default_features()

        x, y, fw, fh = faces[0]
        face_roi = gray[y:y + fh, x:x + fw]

        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        eyes = eye_cascade.detectMultiScale(face_roi, 1.1, 4, minSize=(20, 20))

        mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
        mouths = mouth_cascade.detectMultiScale(face_roi, 1.7, 20)

        eye_openness = 0.0
        if len(eyes) >= 2:
            eye1_h = eyes[0][3] / (eyes[0][2] + 1e-8)
            eye2_h = eyes[1][3] / (eyes[1][2] + 1e-8)
            eye_openness = (eye1_h + eye2_h) / 2

        mouth_width = 0.0
        mouth_height = 0.0
        if len(mouths) > 0:
            mw, mh = mouths[0][2], mouths[0][3]
            mouth_width = mw / (fw + 1e-8)
            mouth_height = mh / (fh + 1e-8)

        eyebrow_y = y + int(fh * 0.2)
        forehead_roi = gray[max(0,eyrow_y-10):eyrow_y+10, x:x+fw]
        eyebrow_texture = float(np.std(forehead_roi)) / 255.0 if forehead_roi.size > 0 else 0.5

        edge_density = float(np.mean(cv2.Canny(face_roi, 50, 150))) / 255.0

        return {
            "face_detected": True,
            "face_bbox": {"x": int(x), "y": int(y), "w": int(fw), "h": int(fh)},
            "eye_openness": round(float(eye_openness), 4),
            "mouth_width_ratio": round(float(mouth_width), 4),
            "mouth_height_ratio": round(float(mouth_height), 4),
            "eyebrow_position": round(float(eyebrow_texture), 4),
            "edge_density": round(float(edge_density), 4),
            "face_symmetry": self._compute_symmetry(face_roi),
        }

    def _default_features(self) -> dict:
        return {
            "face_detected": False,
            "face_bbox": None,
            "eye_openness": 0.0,
            "mouth_width_ratio": 0.0,
            "mouth_height_ratio": 0.0,
            "eyebrow_position": 0.5,
            "edge_density": 0.0,
            "face_symmetry": 0.5,
        }

    def _compute_symmetry(self, face_gray: np.ndarray) -> float:
        h, w = face_gray.shape
        left = face_gray[:, :w // 2]
        right = cv2.flip(face_gray[:, w // 2:], 1)
        min_w = min(left.shape[1], right.shape[1])
        if min_w == 0:
            return 0.5
        diff = np.abs(left[:, :min_w].astype(float) - right[:, :min_w].astype(float))
        return round(1.0 - float(np.mean(diff)) / 255.0, 4)

    def _classify_emotion(self, features: dict) -> dict:
        scores = {}
        for emotion, template in self.emotion_templates.items():
            match_score = 0.0
            n_features = 0

            for feature_name, (low, high) in template.items():
                value = features.get(feature_name, 0.5)
                if low <= value <= high:
                    match_score += 1.0
                else:
                    dist = min(abs(value - low), abs(value - high))
                    match_score += max(0, 1.0 - dist * 2)
                n_features += 1

            scores[emotion] = match_score / (n_features + 1e-8)

        total = sum(scores.values()) + 1e-8
        normalized = {k: round(v / total, 4) for k, v in scores.items()}
        return normalized

    def _compute_consistency(self, emotion_history: list[dict]) -> float:
        if len(emotion_history) < 2:
            return 1.0

        dominant_sequence = [max(e, key=e.get) for e in emotion_history]
        transitions = sum(
            1 for i in range(1, len(dominant_sequence))
            if dominant_sequence[i] != dominant_sequence[i - 1]
        )
        transition_rate = transitions / (len(dominant_sequence) - 1)

        consistency = 1.0 - transition_rate * 0.5

        if len(emotion_history) >= 3:
            for emotion in EMOTION_LABELS:
                values = [e.get(emotion, 0) for e in emotion_history]
                ema = exponential_moving_average(values, 0.3)
                variance = np.var(ema[-3:]) if len(ema) >= 3 else 0
                if variance > 0.05:
                    consistency *= 0.95

        return round(max(0.0, min(1.0, consistency)), 4)

    def _detect_micro_expressions(self, emotion_history: list[dict]) -> list[dict]:
        micro_expressions = []
        if len(emotion_history) < 3:
            return micro_expressions

        dominant_sequence = [max(e, key=e.get) for e in emotion_history]
        for i in range(1, len(dominant_sequence) - 1):
            if (dominant_sequence[i] != dominant_sequence[i - 1] and
                dominant_sequence[i] != dominant_sequence[i + 1] and
                dominant_sequence[i] != "neutral"):
                micro_expressions.append({
                    "frame_index": i,
                    "emotion": dominant_sequence[i],
                    "duration_frames": 1,
                    "intensity": round(emotion_history[i].get(dominant_sequence[i], 0), 4),
                })

        return micro_expressions

    def _compute_valence_arousal(self, emotion_scores: dict) -> dict:
        valence = (
            emotion_scores.get("happy", 0) * 1.0 +
            emotion_scores.get("surprised", 0) * 0.5 +
            emotion_scores.get("neutral", 0) * 0.3 -
            emotion_scores.get("sad", 0) * 1.0 -
            emotion_scores.get("angry", 0) * 0.8 -
            emotion_scores.get("fearful", 0) * 0.7 -
            emotion_scores.get("disgusted", 0) * 0.6
        )

        arousal = (
            emotion_scores.get("angry", 0) * 1.0 +
            emotion_scores.get("fearful", 0) * 0.9 +
            emotion_scores.get("surprised", 0) * 0.8 +
            emotion_scores.get("happy", 0) * 0.6 -
            emotion_scores.get("sad", 0) * 0.5 -
            emotion_scores.get("neutral", 0) * 0.3 -
            emotion_scores.get("disgusted", 0) * 0.2
        )

        return {
            "valence": round(float(np.clip(valence, -1, 1)), 4),
            "arousal": round(float(np.clip(arousal, -1, 1)), 4),
            "quadrant": self._get_quadrant(valence, arousal),
        }

    def _get_quadrant(self, valence: float, arousal: float) -> str:
        if valence >= 0 and arousal >= 0:
            return "positive_high_energy"
        elif valence >= 0 and arousal < 0:
            return "positive_low_energy"
        elif valence < 0 and arousal >= 0:
            return "negative_high_energy"
        return "negative_low_energy"

    def analyze(
        self, image_data: str, emotion_history: list[dict] | None = None
    ) -> EmotionAnalysisResult:
        with Timer() as timer:
            image = self._decode_image(image_data)
            features = self._extract_geometric_features(image)

            if not features["face_detected"]:
                return EmotionAnalysisResult(
                    confidence=0.0,
                    dominant_emotion="unknown",
                    emotion_scores={e: 0.0 for e in EMOTION_LABELS},
                    consistency_score=0.0,
                    temporal_analysis={"frame_count": 0, "transitions": 0},
                    micro_expressions=[],
                    valence_arousal={"valence": 0, "arousal": 0, "quadrant": "unknown"},
                    explanations=[{"feature": "face_detection", "value": False, "weight": 1.0, "contribution": 0, "explanation": "No face detected in image"}],
                    latency_ms=round(timer.elapsed_ms, 2),
                )

            emotion_scores = self._classify_emotion(features)
            dominant = max(emotion_scores, key=emotion_scores.get)

            all_history = list(emotion_history or [])
            all_history.append(emotion_scores)
            consistency = self._compute_consistency(all_history)

            micro_expressions = self._detect_micro_expressions(all_history)
            valence_arousal = self._compute_valence_arousal(emotion_scores)

            temporal = {
                "frame_count": len(all_history),
                "dominant_sequence": [max(e, key=e.get) for e in all_history[-5:]],
                "transitions": sum(
                    1 for i in range(1, len(all_history))
                    if max(all_history[i], key=all_history[i].get) != max(all_history[i-1], key=all_history[i-1].get)
                ),
                "consistency": consistency,
            }

            explanations = []
            for emotion, score in sorted(emotion_scores.items(), key=lambda x: -x[1]):
                explanations.append({
                    "feature": f"emotion_{emotion}",
                    "value": score,
                    "weight": 1.0 / len(EMOTION_LABELS),
                    "contribution": score / len(EMOTION_LABELS),
                    "explanation": f"{emotion}: {score:.1%} {'(dominant)' if emotion == dominant else ''}",
                })

            explanations.append({
                "feature": "temporal_consistency",
                "value": consistency,
                "weight": 0.2,
                "contribution": consistency * 0.2,
                "explanation": f"Emotion stability: {consistency:.1%} — {'Consistent' if consistency > 0.7 else 'Volatile'}",
            })

        return EmotionAnalysisResult(
            confidence=round(float(emotion_scores[dominant]), 4),
            dominant_emotion=dominant,
            emotion_scores=emotion_scores,
            consistency_score=consistency,
            temporal_analysis=temporal,
            micro_expressions=micro_expressions,
            valence_arousal=valence_arousal,
            explanations=explanations,
            latency_ms=round(timer.elapsed_ms, 2),
        )
