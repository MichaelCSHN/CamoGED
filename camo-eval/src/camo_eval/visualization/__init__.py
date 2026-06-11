"""Visualization helpers for COD mask evaluation demos."""

from __future__ import annotations

import numpy as np

from ..metrics.detection._common import prepare_prediction_and_gt


def _boundary(mask: np.ndarray) -> np.ndarray:
    padded = np.pad(mask.astype(bool), 1, mode="constant", constant_values=False)
    center = padded[1:-1, 1:-1]
    neighbors = (
        padded[:-2, 1:-1] & padded[2:, 1:-1] & padded[1:-1, :-2] & padded[1:-1, 2:]
    )
    return center & ~neighbors


def mask_overlay(
    pred: np.ndarray, gt: np.ndarray, threshold: float = 0.5
) -> np.ndarray:
    """Create an RGB overlay with prediction fill and ground-truth boundary."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= threshold
    gt_mask = gt_arr.astype(bool)

    base = np.repeat((gt_mask.astype(np.float64) * 130.0 + 45.0)[..., None], 3, axis=2)
    overlay = base.copy()
    overlay[pred_mask] = (
        overlay[pred_mask] * 0.35 + np.array([255.0, 185.0, 35.0]) * 0.65
    )
    overlay[_boundary(gt_mask)] = np.array([0.0, 215.0, 255.0])
    return np.clip(overlay, 0, 255).astype(np.uint8)


def error_map(pred: np.ndarray, gt: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Create an RGB TP/FP/FN/TN mask error map."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= threshold
    gt_mask = gt_arr.astype(bool)

    out = np.zeros((*pred_mask.shape, 3), dtype=np.uint8)
    out[~pred_mask & ~gt_mask] = np.array([25, 25, 25], dtype=np.uint8)
    out[pred_mask & gt_mask] = np.array([45, 190, 95], dtype=np.uint8)
    out[pred_mask & ~gt_mask] = np.array([55, 135, 235], dtype=np.uint8)
    out[~pred_mask & gt_mask] = np.array([225, 70, 65], dtype=np.uint8)
    return out


__all__ = ["mask_overlay", "error_map"]
