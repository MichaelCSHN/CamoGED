import json

import numpy as np
import pytest

from camo_eval import (
    EvaluationContext,
    EvaluationReport,
    boundary_f_score,
    boundary_iou,
    camouflage_difficulty,
    deception_rate,
    dice,
    dists,
    edge_density,
    feature_congestion,
    fid,
    iou,
    j_and_f,
    jaccard_index,
    kid,
    lpips,
    ms_ssim,
    signal_to_clutter_ratio,
    spectral_angle_mapper,
    ssim,
    subband_entropy,
    target_background_similarity,
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


def test_lightweight_generation_pair_metrics_perfect_match():
    img = np.tile(np.linspace(0.0, 1.0, 16), (16, 1))
    changed = np.fliplr(img)
    assert lpips(img, img) == pytest.approx(0.0)
    assert dists(img, img) == pytest.approx(0.0)
    assert lpips(img, changed) > 0
    assert dists(img, changed) > 0


def test_lightweight_generation_directory_metrics(tmp_path):
    real_dir = tmp_path / "real"
    fake_dir = tmp_path / "fake"
    real_dir.mkdir()
    fake_dir.mkdir()

    base = np.tile(np.linspace(0.0, 1.0, 16), (16, 1))
    alt = np.flipud(base)
    np.save(real_dir / "a.npy", base)
    np.save(real_dir / "b.npy", alt)
    np.save(fake_dir / "a.npy", base)
    np.save(fake_dir / "b.npy", np.clip(alt + 0.1, 0.0, 1.0))

    assert fid(str(real_dir), str(real_dir)) == pytest.approx(0.0)
    assert fid(str(real_dir), str(fake_dir)) >= 0
    assert np.isfinite(kid(str(real_dir), str(fake_dir)))


def test_deception_rate_sequence_and_callable_targets():
    def detector(item):
        return {"label": item, "score": 0.2 if item == "hidden" else 0.9}

    assert deception_rate(detector, ["hidden", "visible"], ["hidden", "hidden"]) == 0.5
    assert deception_rate(detector, ["hidden", "visible"], lambda out: out["score"] < 0.5) == 0.5


def test_clutter_and_camouflage_difficulty_metrics():
    image = np.tile(np.linspace(0.0, 1.0, 16), (16, 1))
    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[5:11, 5:11] = 1

    assert 0 <= edge_density(image) <= 1
    assert 0 <= subband_entropy(image) <= 1
    assert feature_congestion(image) >= 0

    difficulty = camouflage_difficulty(image, mask)
    assert 0 <= difficulty["difficulty"] <= 1
    assert "near_histogram_intersection" in difficulty


def test_signature_metrics_basic_behavior():
    target = np.array([10.0, 12.0, 14.0])
    background = np.array([4.0, 5.0, 6.0])
    assert thermal_contrast(target, background) == pytest.approx(7.0)
    assert signal_to_clutter_ratio(target, background) > 0
    assert spectral_angle_mapper(np.array([1.0, 0.0]), np.array([1.0, 0.0])) == pytest.approx(0.0)


def test_target_background_similarity_all_and_near_modes():
    image = np.array(
        [
            [0.2, 0.2, 0.3, 0.4],
            [0.2, 0.8, 0.8, 0.4],
            [0.3, 0.8, 0.7, 0.4],
            [0.2, 0.3, 0.3, 0.4],
        ]
    )
    mask = np.array(
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ]
    )

    all_background = target_background_similarity(image, mask, mode="all")
    near_background = target_background_similarity(image, mask, mode="near")

    assert all_background["mean_abs_diff"] > 0
    assert near_background["mean_abs_diff"] > 0
    assert 0 <= all_background["histogram_intersection"] <= 1
    assert 0 <= near_background["histogram_intersection"] <= 1


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


def test_report_markdown_flattens_nested_metric_dicts():
    """Dict-valued metrics (e.g. Em) must flatten to dotted rows, not render as
    raw Python ``dict`` reprs in the Markdown table."""
    context = EvaluationContext(
        observer="model", channel="rgb", task="image-cod", protocol="demo"
    )
    report = EvaluationReport(
        context=context,
        metrics={"COD core": {"MAE": 0.1, "Em": {"mean": 0.7, "max": 0.9}}},
    )
    markdown = report.to_markdown()
    assert "| COD core.MAE | 0.1 |" in markdown
    assert "| COD core.Em.mean | 0.7 |" in markdown
    assert "| COD core.Em.max | 0.9 |" in markdown
    assert "{" not in markdown  # no raw dict repr leaked
