"""Batch evaluation entry point."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .metrics.detection import e_measure, f_measure, mae, s_measure, weighted_f_measure
from .results import ResultsTable


def _load_array(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npy":
        return np.load(path)
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Image loading requires Pillow for non-.npy inputs. "
            "Install with `pip install pillow` or use .npy files."
        ) from exc
    return np.asarray(Image.open(path))


def _index_files(directory: Path) -> dict[str, Path]:
    return {path.stem: path for path in directory.iterdir() if path.is_file()}


def _metric_value(name: str, pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    key = name.lower()
    if key in {"mae"}:
        return {"MAE": mae(pred, gt)}
    if key in {"weighted_f_measure", "fw"}:
        return {"Fw": weighted_f_measure(pred, gt)}
    if key in {"s_measure", "sm"}:
        return {"Sm": s_measure(pred, gt)}
    if key in {"e_measure", "em"}:
        return {f"Em_{subkey}": value for subkey, value in e_measure(pred, gt).items()}
    if key in {"f_measure", "f"}:
        return {f"F_{subkey}": value for subkey, value in f_measure(pred, gt).items()}
    raise KeyError(f"Unsupported metric '{name}'.")


def evaluate(pred_dir, gt_dir, metrics: list[str]) -> ResultsTable:
    """Evaluate matching files by basename across two directories."""

    pred_path = Path(pred_dir)
    gt_path = Path(gt_dir)
    pred_files = _index_files(pred_path)
    gt_files = _index_files(gt_path)
    basenames = sorted(set(pred_files) & set(gt_files))
    if not basenames:
        raise ValueError("No matching prediction/ground-truth files found by basename.")

    aggregates: dict[str, list[float]] = {}
    for basename in basenames:
        pred = _load_array(pred_files[basename])
        gt = _load_array(gt_files[basename])
        for metric in metrics:
            values = _metric_value(metric, pred, gt)
            for key, value in values.items():
                aggregates.setdefault(key, []).append(float(value))

    row = {"samples": len(basenames)}
    for key in sorted(aggregates):
        row[key] = float(np.mean(aggregates[key]))
    return ResultsTable(rows=[row], columns=list(row.keys()))
