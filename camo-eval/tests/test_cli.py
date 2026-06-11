import json

import numpy as np

from camo_eval.cli import main


def test_cli_list_metrics_json(capsys):
    exit_code = main(["list-metrics", "--format", "json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert "detection" in payload
    assert "video" in payload


def test_cli_evaluate_markdown(tmp_path, capsys):
    pred_dir = tmp_path / "pred"
    gt_dir = tmp_path / "gt"
    pred_dir.mkdir()
    gt_dir.mkdir()

    np.save(pred_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))
    np.save(gt_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))

    exit_code = main(
        [
            "evaluate",
            "--pred-dir",
            str(pred_dir),
            "--gt-dir",
            str(gt_dir),
            "--metrics",
            "mae",
            "iou",
            "ssim",
            "--format",
            "markdown",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "| MAE |" in captured.out
    assert "IoU" in captured.out


def test_cli_protocol_template_json(capsys):
    exit_code = main(
        [
            "protocol-template",
            "--observer",
            "model",
            "--channel",
            "rgb",
            "--task",
            "image-cod",
            "--protocol",
            "COD10K test split",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["context"]["protocol"] == "COD10K test split"
