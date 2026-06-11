"""Reference-value tests for the extension metrics (P1 numerical correctness).

Each metric with an authoritative reference is pinned here:
- SSIM / MS-SSIM  -> ``skimage.metrics`` (gaussian-weighted convention)
- IoU / Dice      -> exact set-operation definitions on binary masks
- boundary_iou    -> hand-computed expectation (note: this is a boundary-pixel
  band-matching score, NOT the region-band Boundary IoU of Cheng et al. 2021;
  see camo-eval/ROADMAP.md).
"""

import numpy as np
import pytest

from camo_eval import boundary_iou, dice, iou, ms_ssim, ssim

skimage_metrics = pytest.importorskip("skimage.metrics")


def _sk_ssim(a, b):
    return skimage_metrics.structural_similarity(
        a,
        b,
        data_range=1.0,
        gaussian_weights=True,
        sigma=1.5,
        use_sample_covariance=False,
    )


SSIM_FIXTURES = [
    (lambda r: r.random((64, 64)), 0.1),
    (lambda r: r.random((48, 80)), 0.25),
    (lambda r: r.random((33, 51)), 0.05),
]


@pytest.mark.parametrize(("make", "noise"), SSIM_FIXTURES)
def test_ssim_matches_skimage(make, noise):
    """Reference source: scikit-image structural_similarity (gaussian weights)."""
    rng = np.random.default_rng(42)
    a = make(rng)
    b = np.clip(a + rng.normal(0, noise, a.shape), 0.0, 1.0)
    assert ssim(a, b) == pytest.approx(_sk_ssim(a, b), abs=1e-4)


def test_ssim_identity_and_bounds():
    rng = np.random.default_rng(0)
    a = rng.random((40, 40))
    assert ssim(a, a) == pytest.approx(1.0, abs=1e-6)
    assert ssim(a, a) == pytest.approx(_sk_ssim(a, a), abs=1e-4)


def test_ms_ssim_identity_and_monotonic():
    rng = np.random.default_rng(1)
    a = rng.random((64, 64))
    b = np.clip(a + rng.normal(0, 0.1, a.shape), 0.0, 1.0)
    c = np.clip(a + rng.normal(0, 0.4, a.shape), 0.0, 1.0)
    assert ms_ssim(a, a) == pytest.approx(1.0, abs=1e-6)
    # More noise -> lower MS-SSIM.
    assert ms_ssim(a, b) > ms_ssim(a, c)


def test_iou_dice_exact_on_binary_masks():
    pred = np.array(
        [[255, 255, 0, 0], [255, 255, 0, 0], [0, 0, 0, 0], [0, 0, 0, 255]],
        dtype=np.uint8,
    )
    gt = np.array(
        [[255, 0, 0, 0], [255, 255, 0, 0], [0, 255, 0, 0], [0, 0, 0, 0]],
        dtype=np.uint8,
    )
    p = pred > 0
    g = gt > 0
    inter = int(np.count_nonzero(p & g))
    union = int(np.count_nonzero(p | g))
    denom = int(np.count_nonzero(p) + np.count_nonzero(g))

    assert iou(pred, gt) == pytest.approx(inter / union, abs=1e-12)
    assert dice(pred, gt) == pytest.approx(2 * inter / denom, abs=1e-12)


def test_iou_dice_disjoint_and_empty():
    a = np.array([[255, 0], [0, 0]], dtype=np.uint8)
    b = np.array([[0, 0], [0, 255]], dtype=np.uint8)
    assert iou(a, b) == pytest.approx(0.0)
    assert dice(a, b) == pytest.approx(0.0)
    empty = np.zeros((2, 2), dtype=np.uint8)
    # Both empty -> perfect agreement by convention.
    assert iou(empty, empty) == pytest.approx(1.0)
    assert dice(empty, empty) == pytest.approx(1.0)


def test_boundary_iou_known_case():
    """A square vs an identical mask scores 1.0; a boundary far outside the
    dilation tolerance scores 0.0. Documents the band-matching behavior (this is
    NOT Cheng et al. 2021 region-band Boundary IoU; see ROADMAP)."""
    square = np.zeros((16, 16), dtype=np.uint8)
    square[1:7, 1:7] = 255
    assert boundary_iou(square, square) == pytest.approx(1.0)

    # A single far-corner pixel: its boundary is well outside the 1px tolerance
    # band of the square's boundary, so there is no match.
    other = np.zeros((16, 16), dtype=np.uint8)
    other[15, 15] = 255
    assert boundary_iou(square, other) == pytest.approx(0.0)
