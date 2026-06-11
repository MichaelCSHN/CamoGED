"""Perceptual similarity metrics for camouflage generation and reconstruction."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter


def _prepare_image_pair(
    img_a: np.ndarray, img_b: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(img_a, dtype=np.float64)
    b = np.asarray(img_b, dtype=np.float64)
    if a.size == 0 or b.size == 0:
        raise ValueError("Images must be non-empty.")
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Images must not contain NaN or inf.")

    if a.max() > 1.0 or a.min() < 0.0:
        if a.max() > 255.0 or a.min() < 0.0:
            raise ValueError("Image values must be in [0, 1] or [0, 255].")
        a = a / 255.0
    if b.max() > 1.0 or b.min() < 0.0:
        if b.max() > 255.0 or b.min() < 0.0:
            raise ValueError("Image values must be in [0, 1] or [0, 255].")
        b = b / 255.0
    return np.clip(a, 0.0, 1.0), np.clip(b, 0.0, 1.0)


def _ssim_single_channel(
    a: np.ndarray, b: np.ndarray, sigma: float, truncate: float = 3.5
) -> float:
    c1 = 0.01**2
    c2 = 0.03**2
    args = {"sigma": sigma, "truncate": truncate}

    mu_a = gaussian_filter(a, **args)
    mu_b = gaussian_filter(b, **args)
    mu_a_sq = mu_a * mu_a
    mu_b_sq = mu_b * mu_b
    mu_ab = mu_a * mu_b

    sigma_a_sq = gaussian_filter(a * a, **args) - mu_a_sq
    sigma_b_sq = gaussian_filter(b * b, **args) - mu_b_sq
    sigma_ab = gaussian_filter(a * b, **args) - mu_ab

    numerator = (2 * mu_ab + c1) * (2 * sigma_ab + c2)
    denominator = (mu_a_sq + mu_b_sq + c1) * (sigma_a_sq + sigma_b_sq + c2)
    ssim_map = numerator / denominator

    # Match skimage's convention: average over the valid interior, dropping the
    # ``int(truncate*sigma + 0.5)`` border where the Gaussian window runs off the
    # edge. Fall back to the full map for images too small to crop.
    pad = int(truncate * sigma + 0.5)
    if ssim_map.shape[0] > 2 * pad and ssim_map.shape[1] > 2 * pad:
        ssim_map = ssim_map[pad:-pad, pad:-pad]
    return float(ssim_map.mean())


def ssim(img_a: np.ndarray, img_b: np.ndarray, sigma: float = 1.5) -> float:
    """Compute structural similarity (Wang et al. 2004) for grayscale or RGB images.

    Matches ``skimage.metrics.structural_similarity`` with
    ``gaussian_weights=True, sigma=1.5, use_sample_covariance=False`` to ~1e-6.
    Multichannel input is scored per channel and averaged.
    """

    a, b = _prepare_image_pair(img_a, img_b)
    if a.ndim == 3:
        channels = [
            _ssim_single_channel(a[..., c], b[..., c], sigma)
            for c in range(a.shape[-1])
        ]
        return float(np.mean(channels))
    return _ssim_single_channel(a, b, sigma)


def _downsample(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return (
            image[0::2, 0::2]
            + image[1::2, 0::2]
            + image[0::2, 1::2]
            + image[1::2, 1::2]
        ) / 4.0
    return (
        image[0::2, 0::2, ...]
        + image[1::2, 0::2, ...]
        + image[0::2, 1::2, ...]
        + image[1::2, 1::2, ...]
    ) / 4.0


def ms_ssim(img_a: np.ndarray, img_b: np.ndarray, levels: int = 4) -> float:
    """Compute a lightweight multi-scale SSIM score."""

    a, b = _prepare_image_pair(img_a, img_b)
    weights = np.array([0.0448, 0.2856, 0.3001, 0.2363, 0.1333], dtype=np.float64)
    weights = weights[:levels]
    weights = weights / weights.sum()

    scores = []
    for _ in range(levels):
        scores.append(max(ssim(a, b), 0.0))
        if min(a.shape[0], a.shape[1]) < 2 or min(b.shape[0], b.shape[1]) < 2:
            break
        if a.shape[0] % 2 == 1:
            a = a[:-1, ...]
            b = b[:-1, ...]
        if a.shape[1] % 2 == 1:
            a = a[:, :-1, ...]
            b = b[:, :-1, ...]
        a = _downsample(a)
        b = _downsample(b)

    weights = weights[: len(scores)]
    return float(np.prod(np.power(np.asarray(scores), weights)))
