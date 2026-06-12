"""Lightweight generation and deception metrics.

The canonical FID/LPIPS implementations depend on heavy learned networks. This
module provides deterministic, dependency-light counterparts with the same
public API so demos, CI, and small offline audits can run without model weights.
The values are useful for smoke tests and relative comparisons inside the same
protocol; heavyweight Inception/LPIPS backends can be added later behind the
same API.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
from scipy import linalg
from scipy.ndimage import gaussian_filter, sobel

from ..perceptual import ms_ssim, ssim

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".pgm", ".npy"}
EPS = np.spacing(1)


def _load_image(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npy":
        return np.load(path)
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Image loading requires Pillow for non-.npy files.") from exc
    return np.asarray(Image.open(path).convert("RGB"))


def _normalize_image(image) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("image must be non-empty.")
    if not np.isfinite(arr).all():
        raise ValueError("image must not contain NaN or inf.")
    if arr.ndim == 2:
        arr = arr[..., None]
    if arr.ndim != 3:
        raise ValueError("image must be a 2D grayscale or 3D image array.")
    if arr.max() > 1.0 or arr.min() < 0.0:
        if arr.max() > 255.0 or arr.min() < 0.0:
            raise ValueError("image values must be in [0, 1] or [0, 255].")
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def _to_gray(image: np.ndarray) -> np.ndarray:
    if image.shape[-1] == 1:
        return image[..., 0]
    return image[..., :3].mean(axis=2)


def _feature_vector(image) -> np.ndarray:
    arr = _normalize_image(image)
    gray = _to_gray(arr)
    gx = sobel(gray, axis=1)
    gy = sobel(gray, axis=0)
    grad = np.hypot(gx, gy)
    blur = gaussian_filter(gray, sigma=1.5)
    high = gray - blur

    features: list[float] = []
    for channel in range(arr.shape[-1]):
        values = arr[..., channel].reshape(-1)
        features.extend(
            [
                float(values.mean()),
                float(values.std()),
                float(np.quantile(values, 0.1)),
                float(np.quantile(values, 0.5)),
                float(np.quantile(values, 0.9)),
            ]
        )
    for values in (gray.reshape(-1), grad.reshape(-1), high.reshape(-1)):
        features.extend(
            [
                float(values.mean()),
                float(values.std()),
                float(np.mean(np.abs(values))),
                float(np.quantile(values, 0.25)),
                float(np.quantile(values, 0.75)),
            ]
        )
    hist, _ = np.histogram(gray, bins=16, range=(0.0, 1.0), density=False)
    hist = hist.astype(np.float64) / (hist.sum() + EPS)
    features.extend(hist.tolist())
    return np.asarray(features, dtype=np.float64)


def _image_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"{directory} is not a directory.")
    files = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not files:
        raise ValueError(f"No supported image files found in {directory}.")
    return files


def _feature_matrix(directory: Path) -> np.ndarray:
    return np.stack(
        [_feature_vector(_load_image(path)) for path in _image_files(directory)],
        axis=0,
    )


def _mean_and_cov(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = features.mean(axis=0)
    if features.shape[0] == 1:
        cov = np.eye(features.shape[1], dtype=np.float64) * EPS
    else:
        cov = np.cov(features, rowvar=False)
    return mean, np.atleast_2d(cov)


def fid(real_dir: str, fake_dir: str) -> float:
    """Compute a deterministic lightweight Frechet feature distance.

    The feature extractor uses color, gradient, high-frequency, and histogram
    statistics rather than Inception activations. Lower is better.
    """

    real = _feature_matrix(Path(real_dir))
    fake = _feature_matrix(Path(fake_dir))
    mu_real, cov_real = _mean_and_cov(real)
    mu_fake, cov_fake = _mean_and_cov(fake)
    diff = mu_real - mu_fake
    eps_eye = np.eye(cov_real.shape[0], dtype=np.float64) * 1e-9
    covmean, _ = linalg.sqrtm((cov_real + eps_eye) @ (cov_fake + eps_eye), disp=False)
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    if np.isfinite(covmean).all():
        trace_covmean = float(np.trace(covmean))
    else:
        # Tiny demo sets often produce singular covariance products. Fall back
        # to the diagonal Frechet term rather than emitting NaN.
        diag_real = np.clip(np.diag(cov_real), 0.0, None)
        diag_fake = np.clip(np.diag(cov_fake), 0.0, None)
        trace_covmean = float(np.sum(np.sqrt(diag_real * diag_fake)))
    value = diff @ diff + np.trace(cov_real) + np.trace(cov_fake) - 2.0 * trace_covmean
    if not np.isfinite(value):
        raise ValueError("FID_lite produced a non-finite value.")
    return float(max(value, 0.0))


def kid(
    real_dir: str,
    fake_dir: str,
    degree: int = 3,
    gamma: float | None = None,
    coef0: float = 1.0,
) -> float:
    """Compute a polynomial-kernel MMD/KID-style distance over lightweight features."""

    real = _feature_matrix(Path(real_dir))
    fake = _feature_matrix(Path(fake_dir))
    gamma = gamma if gamma is not None else 1.0 / real.shape[1]

    def kernel(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return (gamma * (x @ y.T) + coef0) ** degree

    k_rr = kernel(real, real)
    k_ff = kernel(fake, fake)
    k_rf = kernel(real, fake)
    if len(real) > 1:
        rr = (k_rr.sum() - np.trace(k_rr)) / (len(real) * (len(real) - 1))
    else:
        rr = 0.0
    if len(fake) > 1:
        ff = (k_ff.sum() - np.trace(k_ff)) / (len(fake) * (len(fake) - 1))
    else:
        ff = 0.0
    return float(rr + ff - 2.0 * k_rf.mean())


def lpips(img_a, img_b) -> float:
    """Compute a lightweight perceptual distance inspired by LPIPS.

    Lower is better. The score combines multi-scale absolute error, gradient
    difference, and SSIM/MS-SSIM disagreement.
    """

    a = _normalize_image(img_a)
    b = _normalize_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    gray_a = _to_gray(a)
    gray_b = _to_gray(b)
    grad_a = np.hypot(sobel(gray_a, axis=1), sobel(gray_a, axis=0))
    grad_b = np.hypot(sobel(gray_b, axis=1), sobel(gray_b, axis=0))
    l1 = float(np.mean(np.abs(a - b)))
    grad = float(np.mean(np.abs(grad_a - grad_b)))
    structural = 1.0 - max(0.0, min(1.0, ssim(gray_a, gray_b)))
    multiscale = 1.0 - max(0.0, min(1.0, ms_ssim(gray_a, gray_b)))
    return float(0.45 * l1 + 0.25 * grad + 0.2 * structural + 0.1 * multiscale)


def dists(img_a, img_b) -> float:
    """Compute a lightweight DISTS-style structure/texture distance."""

    a = _normalize_image(img_a)
    b = _normalize_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    gray_a = _to_gray(a)
    gray_b = _to_gray(b)
    texture_a = gray_a - gaussian_filter(gray_a, sigma=2.0)
    texture_b = gray_b - gaussian_filter(gray_b, sigma=2.0)
    structure = 1.0 - max(0.0, min(1.0, ssim(gray_a, gray_b)))
    texture = float(np.mean(np.abs(texture_a - texture_b)))
    contrast = float(abs(gray_a.std() - gray_b.std()))
    return float(0.5 * structure + 0.35 * texture + 0.15 * contrast)


def _target_success(output, target) -> bool:
    if callable(target):
        return bool(target(output))
    if isinstance(output, dict):
        if "label" in output:
            output = output["label"]
        elif "class" in output:
            output = output["class"]
        elif "score" in output and isinstance(target, (int, float)):
            return float(output["score"]) <= float(target)
    if isinstance(target, (set, list, tuple)) and not isinstance(target, str):
        return output in target
    return output == target


def deception_rate(detector: Callable, images: Sequence, targets: Sequence | Callable) -> float:
    """Compute the fraction of images for which a detector meets the target.

    ``targets`` may be a callable success criterion applied to each detector
    output, or a sequence aligned with ``images``.
    """

    image_list = list(images)
    if not image_list:
        raise ValueError("At least one image is required.")
    outputs = [detector(image) for image in image_list]
    if callable(targets):
        successes = [bool(targets(output)) for output in outputs]
    else:
        target_list = list(targets)
        if len(target_list) != len(image_list):
            raise ValueError("targets must have the same length as images.")
        successes = [
            _target_success(output, target) for output, target in zip(outputs, target_list)
        ]
    return float(sum(successes) / len(successes))
