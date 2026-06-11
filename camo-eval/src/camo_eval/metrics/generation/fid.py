"""Optional generation metrics."""

from __future__ import annotations


def _missing_extra(metric: str) -> ImportError:
    return ImportError(
        f"{metric} requires the optional generation extra. "
        "Install with `pip install camo-eval[generation]`."
    )


def fid(real_dir: str, fake_dir: str) -> float:
    raise _missing_extra("fid")


def lpips(img_a, img_b) -> float:
    raise _missing_extra("lpips")


def deception_rate(detector, images, targets) -> float:
    raise _missing_extra("deception_rate")
