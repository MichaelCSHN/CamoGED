"""Standard F-measure variants used by the COD literature."""

from __future__ import annotations

import numpy as np

from ._common import EPS, adaptive_threshold, prepare_prediction_and_gt


def _precision_recall_curve_arrays(
    pred: np.ndarray, gt: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pred_uint8 = (pred * 255).astype(np.uint8)
    bins = np.linspace(0, 256, 257)
    fg_hist, _ = np.histogram(pred_uint8[gt], bins=bins)
    bg_hist, _ = np.histogram(pred_uint8[~gt], bins=bins)

    fg_w_thrs = np.cumsum(np.flip(fg_hist), axis=0)
    bg_w_thrs = np.cumsum(np.flip(bg_hist), axis=0)
    true_positive = fg_w_thrs
    predicted_positive = fg_w_thrs + bg_w_thrs
    predicted_positive[predicted_positive == 0] = 1
    gt_positive = max(np.count_nonzero(gt), 1)

    precisions = true_positive / predicted_positive
    recalls = true_positive / gt_positive
    thresholds = np.arange(255, -1, -1, dtype=np.float64) / 255.0
    return thresholds, precisions, recalls


def _adaptive_precision_recall(pred: np.ndarray, gt: np.ndarray) -> tuple[float, float]:
    threshold = adaptive_threshold(pred)
    binary_prediction = pred >= threshold
    intersection = int(np.count_nonzero(binary_prediction & gt))
    if intersection == 0:
        return 0.0, 0.0
    precision_value = intersection / max(np.count_nonzero(binary_prediction), 1)
    recall_value = intersection / max(np.count_nonzero(gt), 1)
    return float(precision_value), float(recall_value)


def precision_recall_curve(pred: np.ndarray, gt: np.ndarray) -> dict[str, np.ndarray]:
    """Return COD/SOD precision-recall curve samples across 256 thresholds."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    thresholds, precisions, recalls = _precision_recall_curve_arrays(pred_arr, gt_arr)
    return {
        "thresholds": thresholds,
        "precision": precisions,
        "recall": recalls,
    }


def precision(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    """Compute max/mean/adaptive precision over the COD threshold sweep."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    _, precisions, _ = _precision_recall_curve_arrays(pred_arr, gt_arr)
    adaptive_precision, _ = _adaptive_precision_recall(pred_arr, gt_arr)
    return {
        "max": float(precisions.max()),
        "mean": float(precisions.mean()),
        "adaptive": float(adaptive_precision),
    }


def recall(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    """Compute max/mean/adaptive recall over the COD threshold sweep."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    _, _, recalls = _precision_recall_curve_arrays(pred_arr, gt_arr)
    _, adaptive_recall = _adaptive_precision_recall(pred_arr, gt_arr)
    return {
        "max": float(recalls.max()),
        "mean": float(recalls.mean()),
        "adaptive": float(adaptive_recall),
    }


def f_measure(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    """Compute max/mean/adaptive F-measure with the COD convention ``beta^2=0.3``."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    _, precisions, recalls = _precision_recall_curve_arrays(pred_arr, gt_arr)

    beta2 = 0.3
    numerator = (1.0 + beta2) * precisions * recalls
    denominator = np.where(numerator == 0, 1.0, beta2 * precisions + recalls)
    curve = numerator / denominator

    precision_value, recall_value = _adaptive_precision_recall(pred_arr, gt_arr)
    adaptive = (
        (1.0 + beta2)
        * precision_value
        * recall_value
        / (beta2 * precision_value + recall_value + EPS)
    )

    return {
        "max": float(curve.max()),
        "mean": float(curve.mean()),
        "adaptive": float(adaptive),
    }
