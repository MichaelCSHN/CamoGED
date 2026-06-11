"""Standard F-measure variants used by the COD literature."""

from __future__ import annotations

import numpy as np

from ._common import EPS, adaptive_threshold, prepare_prediction_and_gt


def _precision_recall_curve(
    pred: np.ndarray, gt: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
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
    return precisions, recalls


def f_measure(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    """Compute max/mean/adaptive F-measure with the COD convention ``beta^2=0.3``."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    precisions, recalls = _precision_recall_curve(pred_arr, gt_arr)

    beta2 = 0.3
    numerator = (1.0 + beta2) * precisions * recalls
    denominator = np.where(numerator == 0, 1.0, beta2 * precisions + recalls)
    curve = numerator / denominator

    thr = adaptive_threshold(pred_arr)
    binary_prediction = pred_arr >= thr
    intersection = int(np.count_nonzero(binary_prediction & gt_arr))
    if intersection == 0:
        adaptive = 0.0
    else:
        precision = intersection / max(np.count_nonzero(binary_prediction), 1)
        recall = intersection / max(np.count_nonzero(gt_arr), 1)
        adaptive = (
            (1.0 + beta2) * precision * recall / (beta2 * precision + recall + EPS)
        )

    return {
        "max": float(curve.max()),
        "mean": float(curve.mean()),
        "adaptive": float(adaptive),
    }
