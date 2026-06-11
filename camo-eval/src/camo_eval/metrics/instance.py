"""Instance and mask-level metrics for camouflage segmentation tasks.

This module covers layer-1 metrics that are commonly used once a task moves
from binary foreground-map evaluation to explicit object masks and boundaries.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion

from .detection._common import EPS, prepare_prediction_and_gt


def iou(pred: np.ndarray, gt: np.ndarray) -> float:
    """Compute the intersection-over-union for two binary masks."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    union = np.count_nonzero(pred_mask | gt_mask)
    if union == 0:
        return 1.0
    intersection = np.count_nonzero(pred_mask & gt_mask)
    return float(intersection / union)


def dice(pred: np.ndarray, gt: np.ndarray) -> float:
    """Compute the Dice coefficient for two binary masks."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    denom = np.count_nonzero(pred_mask) + np.count_nonzero(gt_mask)
    if denom == 0:
        return 1.0
    intersection = np.count_nonzero(pred_mask & gt_mask)
    return float((2.0 * intersection) / denom)


def _boundary_mask(mask: np.ndarray) -> np.ndarray:
    mask = mask.astype(bool)
    if not np.any(mask):
        return np.zeros_like(mask, dtype=bool)
    eroded = binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    return mask ^ eroded


def boundary_iou(
    pred: np.ndarray, gt: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    """Compute a tolerance-based boundary overlap score.

    The implementation follows the common "match within a dilated neighborhood"
    pattern used by boundary metrics. It serves as a practical boundary-IoU-like
    score for camouflage masks, where precise contour quality matters.
    """

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    if pred_mask.shape != gt_mask.shape:
        raise ValueError("Prediction and ground truth must share the same shape.")

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

    pred_match = pred_boundary & gt_dilated
    gt_match = gt_boundary & pred_dilated
    intersection = np.count_nonzero(pred_match) + np.count_nonzero(gt_match)
    union = np.count_nonzero(pred_boundary) + np.count_nonzero(gt_boundary)
    return float(intersection / (union + EPS))


def average_precision(
    true_positive_flags: np.ndarray,
    confidence_scores: np.ndarray,
    num_ground_truth: int,
) -> float:
    """Compute average precision from ranked detections.

    Parameters
    ----------
    true_positive_flags:
        Boolean/0-1 array indicating whether each ranked prediction is a true
        positive after matching.
    confidence_scores:
        Confidence scores aligned with ``true_positive_flags``.
    num_ground_truth:
        Total number of ground-truth objects.
    """

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

    recalls = tp_cumsum / num_ground_truth
    precisions = tp_cumsum / np.maximum(tp_cumsum + fp_cumsum, EPS)

    recalls = np.concatenate(([0.0], recalls, [1.0]))
    precisions = np.concatenate(([1.0], precisions, [0.0]))
    for idx in range(len(precisions) - 2, -1, -1):
        precisions[idx] = max(precisions[idx], precisions[idx + 1])
    return float(np.sum((recalls[1:] - recalls[:-1]) * precisions[1:]))


def average_recall(true_positive_flags: np.ndarray, num_ground_truth: int) -> float:
    """Compute average recall from a set of matched detections."""

    if num_ground_truth <= 0:
        raise ValueError("num_ground_truth must be positive.")
    tp = np.asarray(true_positive_flags, dtype=np.float64)
    return float(np.sum(tp) / num_ground_truth)
