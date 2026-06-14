"""E-measure and weighted F-measure for COD."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import convolve
from scipy.ndimage import distance_transform_edt as distance_transform

from ._common import EPS, adaptive_threshold, prepare_prediction_and_gt


def _generate_parts_numel_combinations(
    gt_fg_numel: int,
    gt_size: int,
    fg_fg_numel,
    fg_bg_numel,
    pred_fg_numel,
    pred_bg_numel,
):
    bg_fg_numel = gt_fg_numel - fg_fg_numel
    bg_bg_numel = pred_bg_numel - bg_fg_numel
    parts_numel = [fg_fg_numel, fg_bg_numel, bg_fg_numel, bg_bg_numel]

    mean_pred_value = pred_fg_numel / gt_size
    mean_gt_value = gt_fg_numel / gt_size

    demeaned_pred_fg_value = 1 - mean_pred_value
    demeaned_pred_bg_value = 0 - mean_pred_value
    demeaned_gt_fg_value = 1 - mean_gt_value
    demeaned_gt_bg_value = 0 - mean_gt_value

    combinations = [
        (demeaned_pred_fg_value, demeaned_gt_fg_value),
        (demeaned_pred_fg_value, demeaned_gt_bg_value),
        (demeaned_pred_bg_value, demeaned_gt_fg_value),
        (demeaned_pred_bg_value, demeaned_gt_bg_value),
    ]
    return parts_numel, combinations


def _em_with_threshold(pred: np.ndarray, gt: np.ndarray, threshold: float) -> float:
    gt_fg_numel = int(np.count_nonzero(gt))
    gt_size = int(gt.size)
    if gt_size == 1:
        return float(
            (pred >= threshold).astype(np.uint8).item() == gt.astype(np.uint8).item()
        )
    binarized_pred = pred >= threshold
    fg_fg_numel = int(np.count_nonzero(binarized_pred & gt))
    fg_bg_numel = int(np.count_nonzero(binarized_pred & ~gt))
    pred_fg_numel = fg_fg_numel + fg_bg_numel
    pred_bg_numel = gt_size - pred_fg_numel

    if gt_fg_numel == 0:
        enhanced_matrix_sum = pred_bg_numel
    elif gt_fg_numel == gt_size:
        enhanced_matrix_sum = pred_fg_numel
    else:
        parts_numel, combinations = _generate_parts_numel_combinations(
            gt_fg_numel=gt_fg_numel,
            gt_size=gt_size,
            fg_fg_numel=fg_fg_numel,
            fg_bg_numel=fg_bg_numel,
            pred_fg_numel=pred_fg_numel,
            pred_bg_numel=pred_bg_numel,
        )
        enhanced_matrix_sum = 0.0
        for part_numel, combination in zip(parts_numel, combinations):
            align_matrix_value = (
                2
                * (combination[0] * combination[1])
                / (combination[0] ** 2 + combination[1] ** 2 + EPS)
            )
            enhanced_matrix_value = (align_matrix_value + 1) ** 2 / 4
            enhanced_matrix_sum += enhanced_matrix_value * part_numel

    return float(enhanced_matrix_sum / (gt_size - 1 + EPS))


def _em_curve(pred: np.ndarray, gt: np.ndarray) -> np.ndarray:
    gt_fg_numel = int(np.count_nonzero(gt))
    gt_size = int(gt.size)
    if gt_size == 1:
        # `pred` is a normalized float in [0, 1]; binarize at 0.5 before comparing.
        # (The previous `pred.astype(np.uint8)` truncated e.g. 0.99 -> 0, wrongly
        # scoring a near-correct single-pixel prediction as a total miss.)
        score = float(bool(pred.item() >= 0.5) == bool(gt.item()))
        return np.full(256, score, dtype=np.float64)
    pred_uint8 = (pred * 255).astype(np.uint8)
    bins = np.linspace(0, 256, 257)
    fg_fg_hist, _ = np.histogram(pred_uint8[gt], bins=bins)
    fg_bg_hist, _ = np.histogram(pred_uint8[~gt], bins=bins)
    fg_fg_numel_w_thrs = np.cumsum(np.flip(fg_fg_hist), axis=0)
    fg_bg_numel_w_thrs = np.cumsum(np.flip(fg_bg_hist), axis=0)
    pred_fg_numel_w_thrs = fg_fg_numel_w_thrs + fg_bg_numel_w_thrs
    pred_bg_numel_w_thrs = gt_size - pred_fg_numel_w_thrs

    if gt_fg_numel == 0:
        enhanced_matrix_sum = pred_bg_numel_w_thrs
    elif gt_fg_numel == gt_size:
        enhanced_matrix_sum = pred_fg_numel_w_thrs
    else:
        parts_numel_w_thrs, combinations = _generate_parts_numel_combinations(
            gt_fg_numel=gt_fg_numel,
            gt_size=gt_size,
            fg_fg_numel=fg_fg_numel_w_thrs,
            fg_bg_numel=fg_bg_numel_w_thrs,
            pred_fg_numel=pred_fg_numel_w_thrs,
            pred_bg_numel=pred_bg_numel_w_thrs,
        )
        results_parts = np.empty((4, 256), dtype=np.float64)
        for idx, (part_numel, combination) in enumerate(
            zip(parts_numel_w_thrs, combinations)
        ):
            align_matrix_value = (
                2
                * (combination[0] * combination[1])
                / (combination[0] ** 2 + combination[1] ** 2 + EPS)
            )
            enhanced_matrix_value = (align_matrix_value + 1) ** 2 / 4
            results_parts[idx] = enhanced_matrix_value * part_numel
        enhanced_matrix_sum = results_parts.sum(axis=0)

    return enhanced_matrix_sum / (gt_size - 1 + EPS)


def e_measure(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    """Compute adaptive/mean/max E-measure following Fan et al. (IJCAI 2018)."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    curve = _em_curve(pred_arr, gt_arr)
    adaptive = _em_with_threshold(pred_arr, gt_arr, adaptive_threshold(pred_arr))
    return {
        "adaptive": float(adaptive),
        "mean": float(curve.mean()),
        "max": float(curve.max()),
    }


def _matlab_style_gauss2d(
    shape: tuple[int, int] = (7, 7), sigma: int = 5
) -> np.ndarray:
    m, n = [(size - 1) / 2 for size in shape]
    y, x = np.ogrid[-m : m + 1, -n : n + 1]
    kernel = np.exp(-(x * x + y * y) / (2 * sigma * sigma))
    kernel[kernel < np.finfo(kernel.dtype).eps * kernel.max()] = 0
    sum_kernel = kernel.sum()
    if sum_kernel != 0:
        kernel /= sum_kernel
    return kernel


def weighted_f_measure(pred: np.ndarray, gt: np.ndarray, beta2: float = 1.0) -> float:
    """Compute weighted F-measure following Margolin et al. (CVPR 2014)."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    if np.all(~gt_arr):
        return 0.0

    dst, indices = distance_transform(gt_arr == 0, return_indices=True)
    error = np.abs(pred_arr - gt_arr.astype(np.float64))
    propagated_error = np.copy(error)
    propagated_error[~gt_arr] = propagated_error[
        indices[0][~gt_arr], indices[1][~gt_arr]
    ]

    gaussian = _matlab_style_gauss2d((7, 7), sigma=5)
    smoothed_error = convolve(
        propagated_error, weights=gaussian, mode="constant", cval=0.0
    )
    minimum_error = np.where(gt_arr & (smoothed_error < error), smoothed_error, error)

    importance = np.where(
        ~gt_arr,
        2.0 - np.exp(np.log(0.5) / 5.0 * dst),
        np.ones_like(pred_arr),
    )
    weighted_error = minimum_error * importance

    true_positive_weighted = np.sum(gt_arr) - np.sum(weighted_error[gt_arr])
    false_positive_weighted = np.sum(weighted_error[~gt_arr])
    recall = 1.0 - np.mean(weighted_error[gt_arr])
    precision = true_positive_weighted / (
        true_positive_weighted + false_positive_weighted + EPS
    )
    return float(
        (1.0 + beta2) * recall * precision / (recall + beta2 * precision + EPS)
    )
