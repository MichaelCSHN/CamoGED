import json
from pathlib import Path

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


def test_cli_protocol_template_manifest_json(capsys):
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
            "demo manifest",
            "--name",
            "rgb_masks_demo",
            "--pred-dir",
            "pred",
            "--gt-dir",
            "gt",
            "--metrics",
            "mae",
            "iou",
            "--pred-source",
            "demo/pred",
            "--gt-source",
            "demo/gt",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["name"] == "rgb_masks_demo"
    assert payload["pred_dir"] == "pred"
    assert payload["metrics"] == ["mae", "iou"]
    assert payload["pred_source"] == "demo/pred"


def test_cli_evaluate_report_json(tmp_path, capsys):
    pred_dir = tmp_path / "pred"
    gt_dir = tmp_path / "gt"
    pred_dir.mkdir()
    gt_dir.mkdir()

    np.save(pred_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))
    np.save(gt_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))

    exit_code = main(
        [
            "evaluate-report",
            "--pred-dir",
            str(pred_dir),
            "--gt-dir",
            str(gt_dir),
            "--metrics",
            "mae",
            "iou",
            "--observer",
            "model",
            "--channel",
            "rgb",
            "--task",
            "image-cod",
            "--protocol",
            "demo protocol",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["context"]["protocol"] == "demo protocol"
    assert payload["metrics"]["samples"] == 1
    assert payload["artifacts"]["pred_dir"] == str(pred_dir.resolve())


def test_cli_evaluate_report_writes_markdown_file(tmp_path):
    pred_dir = tmp_path / "pred"
    gt_dir = tmp_path / "gt"
    output_path = tmp_path / "report.md"
    pred_dir.mkdir()
    gt_dir.mkdir()

    np.save(pred_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))
    np.save(gt_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))

    exit_code = main(
        [
            "evaluate-report",
            "--pred-dir",
            str(pred_dir),
            "--gt-dir",
            str(gt_dir),
            "--metrics",
            "mae",
            "iou",
            "--observer",
            "model",
            "--channel",
            "rgb",
            "--task",
            "image-cod",
            "--protocol",
            "written demo",
            "--format",
            "markdown",
            "--output",
            str(output_path),
        ]
    )
    assert exit_code == 0
    text = output_path.read_text(encoding="utf-8")
    assert "written demo" in text
    assert "| Metric | Value |" in text


def test_demo_dataset_files_exist():
    demo_root = Path(__file__).resolve().parents[1] / "demo_data" / "rgb_masks"
    assert (demo_root / "manifest.json").exists()
    assert (demo_root / "pred" / "sample1.pgm").exists()
    assert (demo_root / "gt" / "sample1.pgm").exists()


def test_cli_evaluate_protocol_from_manifest(capsys):
    demo_root = Path(__file__).resolve().parents[1] / "demo_data" / "rgb_masks"
    exit_code = main(
        [
            "evaluate-protocol",
            "--manifest",
            str(demo_root / "manifest.json"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["context"]["protocol"] == "repository demo bundle"
    assert payload["artifacts"]["bundle_name"] == "rgb_masks_demo"
    assert payload["artifacts"]["pred_source"] == "demo_data/rgb_masks/pred"
