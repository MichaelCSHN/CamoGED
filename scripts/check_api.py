#!/usr/bin/env python3
"""Verify that camo-eval's public API matches the frozen contract.

The authoritative API is specified in AGENTS.md §6 and Chapter 15 / Appendix B.
This script mirrors that list and checks the actual function signatures via
`inspect`, so the contract cannot drift silently. Run:

    python scripts/check_api.py

Exit 0 if all REQUIRED functions exist with the expected parameter names; 1
otherwise. Functions in OPTIONAL modules (generation extras that need heavy deps
like torch) are downgraded to warnings if the module cannot be imported.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Allow importing the package whether or not it is pip-installed.
sys.path.insert(0, str(ROOT / "camo-eval" / "src"))

# ---- Authoritative contract (mirrors AGENTS.md §6) ----
# module -> {function: [expected positional/keyword parameter names in order]}
EXPECTED: dict[str, dict[str, list[str]]] = {
    "camo_eval.metrics.detection": {
        "mae": ["pred", "gt"],
        "weighted_f_measure": ["pred", "gt", "beta2"],
        "s_measure": ["pred", "gt", "alpha"],
        "e_measure": ["pred", "gt"],
        "f_measure": ["pred", "gt"],
    },
    "camo_eval.metrics.robustness": {
        "attack_success_rate": ["clean_outputs", "attacked_outputs", "criterion"],
        "ap_drop": ["clean_ap", "attacked_ap"],
        "transferability": ["asr_by_model"],
    },
    "camo_eval.runner": {
        "evaluate": ["pred_dir", "gt_dir", "metrics"],
    },
    "camo_eval.export": {
        "to_latex": ["results"],
        "to_markdown": ["results"],
    },
}

# Modules allowed to fail import due to optional heavy deps (torch, etc.).
OPTIONAL_MODULES = {
    "camo_eval.metrics.generation": {
        "fid": ["real_dir", "fake_dir"],
        "kid": ["real_dir", "fake_dir", "degree", "gamma", "coef0"],
        "lpips": ["img_a", "img_b"],
        "dists": ["img_a", "img_b"],
        "deception_rate": ["detector", "images", "targets"],
    },
}

# ---- Extension API (Claude-owned, beyond AGENTS.md §6) ----
# Stable public functions added by the lead. Frozen here so they cannot drift
# silently either; these are consumed by the CLI, demos, and the website.
EXTENSION: dict[str, dict[str, list[str]]] = {
    "camo_eval.metrics.detection": {
        "precision": ["pred", "gt"],
        "recall": ["pred", "gt"],
        "precision_recall_curve": ["pred", "gt"],
    },
    "camo_eval.metrics.instance": {
        "iou": ["pred", "gt"],
        "dice": ["pred", "gt"],
        "boundary_iou": ["pred", "gt", "dilation_ratio"],
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
    },
    "camo_eval.metrics.signature": {
        "thermal_contrast": ["target", "background"],
        "signal_to_clutter_ratio": ["target", "background"],
        "spectral_angle_mapper": ["signature_a", "signature_b"],
    },
    "camo_eval.metrics.background": {
        "target_background_similarity": [
            "image",
            "target_mask",
            "mode",
            "bins",
            "near_iterations",
        ],
    },
    "camo_eval.metrics.clutter": {
        "edge_density": ["image", "threshold"],
        "subband_entropy": ["image", "bins"],
        "feature_congestion": ["image"],
        "camouflage_difficulty": ["image", "target_mask"],
    },
    "camo_eval.metrics.video": {
        "jaccard_index": ["pred_frames", "gt_frames"],
        "boundary_f_score": ["pred_frames", "gt_frames", "dilation_ratio"],
        "j_and_f": ["pred_frames", "gt_frames"],
        "temporal_stability": ["pred_frames", "gt_frames"],
    },
}

errors: list[str] = []
warnings: list[str] = []


def param_names(func) -> list[str]:
    sig = inspect.signature(func)
    names = []
    for name, p in sig.parameters.items():
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if name == "self":
            continue
        names.append(name)
    return names


def check_module(modname: str, funcs: dict[str, list[str]], optional: bool) -> None:
    try:
        mod = importlib.import_module(modname)
    except ImportError as e:
        msg = f"{modname}: cannot import ({e})"
        if optional:
            warnings.append(msg + " [optional module — install extras to check]")
        else:
            errors.append(msg + " [required module not implemented?]")
        return
    for fname, expected in funcs.items():
        fn = getattr(mod, fname, None)
        if fn is None or not callable(fn):
            errors.append(f"{modname}.{fname}: missing or not callable")
            continue
        actual = param_names(fn)
        if actual != expected:
            errors.append(
                f"{modname}.{fname}: signature mismatch — "
                f"expected params {expected}, got {actual}"
            )


def main() -> int:
    for modname, funcs in EXPECTED.items():
        check_module(modname, funcs, optional=False)
    for modname, funcs in EXTENSION.items():
        check_module(modname, funcs, optional=False)
    for modname, funcs in OPTIONAL_MODULES.items():
        check_module(modname, funcs, optional=True)

    print("=" * 60)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print("=" * 60)
    print(f"check_api: {len(errors)} error(s), {len(warnings)} warning(s)")
    if not errors:
        print("OK — camo-eval public API matches the frozen contract")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
