"""Batch evaluation entry point."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .metrics.detection import (
    e_measure,
    f_measure,
    mae,
    precision,
    recall,
    s_measure,
    weighted_f_measure,
)
from .metrics.generation import dists_lite, lpips_lite
from .metrics.instance import boundary_match_score, dice, iou
from .metrics.perceptual import ms_ssim_lite, ssim
from .metrics.video import (
    boundary_f_score_lite,
    j_and_f_lite,
    jaccard_index,
    temporal_stability,
)
from .results import ResultsTable


def _load_array(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npy":
        return np.load(path)
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Image loading requires Pillow for non-.npy inputs.") from exc
    return np.asarray(Image.open(path))


def _index_files(directory: Path) -> dict[str, Path]:
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"{directory} is not a directory")
    return {path.stem: path for path in directory.iterdir() if path.is_file()}


def _metric_value(name: str, pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    key = name.lower()
    if key == "mae":
        return {"MAE": mae(pred, gt)}
    if key in {"weighted_f_measure", "fw"}:
        return {"Fw": weighted_f_measure(pred, gt)}
    if key in {"s_measure", "sm"}:
        return {"Sm": s_measure(pred, gt)}
    if key in {"e_measure", "em"}:
        return {f"Em_{subkey}": value for subkey, value in e_measure(pred, gt).items()}
    if key in {"f_measure", "f"}:
        return {f"F_{subkey}": value for subkey, value in f_measure(pred, gt).items()}
    if key in {"precision", "p"}:
        return {f"P_{subkey}": value for subkey, value in precision(pred, gt).items()}
    if key in {"recall", "r"}:
        return {f"R_{subkey}": value for subkey, value in recall(pred, gt).items()}
    if key == "iou":
        return {"IoU": iou(pred, gt)}
    if key == "dice":
        return {"Dice": dice(pred, gt)}
    if key in {"boundary_match", "boundary_match_score"}:
        return {"BoundaryMatch": boundary_match_score(pred, gt)}
    if key == "ssim":
        return {"SSIM": ssim(pred, gt)}
    if key in {"ms_ssim_lite", "msssim_lite"}:
        return {"MS_SSIM_lite": ms_ssim_lite(pred, gt)}
    if key in {"lpips_lite", "perceptual_distance_lite"}:
        return {"LPIPS_lite": lpips_lite(pred, gt)}
    if key in {"dists_lite", "structure_texture_lite"}:
        return {"DISTS_lite": dists_lite(pred, gt)}
    if key in {"j", "jaccard"}:
        return {"J": jaccard_index(pred, gt)}
    if key in {"boundary_f_lite", "f_boundary_lite"}:
        return {"BoundaryF_lite": boundary_f_score_lite(pred, gt)}
    if key in {"jf_lite", "j_and_f_lite"}:
        return {"JF_lite": j_and_f_lite(pred, gt)}
    if key in {"temporal", "temporal_stability"}:
        return {"Temporal": temporal_stability(pred, gt)}
    if key in {
        "boundary_iou",
        "ms_ssim",
        "lpips",
        "dists",
        "boundary_f",
        "jf",
        "j_and_f",
    }:
        raise NotImplementedError(
            f"Metric {name!r} is a reserved standard name without a validated implementation in this release."
        )
    raise KeyError(f"Unsupported metric {name!r}.")


def evaluate(pred_dir, gt_dir, metrics: list[str]) -> ResultsTable:
    pred_files = _index_files(Path(pred_dir))
    gt_files = _index_files(Path(gt_dir))
    basenames = sorted(set(pred_files) & set(gt_files))
    if not basenames:
        raise ValueError("No matching prediction/ground-truth files found by basename.")
    aggregates: dict[str, list[float]] = {}
    for basename in basenames:
        pred = _load_array(pred_files[basename])
        gt = _load_array(gt_files[basename])
        for metric in metrics:
            for key, value in _metric_value(metric, pred, gt).items():
                aggregates.setdefault(key, []).append(float(value))
    row = {"samples": len(basenames)}
    row.update(
        {key: float(np.mean(values)) for key, values in sorted(aggregates.items())}
    )
    return ResultsTable(rows=[row], columns=list(row.keys()))
