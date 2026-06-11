import json

import numpy as np
import pytest

from camo_eval import (
    EvaluationContext,
    EvaluationReport,
    boundary_f_score,
    boundary_iou,
    dice,
    iou,
    j_and_f,
    jaccard_index,
    ms_ssim,
    signal_to_clutter_ratio,
    spectral_angle_mapper,
    ssim,
    temporal_stability,
    thermal_contrast,
)


def test_instance_metrics_perfect_overlap():
    pred = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    gt = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    assert iou(pred, gt) == pytest.approx(1.0)
    assert dice(pred, gt) == pytest.approx(1.0)
    assert boundary_iou(pred, gt) == pytest.approx(1.0)


def test_perceptual_metrics_perfect_match():
    img = np.array([[0.0, 1.0], [1.0, 0.0]])
    assert ssim(img, img) == pytest.approx(1.0)
    assert ms_ssim(img, img) == pytest.approx(1.0)


def test_signature_metrics_basic_behavior():
    target = np.array([10.0, 12.0, 14.0])
    background = np.array([4.0, 5.0, 6.0])
    assert thermal_contrast(target, background) == pytest.approx(7.0)
    assert signal_to_clutter_ratio(target, background) > 0
    assert spectral_angle_mapper(
        np.array([1.0, 0.0]), np.array([1.0, 0.0])
    ) == pytest.approx(0.0)


def test_video_metrics_basic_behavior():
    pred = np.array(
        [
            [[0, 255], [255, 0]],
            [[0, 255], [255, 0]],
        ],
        dtype=np.uint8,
    )
    gt = pred.copy()
    assert jaccard_index(pred, gt) == pytest.approx(1.0)
    assert boundary_f_score(pred, gt) == pytest.approx(1.0)
    assert j_and_f(pred, gt) == pytest.approx(1.0)
    assert temporal_stability(pred, gt) == pytest.approx(0.0)


def test_protocol_report_roundtrip():
    context = EvaluationContext(
        observer="model",
        channel="rgb",
        task="image-cod",
        protocol="COD10K test split",
        notes="demo",
    )
    report = EvaluationReport(context=context, metrics={"MAE": 0.1})
    payload = json.loads(report.to_json())
    assert payload["context"]["observer"] == "model"
    assert payload["metrics"]["MAE"] == pytest.approx(0.1)
    assert "| MAE | 0.1 |" in report.to_markdown()
