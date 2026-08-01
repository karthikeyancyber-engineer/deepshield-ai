import time
import numpy as np
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIDetection:
    """Base result container for all AI detections."""
    confidence: float
    latency_ms: float
    features: dict = field(default_factory=dict)
    explanations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class Timer:
    """Context manager for measuring execution time."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = (time.perf_counter() - self.start) * 1000


def normalize(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return float(np.clip((value - min_val) / (max_val - min_val + 1e-8), 0.0, 1.0))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a.flatten(), b.flatten())
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(dot / (norm + 1e-8))


def compute_entropy(scores: list[float]) -> float:
    arr = np.array(scores, dtype=np.float64)
    arr = arr[arr > 0]
    arr = arr / arr.sum()
    return float(-np.sum(arr * np.log2(arr + 1e-8)))


def exponential_moving_average(values: list[float], alpha: float = 0.3) -> list[float]:
    if not values:
        return []
    result = [values[0]]
    for v in values[1:]:
        result.append(alpha * v + (1 - alpha) * result[-1])
    return result
