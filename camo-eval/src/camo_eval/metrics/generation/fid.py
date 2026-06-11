"""Optional generation metrics."""

from __future__ import annotations


def _not_implemented(metric: str) -> NotImplementedError:
    return NotImplementedError(
        f"{metric} is not implemented yet. The generation cluster "
        "(FID/KID/LPIPS/DISTS) is tracked in camo-eval/ROADMAP.md (P2)."
    )


def fid(real_dir: str, fake_dir: str) -> float:
    raise _not_implemented("fid")


def lpips(img_a, img_b) -> float:
    raise _not_implemented("lpips")


def deception_rate(detector, images, targets) -> float:
    raise _not_implemented("deception_rate")
