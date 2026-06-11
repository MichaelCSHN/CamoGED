"""Signal and signature metrics for thermal and multispectral camouflage."""

from __future__ import annotations

import numpy as np

from .detection._common import EPS


def thermal_contrast(target: np.ndarray, background: np.ndarray) -> float:
    """Return the mean thermal contrast between target and background regions."""

    target_arr = np.asarray(target, dtype=np.float64)
    background_arr = np.asarray(background, dtype=np.float64)
    if target_arr.size == 0 or background_arr.size == 0:
        raise ValueError("Target and background arrays must be non-empty.")
    return float(np.mean(target_arr) - np.mean(background_arr))


def signal_to_clutter_ratio(target: np.ndarray, background: np.ndarray) -> float:
    """Compute a simple signal-to-clutter ratio."""

    target_arr = np.asarray(target, dtype=np.float64)
    background_arr = np.asarray(background, dtype=np.float64)
    if target_arr.size == 0 or background_arr.size == 0:
        raise ValueError("Target and background arrays must be non-empty.")
    signal = abs(float(np.mean(target_arr) - np.mean(background_arr)))
    clutter = float(np.std(background_arr))
    return float(signal / (clutter + EPS))


def spectral_angle_mapper(signature_a: np.ndarray, signature_b: np.ndarray) -> float:
    """Compute spectral angle mapper in radians between two signatures."""

    a = np.asarray(signature_a, dtype=np.float64).reshape(-1)
    b = np.asarray(signature_b, dtype=np.float64).reshape(-1)
    if a.size == 0 or b.size == 0:
        raise ValueError("Signatures must be non-empty.")
    if a.shape != b.shape:
        raise ValueError("Signatures must have the same length.")
    numerator = float(np.dot(a, b))
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    cosine = np.clip(numerator / (denominator + EPS), -1.0, 1.0)
    if np.isclose(cosine, 1.0, atol=1e-12):
        return 0.0
    return float(np.arccos(cosine))
