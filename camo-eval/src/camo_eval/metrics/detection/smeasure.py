"""S-measure (structure measure)."""

from __future__ import annotations

import numpy as np

from ._common import EPS, prepare_prediction_and_gt


def _object_score(region: np.ndarray) -> float:
    mean = float(np.mean(region))
    if region.size > 1:
        std = float(np.std(region, ddof=1))
    else:
        std = 0.0
    return 2.0 * mean / (mean * mean + 1.0 + std + EPS)


def _ssim(pred: np.ndarray, gt: np.ndarray) -> float:
    h, w = pred.shape
    size = h * w
    pred_mean = float(np.mean(pred))
    gt_mean = float(np.mean(gt))

    sigma_pred = float(np.sum((pred - pred_mean) ** 2) / (size - 1 + EPS))
    sigma_gt = float(np.sum((gt - gt_mean) ** 2) / (size - 1 + EPS))
    sigma_cross = float(np.sum((pred - pred_mean) * (gt - gt_mean)) / (size - 1 + EPS))

    numerator = 4.0 * pred_mean * gt_mean * sigma_cross
    denominator = (pred_mean**2 + gt_mean**2) * (sigma_pred + sigma_gt)
    if numerator != 0:
        return numerator / (denominator + EPS)
    if numerator == 0 and denominator == 0:
        return 1.0
    return 0.0


def _region_score(pred: np.ndarray, gt: np.ndarray) -> float:
    h, w = gt.shape
    area = h * w
    if np.count_nonzero(gt) == 0:
        cy, cx = np.round(h / 2), np.round(w / 2)
    else:
        cy, cx = np.argwhere(gt).mean(axis=0).round()
    cy, cx = int(cy) + 1, int(cx) + 1

    w_lt = cx * cy / area
    w_rt = cy * (w - cx) / area
    w_lb = (h - cy) * cx / area
    w_rb = 1.0 - w_lt - w_rt - w_lb

    score_lt = _ssim(pred[0:cy, 0:cx], gt[0:cy, 0:cx]) * w_lt
    score_rt = _ssim(pred[0:cy, cx:w], gt[0:cy, cx:w]) * w_rt
    score_lb = _ssim(pred[cy:h, 0:cx], gt[cy:h, 0:cx]) * w_lb
    score_rb = _ssim(pred[cy:h, cx:w], gt[cy:h, cx:w]) * w_rb
    return float(score_lt + score_rt + score_lb + score_rb)


def s_measure(pred: np.ndarray, gt: np.ndarray, alpha: float = 0.5) -> float:
    """Compute S-measure following Fan et al. (ICCV 2017)."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    gt_mean = float(np.mean(gt_arr))
    if gt_mean == 0.0:
        return float(1.0 - np.mean(pred_arr))
    if gt_mean == 1.0:
        return float(np.mean(pred_arr))

    foreground = _object_score(pred_arr[gt_arr]) * gt_mean
    background = _object_score((1.0 - pred_arr)[~gt_arr]) * (1.0 - gt_mean)
    object_term = foreground + background
    region_term = _region_score(pred_arr, gt_arr.astype(np.float64))
    return float(max(0.0, alpha * object_term + (1.0 - alpha) * region_term))
