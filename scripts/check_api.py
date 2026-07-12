#!/usr/bin/env python3
"""Check camo-eval public names and signatures, including evidence-explicit APIs."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "camo-eval/src"))

EXPECTED = {
    "camo_eval.metrics.detection": {
        "mae": ["pred", "gt"],
        "weighted_f_measure": ["pred", "gt", "beta2"],
        "s_measure": ["pred", "gt", "alpha"],
        "e_measure": ["pred", "gt"],
        "f_measure": ["pred", "gt"],
        "precision": ["pred", "gt"],
        "recall": ["pred", "gt"],
        "precision_recall_curve": ["pred", "gt"],
    },
    "camo_eval.metrics.generation": {
        "fid": ["real_dir", "fake_dir"],
        "fid_lite": ["real_dir", "fake_dir"],
        "kid": ["real_dir", "fake_dir", "degree", "gamma", "coef0"],
        "kid_lite": ["real_dir", "fake_dir", "degree", "gamma", "coef0"],
        "lpips": ["img_a", "img_b"],
        "lpips_lite": ["img_a", "img_b"],
        "dists": ["img_a", "img_b"],
        "dists_lite": ["img_a", "img_b"],
        "deception_rate": ["detector", "images", "targets"],
    },
    "camo_eval.metrics.instance": {
        "iou": ["pred", "gt"],
        "dice": ["pred", "gt"],
        "boundary_iou": ["pred", "gt", "dilation_ratio"],
        "boundary_match_score": ["pred", "gt", "dilation_ratio"],
        "average_precision": [
            "true_positive_flags",
            "confidence_scores",
            "num_ground_truth",
        ],
        "average_recall": ["true_positive_flags", "num_ground_truth"],
    },
    "camo_eval.metrics.perceptual": {
        "ssim": ["img_a", "img_b", "sigma"],
        "ms_ssim": ["img_a", "img_b", "levels"],
        "ms_ssim_lite": ["img_a", "img_b", "levels"],
    },
    "camo_eval.metrics.video": {
        "jaccard_index": ["pred_frames", "gt_frames"],
        "boundary_f_score": ["pred_frames", "gt_frames", "dilation_ratio"],
        "boundary_f_score_lite": ["pred_frames", "gt_frames", "dilation_ratio"],
        "j_and_f": ["pred_frames", "gt_frames"],
        "j_and_f_lite": ["pred_frames", "gt_frames"],
        "temporal_stability": ["pred_frames", "gt_frames"],
    },
    "camo_eval.metrics.robustness": {
        "attack_success_rate": ["clean_outputs", "attacked_outputs", "criterion"],
        "ap_drop": ["clean_ap", "attacked_ap"],
        "transferability": ["asr_by_model"],
    },
    "camo_eval.runner": {"evaluate": ["pred_dir", "gt_dir", "metrics"]},
    "camo_eval.export": {"to_latex": ["results"], "to_markdown": ["results"]},
}

STANDARD_STUBS = {
    "camo_eval.metrics.generation": ["fid", "kid", "lpips", "dists"],
    "camo_eval.metrics.instance": ["boundary_iou"],
    "camo_eval.metrics.perceptual": ["ms_ssim"],
    "camo_eval.metrics.video": ["boundary_f_score", "j_and_f"],
}


def names(function) -> list[str]:
    return [
        name
        for name, parameter in inspect.signature(function).parameters.items()
        if name != "self"
        and parameter.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]


def main() -> int:
    errors = []
    for module_name, functions in EXPECTED.items():
        module = importlib.import_module(module_name)
        for function_name, expected in functions.items():
            function = getattr(module, function_name, None)
            if not callable(function):
                errors.append(f"{module_name}.{function_name}: missing")
            elif names(function) != expected:
                errors.append(
                    f"{module_name}.{function_name}: expected {expected}, got {names(function)}"
                )
    for module_name, function_names in STANDARD_STUBS.items():
        module = importlib.import_module(module_name)
        for function_name in function_names:
            function = getattr(module, function_name)
            signature = inspect.signature(function)
            arguments = []
            for parameter in signature.parameters.values():
                if parameter.default is not inspect.Parameter.empty:
                    continue
                arguments.append("dummy")
            try:
                function(*arguments)
            except NotImplementedError:
                pass
            except Exception as exc:
                errors.append(
                    f"{module_name}.{function_name}: expected NotImplementedError, got {exc!r}"
                )
            else:
                errors.append(
                    f"{module_name}.{function_name}: standard stub returned a value"
                )
    for error in errors:
        print(f"ERROR {error}")
    print(f"check_api: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
