"""Protocol metadata and report helpers for camouflage evaluation."""

from .schema import (
    EvaluationContext,
    EvaluationReport,
    build_protocol_manifest,
    load_protocol_manifest,
)

__all__ = [
    "EvaluationContext",
    "EvaluationReport",
    "build_protocol_manifest",
    "load_protocol_manifest",
]
