import numpy as np
import pytest

from camo_eval import (
    ResultsTable,
    ap_drop,
    attack_success_rate,
    evaluate,
    to_latex,
    to_markdown,
    transferability,
)


def test_runner_and_export_roundtrip(tmp_path):
    pred_dir = tmp_path / "pred"
    gt_dir = tmp_path / "gt"
    pred_dir.mkdir()
    gt_dir.mkdir()

    np.save(pred_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))
    np.save(gt_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))

    results = evaluate(pred_dir, gt_dir, ["mae", "fw", "sm"])

    assert isinstance(results, ResultsTable)
    assert results.rows[0]["samples"] == 1
    markdown = to_markdown(results)
    latex = to_latex(results)
    assert "MAE" in markdown
    assert "\\begin{tabular}" in latex


def test_attack_success_rate_and_transferability():
    clean = [0.9, 0.8, 0.7]
    attacked = [0.1, 0.3, 0.9]

    asr = attack_success_rate(clean, attacked, lambda c, a: a < c)
    assert asr == pytest.approx(2 / 3)
    assert ap_drop(0.82, 0.51) == pytest.approx(0.31)

    summary = transferability({"a": 0.4, "b": 0.7})
    assert summary["mean"] == pytest.approx(0.55)
    assert summary["min"] == pytest.approx(0.4)
    assert summary["max"] == pytest.approx(0.7)


def test_attack_success_rate_validates_lengths():
    with pytest.raises(ValueError):
        attack_success_rate([1], [1, 2], lambda c, a: True)
