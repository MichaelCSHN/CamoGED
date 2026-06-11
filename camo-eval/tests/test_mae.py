import numpy as np
from camo_eval import mae


def test_mae_identical_is_zero():
    a = np.array([[0, 1], [1, 0]], dtype=np.float64)
    assert mae(a, a) == 0.0


def test_mae_opposite_is_one():
    pred = np.zeros((4, 4))
    gt = np.ones((4, 4))
    assert mae(pred, gt) == 1.0


def test_mae_uint8_autoscale():
    pred = np.full((2, 2), 255, dtype=np.uint8)  # -> 1.0
    gt = np.zeros((2, 2), dtype=np.uint8)  # -> 0.0
    assert mae(pred, gt) == 1.0


def test_mae_half():
    pred = np.full((10, 10), 0.5)
    gt = np.zeros((10, 10))
    assert abs(mae(pred, gt) - 0.5) < 1e-9


def test_shape_mismatch_raises():
    import pytest

    with pytest.raises(ValueError):
        mae(np.zeros((2, 2)), np.zeros((3, 3)))
