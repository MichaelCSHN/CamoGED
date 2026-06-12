import json
from pathlib import Path

import numpy as np
import pytest

from camo_eval.cli import main


def test_cli_list_metrics_json(capsys):
    exit_code = main(["list-metrics", "--format", "json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert "detection" in payload
    assert "video" in payload
    assert "generation" in payload
    assert "clutter" in payload
    assert "precision" in payload["detection"]
    assert "recall" in payload["detection"]
    assert "fid_lite" in payload["generation"]
    assert "camouflage_difficulty" in payload["clutter"]


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
            "lpips_lite",
            "--format",
            "markdown",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "| MAE |" in captured.out
    assert "IoU" in captured.out
    assert "LPIPS_lite" in captured.out


def test_cli_generation_distance_json(tmp_path, capsys):
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

    exit_code = main(
        [
            "generation-distance",
            "--real-dir",
            str(real_dir),
            "--fake-dir",
            str(fake_dir),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert "FID_lite" in payload
    assert "KID_lite" in payload


def test_cli_image_diagnostics_json(tmp_path, capsys):
    image_path = tmp_path / "image.npy"
    mask_path = tmp_path / "mask.npy"
    image = np.tile(np.linspace(0.0, 1.0, 16), (16, 1))
    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[5:11, 5:11] = 1
    np.save(image_path, image)
    np.save(mask_path, mask)

    exit_code = main(
        [
            "image-diagnostics",
            "--image",
            str(image_path),
            "--mask",
            str(mask_path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert "edge_density" in payload
    assert "camouflage_difficulty" in payload


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

    cod_demo_root = Path(__file__).resolve().parents[1] / "demo_data" / "cod_sota_masks"
    assert (cod_demo_root / "manifest.json").exists()
    assert (cod_demo_root / "pred" / "sample1.png").exists()
    assert (cod_demo_root / "gt" / "sample1.png").exists()


def test_cli_evaluate_protocol_from_manifest(capsys):
    pytest.importorskip("PIL")
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
    assert "P_adaptive" in payload["metrics"]
    assert "R_adaptive" in payload["metrics"]


def test_cli_visualize_outputs_demo_artifacts(tmp_path, capsys):
    pytest.importorskip("PIL")
    pytest.importorskip("matplotlib")
    demo_root = Path(__file__).resolve().parents[1] / "demo_data" / "cod_sota_masks"
    output_dir = tmp_path / "visual"
    exit_code = main(
        [
            "visualize",
            "--pred",
            str(demo_root / "pred" / "sample1.png"),
            "--gt",
            str(demo_root / "gt" / "sample1.png"),
            "--output-dir",
            str(output_dir),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert Path(payload["mask_overlay"]).exists()
    assert Path(payload["error_map"]).exists()
    assert Path(payload["pr_curve"]).exists()
    assert Path(payload["scores"]).exists()

    scores = json.loads(Path(payload["scores"]).read_text(encoding="utf-8"))
    assert "MAE" in scores
    assert "P_adaptive" in scores
    assert "R_adaptive" in scores
