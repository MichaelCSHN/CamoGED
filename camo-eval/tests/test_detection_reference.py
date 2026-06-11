import warnings

import numpy as np
import pytest

from camo_eval import (
    e_measure,
    f_measure,
    mae,
    precision,
    precision_recall_curve,
    recall,
    s_measure,
    weighted_f_measure,
)

py_sod_metrics = pytest.importorskip("py_sod_metrics")


FIXTURES = [
    (
        np.array([[0, 64, 128], [255, 192, 32], [16, 80, 240]], dtype=np.uint8),
        np.array([[0, 0, 255], [255, 255, 0], [0, 255, 255]], dtype=np.uint8),
    ),
    (
        np.array([[255, 255], [255, 255]], dtype=np.uint8),
        np.array([[255, 0], [0, 255]], dtype=np.uint8),
    ),
    (
        np.array([[0, 32, 64], [96, 128, 160], [192, 224, 255]], dtype=np.uint8),
        np.array([[0, 0, 0], [255, 255, 255], [255, 0, 0]], dtype=np.uint8),
    ),
    (
        np.array([[10, 10, 10], [10, 10, 10], [10, 10, 10]], dtype=np.uint8),
        np.array([[0, 255, 0], [255, 255, 255], [0, 255, 0]], dtype=np.uint8),
    ),
    (
        np.array([[0, 255, 0, 255], [255, 0, 255, 0]], dtype=np.uint8),
        np.array([[0, 255, 255, 0], [255, 0, 0, 255]], dtype=np.uint8),
    ),
]


def _reference_metrics(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f_metric = py_sod_metrics.Fmeasure()
        e_metric = py_sod_metrics.Emeasure()
        s_metric = py_sod_metrics.Smeasure()
        w_metric = py_sod_metrics.WeightedFmeasure()
        m_metric = py_sod_metrics.MAE()

    for metric in (f_metric, e_metric, s_metric, w_metric, m_metric):
        metric.step(pred, gt)

    f_results = f_metric.get_results()["fm"]
    e_results = e_metric.get_results()["em"]
    return {
        "mae": float(m_metric.get_results()["mae"]),
        "weighted_f_measure": float(w_metric.get_results()["wfm"]),
        "s_measure": float(s_metric.get_results()["sm"]),
        "f_max": float(f_results["curve"].max()),
        "f_mean": float(f_results["curve"].mean()),
        "f_adaptive": float(f_results["adp"]),
        "e_max": float(e_results["curve"].max()),
        "e_mean": float(e_results["curve"].mean()),
        "e_adaptive": float(e_results["adp"]),
    }


@pytest.mark.parametrize(("pred", "gt"), FIXTURES)
def test_detection_metrics_match_pysodmetrics(pred: np.ndarray, gt: np.ndarray):
    """Reference source: `PySODMetrics` 1.6.2 (`py_sod_metrics.sod_metrics`)."""

    expected = _reference_metrics(pred, gt)
    f_actual = f_measure(pred, gt)
    e_actual = e_measure(pred, gt)

    assert mae(pred, gt) == pytest.approx(expected["mae"], abs=1e-4)
    assert weighted_f_measure(pred, gt) == pytest.approx(
        expected["weighted_f_measure"], abs=1e-4
    )
    assert s_measure(pred, gt) == pytest.approx(expected["s_measure"], abs=1e-4)
    assert f_actual["max"] == pytest.approx(expected["f_max"], abs=1e-4)
    assert f_actual["mean"] == pytest.approx(expected["f_mean"], abs=1e-4)
    assert f_actual["adaptive"] == pytest.approx(expected["f_adaptive"], abs=1e-4)
    assert e_actual["max"] == pytest.approx(expected["e_max"], abs=1e-4)
    assert e_actual["mean"] == pytest.approx(expected["e_mean"], abs=1e-4)
    assert e_actual["adaptive"] == pytest.approx(expected["e_adaptive"], abs=1e-4)


@pytest.mark.parametrize(
    "metric", [mae, weighted_f_measure, s_measure, e_measure, f_measure]
)
def test_detection_metrics_reject_empty_arrays(metric):
    with pytest.raises(ValueError):
        metric(np.array([]), np.array([]))


@pytest.mark.parametrize(
    "metric", [mae, weighted_f_measure, s_measure, e_measure, f_measure]
)
def test_detection_metrics_reject_nan_inputs(metric):
    pred = np.array([[0.0, np.nan], [1.0, 0.5]])
    gt = np.array([[0, 1], [1, 0]])
    with pytest.raises(ValueError):
        metric(pred, gt)


def test_detection_metrics_handle_single_pixel_inputs():
    pred = np.array([[255]], dtype=np.uint8)
    gt = np.array([[255]], dtype=np.uint8)

    assert mae(pred, gt) == pytest.approx(0.0)
    assert weighted_f_measure(pred, gt) == pytest.approx(1.0)
    assert s_measure(pred, gt) == pytest.approx(1.0)
    assert e_measure(pred, gt)["adaptive"] == pytest.approx(1.0)
    assert f_measure(pred, gt)["adaptive"] == pytest.approx(1.0)
    assert precision(pred, gt)["adaptive"] == pytest.approx(1.0)
    assert recall(pred, gt)["adaptive"] == pytest.approx(1.0)


def test_precision_recall_curve_shapes_and_bounds():
    pred = np.array([[0, 64, 128], [255, 192, 32]], dtype=np.uint8)
    gt = np.array([[0, 0, 255], [255, 255, 0]], dtype=np.uint8)
    curve = precision_recall_curve(pred, gt)

    assert curve["thresholds"].shape == (256,)
    assert curve["precision"].shape == (256,)
    assert curve["recall"].shape == (256,)
    assert np.all(curve["precision"] >= 0.0)
    assert np.all(curve["precision"] <= 1.0)
    assert np.all(curve["recall"] >= 0.0)
    assert np.all(curve["recall"] <= 1.0)


def test_weighted_f_measure_all_background_matches_reference_behavior():
    pred = np.zeros((3, 3), dtype=np.uint8)
    gt = np.zeros((3, 3), dtype=np.uint8)
    assert weighted_f_measure(pred, gt) == pytest.approx(0.0)
