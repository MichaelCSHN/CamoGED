"""camo-eval: protocol-aware evaluation tools for camouflage research."""

from .export import to_latex, to_markdown
from .metrics.background import target_background_similarity
from .metrics.clutter import (
    camouflage_difficulty,
    edge_density,
    feature_congestion,
    subband_entropy,
)
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
from .metrics.generation import (
    deception_rate,
    dists,
    dists_lite,
    fid,
    fid_lite,
    kid,
    kid_lite,
    lpips,
    lpips_lite,
)
from .metrics.instance import (
    average_precision,
    average_recall,
    boundary_iou,
    boundary_match_score,
    dice,
    iou,
)
from .metrics.perceptual import ms_ssim, ms_ssim_lite, ssim
from .metrics.robustness import ap_drop, attack_success_rate, transferability
from .metrics.signature import (
    signal_to_clutter_ratio,
    spectral_angle_mapper,
    thermal_contrast,
)
from .metrics.video import (
    boundary_f_score,
    boundary_f_score_lite,
    j_and_f,
    j_and_f_lite,
    jaccard_index,
    temporal_stability,
)
from .protocols import EvaluationContext, EvaluationReport
from .results import ResultsTable
from .runner import evaluate

__version__ = "0.2.0.dev0"

__all__ = [name for name in globals() if not name.startswith("_")]
