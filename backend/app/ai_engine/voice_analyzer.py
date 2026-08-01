import io
import struct
import numpy as np
from dataclasses import dataclass
from app.ai_engine.base import Timer, normalize


@dataclass
class VoiceAnalysisResult:
    is_live: bool
    confidence: float
    authenticity_score: float
    speaker_count: int
    speaker_id: str | None
    spectral_features: dict
    prosody_features: dict
    noise_analysis: dict
    audio_quality: dict
    explanations: list[dict]
    latency_ms: float


class VoiceAnalyzer:
    """
    Real-time voice authenticity detection using spectral analysis,
    prosody features, and anti-spoofing heuristics.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frame_length = 0.025
        self.frame_shift = 0.010
        self.n_fft = 512
        self.n_mels = 40
        self.n_mfcc = 13

    def _decode_audio(self, audio_data: str) -> np.ndarray:
        import base64
        raw = base64.b64decode(audio_data)
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        return samples

    def _pre_emphasis(self, signal: np.ndarray, coeff: float = 0.97) -> np.ndarray:
        return np.append(signal[0], signal[1:] - coeff * signal[:-1])

    def _compute_mel_filterbank(self) -> np.ndarray:
        low_freq_mel = 0
        high_freq_mel = 2595 * np.log10(1 + (self.sample_rate / 2) / 700)
        mel_points = np.linspace(low_freq_mel, high_freq_mel, self.n_mels + 2)
        hz_points = 700 * (10 ** (mel_points / 2595) - 1)
        bin_points = np.floor((self.n_fft + 1) * hz_points / self.sample_rate).astype(int)

        filters = np.zeros((self.n_mels, self.n_fft // 2 + 1))
        for i in range(1, self.n_mels + 1):
            left = bin_points[i - 1]
            center = bin_points[i]
            right = bin_points[i + 1]
            for j in range(left, center):
                if center != left:
                    filters[i - 1, j] = (j - left) / (center - left)
            for j in range(center, right):
                if right != center:
                    filters[i - 1, j] = (right - j) / (right - center)
        return filters

    def _compute_mfcc(self, signal: np.ndarray) -> np.ndarray:
        emphasized = self._pre_emphasis(signal)
        frame_size = int(self.frame_length * self.sample_rate)
        frame_shift_size = int(self.frame_shift * self.sample_rate)
        n_frames = 1 + (len(emphasized) - frame_size) // frame_shift_size

        frames = np.zeros((n_frames, frame_size))
        windowed = np.zeros((n_frames, frame_size))
        for i in range(n_frames):
            start = i * frame_shift_size
            frames[i] = emphasized[start:start + frame_size]
            windowed[i] = frames[i] * np.hamming(frame_size)

        mag_frames = np.abs(np.fft.rfft(windowed, self.n_fft))
        pow_frames = (mag_frames ** 2) / self.n_fft

        mel_filters = self._compute_mel_filterbank()
        mel_spec = np.dot(pow_frames, mel_filters.T)
        mel_spec = np.where(mel_spec == 0, np.finfo(float).eps, mel_spec)
        log_mel = np.log(mel_spec)

        mfcc = np.zeros((n_frames, self.n_mfcc))
        for i in range(n_frames):
            for j in range(self.n_mfcc):
                mfcc[i, j] = np.sum(log_mel[i] * np.cos(np.pi * j * np.arange(self.n_mels) / self.n_mels))

        return mfcc

    def _compute_fundamental_freq(self, signal: np.ndarray) -> dict:
        min_lag = int(self.sample_rate / 500)
        max_lag = int(self.sample_rate / 50)
        autocorr = np.correlate(signal, signal, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        autocorr = autocorr / (autocorr[0] + 1e-8)

        search_range = autocorr[min_lag:max_lag]
        if len(search_range) == 0:
            return {"f0_mean": 0, "f0_std": 0, "f0_range": 0}

        peak_idx = np.argmax(search_range) + min_lag
        f0 = self.sample_rate / peak_idx

        return {
            "f0_mean": round(float(f0), 2),
            "f0_std": round(float(np.std(autocorr[min_lag:max_lag]) * 50), 2),
            "f0_range": round(float(f0 * 0.1), 2),
        }

    def _compute_spectral_features(self, signal: np.ndarray) -> dict:
        emphasized = self._pre_emphasis(signal)
        frame_size = int(self.frame_length * self.sample_rate)
        frame_shift_size = int(self.frame_shift * self.sample_rate)
        n_frames = 1 + (len(emphasized) - frame_size) // frame_shift_size

        spectral_centroids = []
        spectral_rolloff = []
        spectral_bandwidth = []
        zcr = []

        for i in range(n_frames):
            start = i * frame_shift_size
            frame = emphasized[start:start + frame_size] * np.hamming(frame_size)
            mag = np.abs(np.fft.rfft(frame, self.n_fft))
            freqs = np.linspace(0, self.sample_rate / 2, len(mag))

            sc = np.sum(freqs * mag) / (np.sum(mag) + 1e-8)
            spectral_centroids.append(sc)

            cumsum = np.cumsum(mag)
            rolloff_idx = np.searchsorted(cumsum, 0.85 * cumsum[-1])
            spectral_rolloff.append(freqs[min(rolloff_idx, len(freqs) - 1)])

            mean_freq = np.sum(freqs * mag) / (np.sum(mag) + 1e-8)
            sb = np.sqrt(np.sum(((freqs - mean_freq) ** 2) * mag) / (np.sum(mag) + 1e-8))
            spectral_bandwidth.append(sb)

            signs = np.sign(frame)
            crossings = np.sum(np.abs(np.diff(signs)) > 0)
            zcr.append(crossings / len(frame))

        return {
            "spectral_centroid_mean": round(float(np.mean(spectral_centroids)), 2),
            "spectral_centroid_std": round(float(np.std(spectral_centroids)), 2),
            "spectral_rolloff_mean": round(float(np.mean(spectral_rolloff)), 2),
            "spectral_bandwidth_mean": round(float(np.mean(spectral_bandwidth)), 2),
            "zero_crossing_rate": round(float(np.mean(zcr)), 4),
        }

    def _compute_prosody(self, signal: np.ndarray) -> dict:
        frame_size = int(self.frame_length * self.sample_rate)
        frame_shift_size = int(self.frame_shift * self.sample_rate)
        n_frames = 1 + (len(signal) - frame_size) // frame_shift_size

        energy = []
        for i in range(n_frames):
            start = i * frame_shift_size
            frame = signal[start:start + frame_size]
            energy.append(float(np.sum(frame ** 2) / frame_size))

        energy = np.array(energy)
        energy_diff = np.diff(energy)

        return {
            "energy_mean": round(float(np.mean(energy)), 6),
            "energy_std": round(float(np.std(energy)), 6),
            "energy_range": round(float(np.max(energy) - np.min(energy)), 6),
            "energy_dynamics": round(float(np.std(energy_diff)), 6),
            "speech_rate_estimate": round(float(n_frames / (len(signal) / self.sample_rate)), 2),
        }

    def _analyze_noise(self, signal: np.ndarray) -> dict:
        frame_size = int(self.frame_length * self.sample_rate)
        frame_shift_size = int(self.frame_shift * self.sample_rate)
        n_frames = 1 + (len(signal) - frame_size) // frame_shift_size

        frame_energies = []
        for i in range(n_frames):
            start = i * frame_shift_size
            frame = signal[start:start + frame_size]
            frame_energies.append(float(np.sum(frame ** 2)))

        frame_energies = np.array(frame_energies)
        sorted_energies = np.sort(frame_energies)
        noise_floor = np.mean(sorted_energies[:max(1, len(sorted_energies) // 10)])
        snr = 10 * np.log10((np.mean(frame_energies) - noise_floor) / (noise_floor + 1e-8))

        return {
            "snr_db": round(float(snr), 2),
            "noise_floor": round(float(noise_floor), 8),
            "is_noisy": bool(snr < 10),
        }

    def _compute_authenticity(
        self, spectral: dict, prosody: dict, noise: dict, mfcc: np.ndarray
    ) -> tuple[float, list[dict]]:
        scores = []
        weights = []
        explanations = []

        mfcc_var = float(np.std(mfcc))
        spectral_score = normalize(spectral["spectral_centroid_std"], 50, 500)
        scores.append(spectral_score)
        weights.append(0.3)
        explanations.append({
            "feature": "spectral_variation",
            "value": spectral["spectral_centroid_std"],
            "weight": 0.3,
            "contribution": spectral_score * 0.3,
            "explanation": f"Spectral centroid std: {spectral['spectral_centroid_std']:.1f} Hz — {'Natural variation' if spectral_score > 0.4 else 'Synthetic monotone'}",
        })

        prosody_score = normalize(prosody["energy_dynamics"], 0.0001, 0.01)
        scores.append(prosody_score)
        weights.append(0.25)
        explanations.append({
            "feature": "prosody_dynamics",
            "value": prosody["energy_dynamics"],
            "weight": 0.25,
            "contribution": prosody_score * 0.25,
            "explanation": f"Energy dynamics: {prosody['energy_dynamics']:.6f} — {'Natural prosody' if prosody_score > 0.4 else 'Robotic cadence'}",
        })

        noise_score = normalize(noise["snr_db"], 5, 40)
        scores.append(noise_score)
        weights.append(0.2)
        explanations.append({
            "feature": "signal_quality",
            "value": noise["snr_db"],
            "weight": 0.2,
            "contribution": noise_score * 0.2,
            "explanation": f"SNR: {noise['snr_db']:.1f} dB — {'Clean audio' if noise['snr_db'] > 20 else 'Noisy environment'}",
        })

        zcr_score = normalize(spectral["zero_crossing_rate"], 0.02, 0.15)
        scores.append(zcr_score)
        weights.append(0.25)
        explanations.append({
            "feature": "zero_crossing_rate",
            "value": spectral["zero_crossing_rate"],
            "weight": 0.25,
            "contribution": zcr_score * 0.25,
            "explanation": f"ZCR: {spectral['zero_crossing_rate']:.4f} — {'Human-like' if 0.03 < spectral['zero_crossing_rate'] < 0.12 else 'Atypical'}",
        })

        total = sum(s * w for s, w in zip(scores, weights))
        return round(total, 4), explanations

    def analyze(self, audio_data: str, sample_rate: int = 16000) -> VoiceAnalysisResult:
        self.sample_rate = sample_rate
        with Timer() as timer:
            signal = self._decode_audio(audio_data)

            if len(signal) < self.sample_rate * 0.5:
                raise ValueError("Audio too short (minimum 0.5 seconds)")

            mfcc = self._compute_mfcc(signal)
            f0 = self._compute_fundamental_freq(signal)
            spectral = self._compute_spectral_features(signal)
            prosody = self._compute_prosody(signal)
            noise = self._analyze_noise(signal)

            authenticity_score, explanations = self._compute_authenticity(
                spectral, prosody, noise, mfcc
            )

            mfcc_var = float(np.std(mfcc))
            speaker_hash = hash(mfcc_var) % 10000
            speaker_id = f"SPK_{speaker_hash:04d}"
            speaker_count = 1 if authenticity_score > 0.6 else 2

        return VoiceAnalysisResult(
            is_live=authenticity_score >= 0.5,
            confidence=round(1.0 - abs(authenticity_score - 0.5) * 2, 4),
            authenticity_score=authenticity_score,
            speaker_count=speaker_count,
            speaker_id=speaker_id,
            spectral_features=spectral,
            prosody_features=prosody,
            noise_analysis=noise,
            audio_quality={
                "f0": f0,
                "sample_rate": sample_rate,
                "duration_seconds": round(len(signal) / sample_rate, 2),
                "total_frames": len(mfcc),
            },
            explanations=explanations,
            latency_ms=round(timer.elapsed_ms, 2),
        )
