"""Video metrics with experimental boundary semantics explicitly named."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation

from ..detection._common import EPS, prepare_prediction_and_gt
from ..instance import _boundary_mask, iou


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
    pred_norm, gt_norm = [], []
    for pred_frame, gt_frame in zip(pred_arr, gt_arr):
        pred_prepared, gt_prepared = prepare_prediction_and_gt(pred_frame, gt_frame)
        pred_norm.append(pred_prepared)
        gt_norm.append(gt_prepared.astype(bool))
    return np.stack(pred_norm), np.stack(gt_norm)


def jaccard_index(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    return float(
        np.mean(
            [
                iou(pred_frame, gt_frame.astype(np.uint8))
                for pred_frame, gt_frame in zip(pred_arr, gt_arr)
            ]
        )
    )


def boundary_f_score(
    pred_frames: np.ndarray, gt_frames: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    raise NotImplementedError(
        "DAVIS boundary F is not yet validated against the official evaluator. Use boundary_f_score_lite only as an explicitly experimental score."
    )


def boundary_f_score_lite(
    pred_frames: np.ndarray, gt_frames: np.ndarray, dilation_ratio: float = 0.02
) -> float:
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
    raise NotImplementedError(
        "Official DAVIS J&F is not yet validated. Use j_and_f_lite only for experimental internal checks."
    )


def j_and_f_lite(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    return float(
        (
            jaccard_index(pred_frames, gt_frames)
            + boundary_f_score_lite(pred_frames, gt_frames)
        )
        / 2.0
    )


def temporal_stability(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    """Mean absolute difference between predicted and GT temporal derivatives; lower is better."""

    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    if pred_arr.shape[0] < 2:
        return 0.0
    return float(
        np.mean(
            np.abs(
                np.diff(pred_arr, axis=0) - np.diff(gt_arr.astype(np.float64), axis=0)
            )
        )
    )
