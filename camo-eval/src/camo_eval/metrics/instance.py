"""Instance and mask-level metrics."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion

from .detection._common import EPS, prepare_prediction_and_gt


def iou(pred: np.ndarray, gt: np.ndarray) -> float:
    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    union = np.count_nonzero(pred_mask | gt_mask)
    if union == 0:
        return 1.0
    return float(np.count_nonzero(pred_mask & gt_mask) / union)


def dice(pred: np.ndarray, gt: np.ndarray) -> float:
    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    denom = np.count_nonzero(pred_mask) + np.count_nonzero(gt_mask)
    if denom == 0:
        return 1.0
    return float((2.0 * np.count_nonzero(pred_mask & gt_mask)) / denom)


def _boundary_mask(mask: np.ndarray) -> np.ndarray:
    mask = mask.astype(bool)
    if not np.any(mask):
        return np.zeros_like(mask, dtype=bool)
    eroded = binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    return mask ^ eroded


def boundary_iou(
    pred: np.ndarray, gt: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    raise NotImplementedError(
        "Standard region-band Boundary IoU is not implemented. Use boundary_match_score for the experimental tolerance-based contour score."
    )


def boundary_match_score(
    pred: np.ndarray, gt: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    """Symmetric tolerance-based contour matching score; not standard Boundary IoU."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    pred_boundary = _boundary_mask(pred_mask)
    gt_boundary = _boundary_mask(gt_mask)
    if not np.any(pred_boundary) and not np.any(gt_boundary):
        return 1.0
    h, w = pred_mask.shape
    dilation = max(1, int(round(dilation_ratio * np.hypot(h, w))))
    structure = np.ones((3, 3), dtype=bool)
    pred_dilated = binary_dilation(
        pred_boundary, structure=structure, iterations=dilation
    )
    gt_dilated = binary_dilation(gt_boundary, structure=structure, iterations=dilation)
    matched = np.count_nonzero(pred_boundary & gt_dilated) + np.count_nonzero(
        gt_boundary & pred_dilated
    )
    total = np.count_nonzero(pred_boundary) + np.count_nonzero(gt_boundary)
    return float(matched / (total + EPS))


def average_precision(
    true_positive_flags: np.ndarray,
    confidence_scores: np.ndarray,
    num_ground_truth: int,
) -> float:
    if num_ground_truth <= 0:
        raise ValueError("num_ground_truth must be positive.")
    tp = np.asarray(true_positive_flags, dtype=np.float64)
    scores = np.asarray(confidence_scores, dtype=np.float64)
    if tp.shape != scores.shape:
        raise ValueError(
            "true_positive_flags and confidence_scores must have the same shape."
        )
    order = np.argsort(-scores)
    tp = tp[order]
    fp = 1.0 - tp
    tp_cumsum = np.cumsum(tp)
    fp_cumsum = np.cumsum(fp)
    recalls = np.concatenate(([0.0], tp_cumsum / num_ground_truth, [1.0]))
    precisions = np.concatenate(
        ([1.0], tp_cumsum / np.maximum(tp_cumsum + fp_cumsum, EPS), [0.0])
    )
    for index in range(len(precisions) - 2, -1, -1):
        precisions[index] = max(precisions[index], precisions[index + 1])
    return float(np.sum((recalls[1:] - recalls[:-1]) * precisions[1:]))


def average_recall(true_positive_flags: np.ndarray, num_ground_truth: int) -> float:
    if num_ground_truth <= 0:
        raise ValueError("num_ground_truth must be positive.")
    return float(
        np.sum(np.asarray(true_positive_flags, dtype=np.float64)) / num_ground_truth
    )
