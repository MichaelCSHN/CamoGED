"""camo-eval: unified evaluation toolkit for camouflage research."""

from .export import to_latex, to_markdown
from .metrics.background import target_background_similarity
from .metrics.detection import (
    e_measure,
    f_measure,
    mae,
    precision,
    precision_recall_curve,
    recall,
    s_measure,
    weighted_f_measure,
)
from .metrics.generation import deception_rate, fid, lpips
from .metrics.instance import average_precision, average_recall, boundary_iou, dice, iou
from .metrics.perceptual import ms_ssim, ssim
from .metrics.robustness import ap_drop, attack_success_rate, transferability
from .metrics.signature import (
    signal_to_clutter_ratio,
    spectral_angle_mapper,
    thermal_contrast,
)
from .metrics.video import boundary_f_score, j_and_f, jaccard_index, temporal_stability
from .protocols import EvaluationContext, EvaluationReport
from .results import ResultsTable
from .runner import evaluate

__version__ = "0.1.0"
__all__ = [
    "EvaluationContext",
    "EvaluationReport",
    "ResultsTable",
    "__version__",
    "ap_drop",
    "attack_success_rate",
    "average_precision",
    "average_recall",
    "boundary_f_score",
    "boundary_iou",
    "deception_rate",
    "dice",
    "e_measure",
    "evaluate",
    "f_measure",
    "fid",
    "iou",
    "j_and_f",
    "jaccard_index",
    "lpips",
    "mae",
    "ms_ssim",
    "precision",
    "precision_recall_curve",
    "recall",
    "s_measure",
    "signal_to_clutter_ratio",
    "spectral_angle_mapper",
    "ssim",
    "target_background_similarity",
    "temporal_stability",
    "thermal_contrast",
    "to_latex",
    "to_markdown",
    "transferability",
    "weighted_f_measure",
]
