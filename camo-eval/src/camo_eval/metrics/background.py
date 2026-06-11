"""Target-background similarity metrics for COD appearance analysis."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation

from .detection._common import EPS


def _prepare_gray_image(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("image must be non-empty.")
    if not np.isfinite(arr).all():
        raise ValueError("image must not contain NaN or inf.")
    if arr.ndim == 3:
        arr = arr[..., :3].mean(axis=2)
    if arr.ndim != 2:
        raise ValueError("image must be a 2D grayscale or 3D RGB-like array.")
    if arr.max() > 1.0 or arr.min() < 0.0:
        if arr.max() > 255.0 or arr.min() < 0.0:
            raise ValueError("image values must be in [0, 1] or [0, 255].")
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def _prepare_mask(mask: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    arr = np.asarray(mask)
    if arr.shape != shape:
        raise ValueError(f"mask shape {arr.shape} does not match image shape {shape}.")
    return arr > 0


def _background_region(mask: np.ndarray, mode: str, near_iterations: int) -> np.ndarray:
    if mode == "all":
        return ~mask
    if mode == "near":
        if near_iterations <= 0:
            raise ValueError("near_iterations must be positive.")
        dilated = binary_dilation(mask, iterations=near_iterations)
        return dilated & ~mask
    raise ValueError("mode must be 'all' or 'near'.")


def target_background_similarity(
    image: np.ndarray,
    target_mask: np.ndarray,
    *,
    mode: str = "all",
    bins: int = 32,
    near_iterations: int = 5,
) -> dict[str, float]:
    """Compare target appearance with all-background or near-background pixels.

    Returns lower-is-more-similar absolute mean/contrast differences and a
    higher-is-more-similar histogram intersection score.
    """

    img = _prepare_gray_image(image)
    mask = _prepare_mask(target_mask, img.shape)
    background = _background_region(mask, mode=mode, near_iterations=near_iterations)
    if not np.any(mask):
        raise ValueError("target_mask must contain foreground pixels.")
    if not np.any(background):
        raise ValueError("background region is empty.")

    target_values = img[mask]
    background_values = img[background]
    target_hist, _ = np.histogram(
        target_values, bins=bins, range=(0.0, 1.0), density=True
    )
    background_hist, _ = np.histogram(
        background_values, bins=bins, range=(0.0, 1.0), density=True
    )
    target_hist = target_hist / (target_hist.sum() + EPS)
    background_hist = background_hist / (background_hist.sum() + EPS)

    return {
        "mean_abs_diff": float(abs(target_values.mean() - background_values.mean())),
        "contrast_abs_diff": float(abs(target_values.std() - background_values.std())),
        "histogram_intersection": float(np.minimum(target_hist, background_hist).sum()),
    }


__all__ = ["target_background_similarity"]
