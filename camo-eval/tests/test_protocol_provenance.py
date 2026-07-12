import json

import numpy as np

from camo_eval.cli import main


def test_evaluate_protocol_preserves_provenance(tmp_path, capsys):
    pred_dir = tmp_path / "pred"
    gt_dir = tmp_path / "gt"
    pred_dir.mkdir()
    gt_dir.mkdir()
    np.save(pred_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))
    np.save(gt_dir / "sample.npy", np.array([[0, 255], [255, 0]], dtype=np.uint8))

    manifest = {
        "name": "provenance-test",
        "observer": "model",
        "channel": "rgb",
        "task": "image-cod",
        "protocol": "fixed synthetic fixture",
        "notes": "regression test",
        "implementation_version": "0.2.0.dev0",
        "dataset_version": "fixture-v1",
        "prediction_revision": "pred-abc123",
        "threshold_policy": "0.5 for binary helpers",
        "seed": 42,
        "environment": "pytest",
        "uncertainty": "not applicable",
        "pred_dir": "pred",
        "gt_dir": "gt",
        "metrics": ["mae", "iou"],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    exit_code = main(["evaluate-protocol", "--manifest", str(manifest_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["context"]["dataset_version"] == "fixture-v1"
    assert payload["context"]["prediction_revision"] == "pred-abc123"
    assert payload["context"]["threshold_policy"] == "0.5 for binary helpers"
    assert payload["context"]["seed"] == 42
    assert payload["context"]["environment"] == "pytest"
    assert payload["context"]["uncertainty"] == "not applicable"
