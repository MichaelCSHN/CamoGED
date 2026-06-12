"""Clutter, saliency, and camouflage-difficulty metrics."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import sobel

from .background import target_background_similarity
from .detection._common import EPS


def _prepare_gray(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("image must be non-empty.")
    if not np.isfinite(arr).all():
        raise ValueError("image must not contain NaN or inf.")
    if arr.ndim == 3:
        arr = arr[..., :3].mean(axis=2)
    if arr.ndim != 2:
        raise ValueError("image must be a 2D grayscale or RGB-like image.")
    if arr.max() > 1.0 or arr.min() < 0.0:
        if arr.max() > 255.0 or arr.min() < 0.0:
            raise ValueError("image values must be in [0, 1] or [0, 255].")
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def edge_density(image: np.ndarray, threshold: float | None = None) -> float:
    """Return the fraction of pixels whose gradient magnitude exceeds threshold."""

    gray = _prepare_gray(image)
    grad = np.hypot(sobel(gray, axis=1), sobel(gray, axis=0))
    if threshold is None:
        threshold = float(grad.mean() + grad.std())
    return float(np.mean(grad > threshold))


def subband_entropy(image: np.ndarray, bins: int = 32) -> float:
    """Estimate high-frequency entropy from a Sobel-gradient histogram."""

    if bins <= 1:
        raise ValueError("bins must be greater than 1.")
    gray = _prepare_gray(image)
    grad = np.hypot(sobel(gray, axis=1), sobel(gray, axis=0))
    if float(grad.max()) > 0:
        grad = grad / float(grad.max())
    hist, _ = np.histogram(grad, bins=bins, range=(0.0, 1.0), density=False)
    prob = hist.astype(np.float64) / (hist.sum() + EPS)
    prob = prob[prob > 0]
    return float(-np.sum(prob * np.log2(prob)) / np.log2(bins))


def feature_congestion(image: np.ndarray) -> float:
    """Compute a lightweight feature-congestion proxy.

    Higher values indicate stronger local contrast and orientation variability.
    """

    gray = _prepare_gray(image)
    gx = sobel(gray, axis=1)
    gy = sobel(gray, axis=0)
    magnitude = np.hypot(gx, gy)
    orientation = np.arctan2(gy, gx)
    mag_term = float(magnitude.std())
    orient_term = float(np.std(np.sin(orientation)) + np.std(np.cos(orientation))) / 2.0
    return float(mag_term * orient_term)


def camouflage_difficulty(image: np.ndarray, target_mask: np.ndarray) -> dict[str, float]:
    """Return a compact difficulty summary for target/background camouflage."""

    gray = _prepare_gray(image)
    similarity = target_background_similarity(gray, target_mask, mode="near")
    edge = edge_density(gray)
    entropy = subband_entropy(gray)
    congestion = feature_congestion(gray)
    # Higher histogram intersection and clutter imply harder visual search.
    score = (
        0.45 * similarity["histogram_intersection"]
        + 0.2 * (1.0 - similarity["mean_abs_diff"])
        + 0.15 * edge
        + 0.1 * entropy
        + 0.1 * min(congestion, 1.0)
    )
    return {
        "difficulty": float(np.clip(score, 0.0, 1.0)),
        "edge_density": edge,
        "subband_entropy": entropy,
        "feature_congestion": congestion,
        **{f"near_{key}": value for key, value in similarity.items()},
    }
