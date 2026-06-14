"""Regression tests for detection-metric input handling.

These run without the optional ``pysodmetrics`` reference dependency so the
invariants below are always enforced in CI.
"""

import numpy as np
import pytest

from camo_eval import e_measure, f_measure, mae, s_measure, weighted_f_measure

DETECTION_SCALARS = [mae, s_measure, weighted_f_measure]


@pytest.mark.parametrize("metric", DETECTION_SCALARS)
def test_uint8_and_float_predictions_agree(metric):
    """A prediction must score identically whether passed as uint8 [0,255] or
    the equivalent float [0,1] (`pred / 255`). Regression for the normalization
    asymmetry where only the uint8 path was min-max stretched."""
    rng = np.random.default_rng(0)
    gt = (rng.random((24, 24)) > 0.5).astype(np.uint8)
    pred_u8 = (rng.random((24, 24)) * 180 + 20).astype(np.uint8)  # partial range
    pred_f = pred_u8.astype(np.float64) / 255.0

    assert metric(pred_u8, gt) == pytest.approx(metric(pred_f, gt), abs=1e-9)


@pytest.mark.parametrize("metric", [e_measure, f_measure])
def test_uint8_and_float_dict_metrics_agree(metric):
    rng = np.random.default_rng(1)
    gt = (rng.random((24, 24)) > 0.5).astype(np.uint8)
    pred_u8 = (rng.random((24, 24)) * 180 + 20).astype(np.uint8)
    pred_f = pred_u8.astype(np.float64) / 255.0

    got_u8 = metric(pred_u8, gt)
    got_f = metric(pred_f, gt)
    assert got_u8.keys() == got_f.keys()
    for key in got_u8:
        assert got_u8[key] == pytest.approx(got_f[key], abs=1e-9)


def test_single_pixel_float_prediction_not_truncated():
    """A near-correct single-pixel float prediction must not be truncated to a
    total miss. Regression for `pred.astype(np.uint8)` in the E-measure curve."""
    scores = e_measure(np.array([[0.99]]), np.array([[1]]))
    assert scores["mean"] == pytest.approx(1.0)
    assert scores["max"] == pytest.approx(1.0)

    miss = e_measure(np.array([[0.2]]), np.array([[1]]))
    assert miss["mean"] == pytest.approx(0.0)
    assert miss["max"] == pytest.approx(0.0)
