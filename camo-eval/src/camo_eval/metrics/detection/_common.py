"""Shared helpers for detection metrics."""

from __future__ import annotations

import numpy as np

EPS = np.spacing(1)


def prepare_prediction_and_gt(
    pred: np.ndarray, gt: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Normalize prediction to ``[0, 1]`` and binarize the ground truth."""

    pred_arr = np.asarray(pred)
    gt_arr = np.asarray(gt)

    if pred_arr.size == 0 or gt_arr.size == 0:
        raise ValueError("Prediction and ground truth must be non-empty.")

    pred_arr = _coerce_hw(pred_arr, "pred")
    gt_arr = _coerce_hw(gt_arr, "gt")
    if pred_arr.shape != gt_arr.shape:
        raise ValueError(f"Shape mismatch: pred {pred_arr.shape} vs gt {gt_arr.shape}")

    if not np.issubdtype(pred_arr.dtype, np.number) or not np.issubdtype(
        gt_arr.dtype, np.number
    ):
        raise TypeError("Prediction and ground truth must be numeric arrays.")

    pred_float = pred_arr.astype(np.float64, copy=False)
    gt_float = gt_arr.astype(np.float64, copy=False)
    if not np.isfinite(pred_float).all() or not np.isfinite(gt_float).all():
        raise ValueError("Prediction and ground truth must not contain NaN or inf.")

    pred_min = float(pred_float.min())
    pred_max = float(pred_float.max())
    if pred_max > 1.0 or pred_min < 0.0:
        if pred_min < 0.0 or pred_max > 255.0:
            raise ValueError("Prediction values must lie in [0, 1] or [0, 255].")
        pred_float = pred_float / 255.0
        scaled_min = float(pred_float.min())
        scaled_max = float(pred_float.max())
        if scaled_max != scaled_min:
            pred_float = (pred_float - scaled_min) / (scaled_max - scaled_min)
    pred_float = np.clip(pred_float, 0.0, 1.0)

    gt_bool = gt_float > 0
    return pred_float, gt_bool


def adaptive_threshold(pred: np.ndarray) -> float:
    """Return the COD adaptive threshold ``min(2 * mean(pred), 1)``."""

    return min(2.0 * float(pred.mean()), 1.0)


def _coerce_hw(array: np.ndarray, name: str) -> np.ndarray:
    if array.ndim == 2:
        return array
    if array.ndim == 3:
        squeezed = np.squeeze(array)
        if squeezed.ndim == 2:
            return squeezed
    raise ValueError(
        f"{name} must be a 2D array or 3D array with a singleton channel dimension."
    )
