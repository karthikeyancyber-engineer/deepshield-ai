import cv2
import numpy as np
import base64
import struct
from dataclasses import dataclass
from app.ai_engine.base import Timer, normalize


@dataclass
class LipSyncResult:
    confidence: float
    sync_score: float
    audio_visual_offset: float
    frame_analysis: dict
    mouth_tracking: dict
    correlation_metrics: dict
    explanations: list[dict]
    latency_ms: float


class LipSyncAnalyzer:
    """
    Lip-sync verification using audio envelope correlation
    with mouth movement detection via OpenCV.
    """

    def __init__(self, sample_rate: int = 16000, fps: float = 30.0):
        self.sample_rate = sample_rate
        self.fps = fps
        self.mouth_landmark_ids = [
            61, 146, 91, 181, 84, 17, 314, 405,
            321, 375, 291, 409, 270, 269, 267, 0,
            37, 39, 40, 185,
        ]

    def _decode_video_frames(self, video_data: str, max_frames: int = 90) -> list[np.ndarray]:
        raw = base64.b64decode(video_data)
        tmp_path = "/tmp/_lipsync_temp.mp4"
        with open(tmp_path, "wb") as f:
            f.write(raw)

        cap = cv2.VideoCapture(tmp_path)
        frames = []
        while cap.isOpened() and len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        return frames

    def _decode_audio(self, audio_data: str) -> np.ndarray:
        raw = base64.b64decode(audio_data)
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        return samples

    def _compute_audio_envelope(self, audio: np.ndarray, frame_size: int) -> np.ndarray:
        n_frames = len(audio) // frame_size
        envelope = np.zeros(n_frames)
        for i in range(n_frames):
            chunk = audio[i * frame_size:(i + 1) * frame_size]
            envelope[i] = np.sqrt(np.mean(chunk ** 2))
        return envelope

    def _detect_mouth_opening(self, frame: np.ndarray) -> float:
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
        ) as face_mesh:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return 0.0

            landmarks = results.multi_face_landmarks[0]
            h, w = frame.shape[:2]

            upper_lip = landmarks.landmark[13]
            lower_lip = landmarks.landmark[14]

            mouth_height = abs(upper_lip.y - lower_lip.y)
            return float(mouth_height)

    def _detect_mouth_opening_simple(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        roi = gray[int(h * 0.55):int(h * 0.75), int(w * 0.35):int(w * 0.65)]
        if roi.size == 0:
            return 0.0

        edges = cv2.Canny(roi, 30, 100)
        edge_density = np.sum(edges > 0) / (edges.size + 1e-8)

        _, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        dark_ratio = np.sum(thresh < 128) / (thresh.size + 1e-8)

        return float(edge_density * dark_ratio)

    def _normalize_envelope(self, envelope: np.ndarray) -> np.ndarray:
        min_val = np.min(envelope)
        max_val = np.max(envelope)
        return (envelope - min_val) / (max_val - min_val + 1e-8)

    def _compute_cross_correlation(self, audio_env: np.ndarray, mouth_env: np.ndarray) -> dict:
        min_len = min(len(audio_env), len(mouth_env))
        a = audio_env[:min_len]
        m = mouth_env[:min_len]

        a = (a - np.mean(a)) / (np.std(a) + 1e-8)
        m = (m - np.mean(m)) / (np.std(m) + 1e-8)

        correlation = np.correlate(a, m, mode='full')
        correlation = correlation / (min_len)

        zero_lag_idx = min_len - 1
        peak_idx = np.argmax(np.abs(correlation))
        offset_frames = peak_idx - zero_lag_idx
        offset_seconds = offset_frames / self.fps

        peak_correlation = float(correlation[peak_idx])

        window_size = max(1, min_len // 10)
        local_corrs = []
        for i in range(0, min_len - window_size, window_size):
            local_a = a[i:i + window_size]
            local_m = m[i:i + window_size]
            if np.std(local_a) > 0 and np.std(local_m) > 0:
                local_corr = float(np.corrcoef(local_a, local_m)[0, 1])
                local_corrs.append(local_corr)

        consistency = float(np.std(local_corrs)) if local_corrs else 1.0

        return {
            "peak_correlation": round(peak_correlation, 4),
            "offset_seconds": round(offset_seconds, 4),
            "offset_frames": int(offset_frames),
            "consistency_std": round(consistency, 4),
            "local_correlations": [round(c, 4) for c in local_corrs[:20]],
        }

    def _compute_sync_score(self, correlation: dict, mouth_movement: float) -> tuple[float, list[dict]]:
        explanations = []

        corr_score = normalize(correlation["peak_correlation"], 0.1, 0.8)
        explanations.append({
            "feature": "peak_correlation",
            "value": correlation["peak_correlation"],
            "weight": 0.4,
            "contribution": corr_score * 0.4,
            "explanation": f"Audio-mouth correlation: {correlation['peak_correlation']:.3f} — {'Strong sync' if corr_score > 0.6 else 'Weak sync'}",
        })

        offset = abs(correlation["offset_seconds"])
        offset_score = normalize(offset, 0.15, 0.0)
        explanations.append({
            "feature": "av_offset",
            "value": correlation["offset_seconds"],
            "weight": 0.3,
            "contribution": offset_score * 0.3,
            "explanation": f"A/V offset: {correlation['offset_seconds']*1000:.1f}ms — {'Synced' if offset < 0.05 else 'Drift detected'}",
        })

        consistency_score = normalize(correlation["consistency_std"], 0.5, 0.0)
        explanations.append({
            "feature": "sync_consistency",
            "value": correlation["consistency_std"],
            "weight": 0.2,
            "contribution": consistency_score * 0.2,
            "explanation": f"Sync stability: {1-correlation['consistency_std']:.1%} — {'Consistent' if consistency_score > 0.5 else 'Variable sync'}",
        })

        movement_score = normalize(mouth_movement, 0.01, 0.15)
        explanations.append({
            "feature": "mouth_movement",
            "value": mouth_movement,
            "weight": 0.1,
            "contribution": movement_score * 0.1,
            "explanation": f"Mouth aperture: {mouth_movement:.4f} — {'Active speech' if movement_score > 0.3 else 'Minimal movement'}",
        })

        total = corr_score * 0.4 + offset_score * 0.3 + consistency_score * 0.2 + movement_score * 0.1
        return round(total, 4), explanations

    def analyze(
        self, video_data: str, audio_data: str, frame_rate: float = 30.0
    ) -> LipSyncResult:
        self.fps = frame_rate
        with Timer() as timer:
            frames = self._decode_video_frames(video_data)
            audio = self._decode_audio(audio_data)

            if not frames:
                raise ValueError("No video frames extracted")

            samples_per_frame = int(self.sample_rate / self.fps)
            audio_env = self._compute_audio_envelope(audio, samples_per_frame)
            audio_env_norm = self._normalize_envelope(audio_env)

            mouth_movements = []
            for frame in frames:
                movement = self._detect_mouth_opening_simple(frame)
                mouth_movements.append(movement)

            mouth_env = np.array(mouth_movements)
            mouth_env_norm = self._normalize_envelope(mouth_env)

            correlation = self._compute_cross_correlation(audio_env_norm, mouth_env_norm)

            sync_score, explanations = self._compute_sync_score(
                correlation, float(np.mean(mouth_movements))
            )

            frame_analysis = {
                "total_frames": len(frames),
                "analyzed_frames": len(mouth_movements),
                "mean_mouth_opening": round(float(np.mean(mouth_movements)), 6),
                "std_mouth_opening": round(float(np.std(mouth_movements)), 6),
                "peak_mouth_opening": round(float(np.max(mouth_movements)), 6),
            }

            mouth_tracking = {
                "movement_signal": [round(float(m), 6) for m in mouth_env_norm[:30]],
                "audio_envelope": [round(float(a), 6) for a in audio_env_norm[:30]],
                "peak_correlation": correlation["peak_correlation"],
            }

        return LipSyncResult(
            confidence=round(1.0 - abs(sync_score - 0.5) * 2, 4),
            sync_score=sync_score,
            audio_visual_offset=correlation["offset_seconds"],
            frame_analysis=frame_analysis,
            mouth_tracking=mouth_tracking,
            correlation_metrics=correlation,
            explanations=explanations,
            latency_ms=round(timer.elapsed_ms, 2),
        )
