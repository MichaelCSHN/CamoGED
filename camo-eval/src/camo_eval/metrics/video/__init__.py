"""Video metrics for sequential camouflage evaluation."""

from __future__ import annotations

import numpy as np

from ..instance import _boundary_mask, iou
from ..detection._common import EPS, prepare_prediction_and_gt


def _prepare_sequence_pair(
    pred_frames: np.ndarray, gt_frames: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    pred_arr = np.asarray(pred_frames)
    gt_arr = np.asarray(gt_frames)
    if pred_arr.ndim == 2 and gt_arr.ndim == 2:
        pred_arr = pred_arr[None, ...]
        gt_arr = gt_arr[None, ...]
    if pred_arr.ndim != 3 or gt_arr.ndim != 3:
        raise ValueError(
            "Video metrics expect [T, H, W] arrays or single [H, W] masks."
        )
    if pred_arr.shape != gt_arr.shape:
        raise ValueError(f"Shape mismatch: {pred_arr.shape} vs {gt_arr.shape}")

    pred_norm = []
    gt_norm = []
    for pred_frame, gt_frame in zip(pred_arr, gt_arr):
        pred_prepared, gt_prepared = prepare_prediction_and_gt(pred_frame, gt_frame)
        pred_norm.append(pred_prepared)
        gt_norm.append(gt_prepared.astype(bool))
    return np.stack(pred_norm, axis=0), np.stack(gt_norm, axis=0)


def jaccard_index(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    """Average region Jaccard score across video frames."""

    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    scores = [
        iou(pred_frame, gt_frame.astype(np.uint8))
        for pred_frame, gt_frame in zip(pred_arr, gt_arr)
    ]
    return float(np.mean(scores))


def boundary_f_score(
    pred_frames: np.ndarray, gt_frames: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    """Average boundary F-score across video frames."""

    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    scores = []
    for pred_frame, gt_frame in zip(pred_arr, gt_arr):
        pred_mask = pred_frame >= 0.5
        gt_mask = gt_frame.astype(bool)
        pred_boundary = _boundary_mask(pred_mask)
        gt_boundary = _boundary_mask(gt_mask)
        if not np.any(pred_boundary) and not np.any(gt_boundary):
            scores.append(1.0)
            continue

        h, w = pred_mask.shape
        dilation = max(1, int(round(dilation_ratio * np.hypot(h, w))))
        from scipy.ndimage import binary_dilation

        structure = np.ones((3, 3), dtype=bool)
        pred_dilated = binary_dilation(
            pred_boundary, structure=structure, iterations=dilation
        )
        gt_dilated = binary_dilation(
            gt_boundary, structure=structure, iterations=dilation
        )

        pred_match = np.count_nonzero(pred_boundary & gt_dilated)
        gt_match = np.count_nonzero(gt_boundary & pred_dilated)
        precision = pred_match / (np.count_nonzero(pred_boundary) + EPS)
        recall = gt_match / (np.count_nonzero(gt_boundary) + EPS)
        scores.append(float((2 * precision * recall) / (precision + recall + EPS)))
    return float(np.mean(scores))


def j_and_f(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    """Compute the DAVIS-style mean of J and boundary F."""

    j_score = jaccard_index(pred_frames, gt_frames)
    f_score = boundary_f_score(pred_frames, gt_frames)
    return float((j_score + f_score) / 2.0)


def temporal_stability(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    """Compare temporal derivatives of predicted and ground-truth masks.

    Lower values are better.
    """

    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    if pred_arr.shape[0] < 2:
        return 0.0
    pred_delta = np.diff(pred_arr, axis=0)
    gt_delta = np.diff(gt_arr.astype(np.float64), axis=0)
    return float(np.mean(np.abs(pred_delta - gt_delta)))
