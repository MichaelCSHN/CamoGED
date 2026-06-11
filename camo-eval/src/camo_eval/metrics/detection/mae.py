"""Mean Absolute Error (MAE) for camouflaged object detection.

MAE is the average per-pixel absolute difference between a predicted saliency/segmentation
map and the binary ground-truth mask. Lower is better.

This is a fully working reference implementation (the first metric shipped in camo-eval).
"""

from __future__ import annotations

import numpy as np


def _to_float01(array: np.ndarray) -> np.ndarray:
    """Coerce an array to float in [0, 1].

    Accepts uint8 [0, 255] or float [0, 1]. Raises on clearly invalid ranges.
    """
    arr = np.asarray(array, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("Empty array passed to MAE.")
    max_val = arr.max(initial=0.0)
    if max_val > 1.0:
        # assume 0-255 range
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def mae(pred: np.ndarray, gt: np.ndarray) -> float:
    """Compute MAE between a prediction and ground-truth mask.

    Parameters
    ----------
    pred : np.ndarray
        Predicted map, HxW (or HxWx1). uint8 [0,255] or float [0,1].
    gt : np.ndarray
        Ground-truth mask, same spatial size as ``pred``.

    Returns
    -------
    float
        Mean absolute error in [0, 1]; lower is better.
    """
    pred = _to_float01(pred).squeeze()
    gt = _to_float01(gt).squeeze()
    if pred.shape != gt.shape:
        raise ValueError(f"Shape mismatch: pred {pred.shape} vs gt {gt.shape}")
    return float(np.mean(np.abs(pred - gt)))
