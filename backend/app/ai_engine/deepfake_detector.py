import cv2
import numpy as np
from dataclasses import dataclass
from app.ai_engine.base import AIDetection, Timer, normalize


@dataclass
class DeepfakeResult:
    is_deepfake: bool
    confidence: float
    authenticity_score: float
    analysis_breakdown: dict
    visual_artifacts: list[dict]
    frequency_analysis: dict
    temporal_consistency: dict
    explanations: list[dict]
    latency_ms: float


class DeepfakeDetector:
    """
    Lightweight deepfake detection using spectral analysis,
    compression artifact detection, and frequency domain features.
    """

    def __init__(self):
        self.dct_block_size = 8
        self.noise_threshold = 0.15
        self.artifact_threshold = 0.3

    def _decode_image(self, image_data: str) -> np.ndarray:
        import base64
        raw = base64.b64decode(image_data)
        arr = np.frombuffer(raw, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
        return img

    def _compute_dct_features(self, gray: np.ndarray) -> dict:
        h, w = gray.shape
        h_pad = (h // self.dct_block_size) * self.dct_block_size
        w_pad = (w // self.dct_block_size) * self.dct_block_size
        roi = gray[:h_pad, :w_pad].astype(np.float32)

        blocks = []
        for i in range(0, h_pad, self.dct_block_size):
            for j in range(0, w_pad, self.dct_block_size):
                block = roi[i:i + self.dct_block_size, j:j + self.dct_block_size]
                dct_block = cv2.dct(block)
                blocks.append(dct_block)

        if not blocks:
            return {"mean_high_freq": 0, "std_high_freq": 0, "ratio": 0}

        blocks_arr = np.array(blocks)
        high_freq = blocks_arr[:, 4:, 4:].reshape(len(blocks), -1)
        low_freq = blocks_arr[:, :4, :4].reshape(len(blocks), -1)

        mean_hf = float(np.mean(np.abs(high_freq)))
        mean_lf = float(np.mean(np.abs(low_freq)))
        std_hf = float(np.std(np.abs(high_freq)))
        ratio = mean_hf / (mean_lf + 1e-8)

        return {
            "mean_high_freq": round(mean_hf, 6),
            "std_high_freq": round(std_hf, 6),
            "low_freq_energy": round(mean_lf, 6),
            "frequency_ratio": round(ratio, 6),
        }

    def _detect_noise_patterns(self, gray: np.ndarray) -> dict:
        denoised = cv2.GaussianBlur(gray, (5, 5), 0.5)
        noise = cv2.absdiff(gray, denoised).astype(np.float64)

        noise_mean = float(np.mean(noise))
        noise_std = float(np.std(noise))
        noise_entropy = float(self._compute_noise_entropy(noise))

        noise_map = (noise / (noise.max() + 1e-8) * 255).astype(np.uint8)
        _, binary = cv2.threshold(noise_map, 30, 255, cv2.THRESH_BINARY)
        noise_regularity = float(np.sum(binary > 0) / (binary.size + 1e-8))

        return {
            "noise_mean": round(noise_mean, 4),
            "noise_std": round(noise_std, 4),
            "noise_entropy": round(noise_entropy, 4),
            "noise_regularity": round(noise_regularity, 4),
        }

    def _compute_noise_entropy(self, noise: np.ndarray) -> float:
        hist, _ = np.histogram(noise.flatten(), bins=256, range=(0, 256))
        hist = hist.astype(float)
        hist = hist[hist > 0]
        hist = hist / hist.sum()
        return float(-np.sum(hist * np.log2(hist + 1e-8)))

    def _detect_compression_artifacts(self, image: np.ndarray) -> dict:
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)

        blocks_y = []
        h, w = y_channel.shape
        for i in range(0, h - 8, 8):
            for j in range(0, w - 8, 8):
                block = y_channel[i:i + 8, j:j + 8]
                dct = cv2.dct(block)
                zigzag = self._zigzag(dct)
                blocks_y.append(zigzag)

        if not blocks_y:
            return {"blocking_score": 0, "ringing_score": 0}

        blocks_arr = np.array(blocks_y)
        ac_coeffs = blocks_arr[:, 1:]

        blocking_score = float(np.mean(np.abs(np.diff(ac_coeffs[:, :8], axis=0))))
        ringing_score = float(np.std(ac_coeffs[:, -8:]))

        return {
            "blocking_score": round(blocking_score, 6),
            "ringing_score": round(ringing_score, 6),
        }

    def _zigzag(self, block: np.ndarray) -> np.ndarray:
        indices = np.array([
            [0, 0], [0, 1], [1, 0], [2, 0], [1, 1], [0, 2], [0, 3], [1, 2],
            [2, 1], [3, 0], [4, 0], [3, 1], [2, 2], [1, 3], [0, 4], [0, 5],
        ])
        result = []
        for i, j in indices:
            if i < block.shape[0] and j < block.shape[1]:
                result.append(block[i, j])
        return np.array(result)

    def _analyze_color_consistency(self, image: np.ndarray) -> dict:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h_channel = hsv[:, :, 0].astype(float)
        s_channel = hsv[:, :, 1].astype(float)

        h_hist, _ = np.histogram(h_channel, bins=180, range=(0, 180))
        s_hist, _ = np.histogram(s_channel, bins=256, range=(0, 256))

        h_entropy = float(-np.sum((h_hist / (h_hist.sum() + 1e-8)) * np.log2(h_hist / (h_hist.sum() + 1e-8) + 1e-8)))
        s_entropy = float(-np.sum((s_hist / (s_hist.sum() + 1e-8)) * np.log2(s_hist / (s_hist.sum() + 1e-8) + 1e-8)))

        skin_mask = cv2.inRange(hsv, (0, 20, 70), (25, 150, 255))
        skin_ratio = float(np.sum(skin_mask > 0) / (skin_mask.size + 1e-8))

        return {
            "hue_entropy": round(h_entropy, 4),
            "sat_entropy": round(s_entropy, 4),
            "skin_ratio": round(skin_ratio, 4),
        }

    def _compute_authenticity_score(
        self, dct_features: dict, noise: dict, compression: dict, color: dict
    ) -> tuple[float, list[dict]]:
        scores = []
        weights = []
        explanations = []

        dct_score = normalize(dct_features["frequency_ratio"], 0.05, 0.5)
        scores.append(dct_score)
        weights.append(0.25)
        explanations.append({
            "feature": "frequency_ratio",
            "value": dct_features["frequency_ratio"],
            "weight": 0.25,
            "contribution": dct_score * 0.25,
            "explanation": f"Spectral ratio: {dct_features['frequency_ratio']:.4f} — {'Natural' if dct_score > 0.5 else 'Suspicious'}",
        })

        noise_score = normalize(noise["noise_entropy"], 4.0, 7.5)
        scores.append(noise_score)
        weights.append(0.25)
        explanations.append({
            "feature": "noise_entropy",
            "value": noise["noise_entropy"],
            "weight": 0.25,
            "contribution": noise_score * 0.25,
            "explanation": f"Noise entropy: {noise['noise_entropy']:.2f} — {'Consistent with real camera' if noise_score > 0.5 else 'Anomalous noise pattern'}",
        })

        block_score = 1.0 - normalize(compression["blocking_score"], 0, 50)
        scores.append(block_score)
        weights.append(0.25)
        explanations.append({
            "feature": "blocking_artifacts",
            "value": compression["blocking_score"],
            "weight": 0.25,
            "contribution": block_score * 0.25,
            "explanation": f"Compression artifacts: {compression['blocking_score']:.6f} — {'Natural JPEG' if block_score > 0.5 else 'Potential manipulation'}",
        })

        color_score = normalize(color["hue_entropy"], 2.0, 6.0)
        scores.append(color_score)
        weights.append(0.25)
        explanations.append({
            "feature": "color_consistency",
            "value": color["hue_entropy"],
            "weight": 0.25,
            "contribution": color_score * 0.25,
            "explanation": f"Color entropy: {color['hue_entropy']:.2f} — {'Natural distribution' if color_score > 0.5 else 'Unusual color pattern'}",
        })

        total = sum(s * w for s, w in zip(scores, weights))
        return round(total, 4), explanations

    def detect(self, image_data: str) -> DeepfakeResult:
        with Timer() as timer:
            image = self._decode_image(image_data)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            dct_features = self._compute_dct_features(gray)
            noise = self._detect_noise_patterns(gray)
            compression = self._detect_compression_artifacts(image)
            color = self._analyze_color_consistency(image)

            authenticity_score, explanations = self._compute_authenticity_score(
                dct_features, noise, compression, color
            )

            visual_artifacts = []
            if noise["noise_regularity"] > 0.3:
                visual_artifacts.append({
                    "type": "noise_regularity",
                    "severity": "medium",
                    "description": "Unusually regular noise pattern detected",
                })
            if compression["blocking_score"] > 30:
                visual_artifacts.append({
                    "type": "blocking_artifacts",
                    "severity": "low",
                    "description": "Strong blocking artifacts suggest re-compression",
                })
            if color["skin_ratio"] > 0.6:
                visual_artifacts.append({
                    "type": "skin_consistency",
                    "severity": "low",
                    "description": "Unusually uniform skin tone distribution",
                })

            frequency_analysis = {
                "dct": dct_features,
                "noise": noise,
                "compression": compression,
            }

            temporal_consistency = {
                "frame_count": 1,
                "consistency_score": authenticity_score,
                "variation": 0.0,
            }

        return DeepfakeResult(
            is_deepfake=authenticity_score < 0.5,
            confidence=round(1.0 - abs(authenticity_score - 0.5) * 2, 4),
            authenticity_score=authenticity_score,
            analysis_breakdown={
                "dct_features": dct_features,
                "noise_patterns": noise,
                "compression_artifacts": compression,
                "color_analysis": color,
            },
            visual_artifacts=visual_artifacts,
            frequency_analysis=frequency_analysis,
            temporal_consistency=temporal_consistency,
            explanations=explanations,
            latency_ms=round(timer.elapsed_ms, 2),
        )
