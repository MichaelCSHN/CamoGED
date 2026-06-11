"""Mean Absolute Error (MAE) for camouflaged object detection."""

from __future__ import annotations

import numpy as np

from ._common import prepare_prediction_and_gt


def mae(pred: np.ndarray, gt: np.ndarray) -> float:
    """Compute the average per-pixel absolute error."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    return float(np.mean(np.abs(pred_arr - gt_arr.astype(np.float64))))
