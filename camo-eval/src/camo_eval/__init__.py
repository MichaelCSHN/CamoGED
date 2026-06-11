"""camo-eval: unified evaluation toolkit for camouflage research."""

from .export import to_latex, to_markdown
from .metrics.detection import e_measure, f_measure, mae, s_measure, weighted_f_measure
from .metrics.generation import deception_rate, fid, lpips
from .metrics.robustness import ap_drop, attack_success_rate, transferability
from .results import ResultsTable
from .runner import evaluate

__version__ = "0.1.0"
__all__ = [
    "ResultsTable",
    "__version__",
    "ap_drop",
    "attack_success_rate",
    "deception_rate",
    "e_measure",
    "evaluate",
    "f_measure",
    "fid",
    "lpips",
    "mae",
    "s_measure",
    "to_latex",
    "to_markdown",
    "transferability",
    "weighted_f_measure",
]
