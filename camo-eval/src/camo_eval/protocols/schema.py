"""Schemas for observer/channel/task/protocol-aware evaluation records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ALLOWED_OBSERVERS = {"human", "model", "operator", "hybrid"}
ALLOWED_CHANNELS = {
    "rgb",
    "video",
    "thermal",
    "multispectral",
    "multimodal",
    "radar",
    "custom",
}
ALLOWED_TASKS = {
    "image-cod",
    "video-cod",
    "instance-cod",
    "physical-adversarial",
    "generation",
    "human-search",
    "signature-analysis",
    "custom",
}


@dataclass(frozen=True)
class EvaluationContext:
    """Protocol metadata for a single evaluation setting."""

    observer: str
    channel: str
    task: str
    protocol: str
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.observer not in ALLOWED_OBSERVERS:
            raise ValueError(f"observer must be one of {sorted(ALLOWED_OBSERVERS)}")
        if self.channel not in ALLOWED_CHANNELS:
            raise ValueError(f"channel must be one of {sorted(ALLOWED_CHANNELS)}")
        if self.task not in ALLOWED_TASKS:
            raise ValueError(f"task must be one of {sorted(ALLOWED_TASKS)}")
        if not self.protocol:
            raise ValueError("protocol must be a non-empty string.")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "observer": self.observer,
            "channel": self.channel,
            "task": self.task,
            "protocol": self.protocol,
            "notes": self.notes,
        }


def _flatten_metrics(
    metrics: dict[str, object], prefix: str = ""
) -> list[tuple[str, object]]:
    """Flatten nested metric dicts into dotted ``(path, scalar)`` rows.

    Several metrics (e.g. ``e_measure``/``precision``) return dicts, so a metric
    group can nest two levels deep; flattening fully keeps the Markdown table
    from rendering raw ``dict`` reprs as cell values.
    """

    rows: list[tuple[str, object]] = []
    for key, value in metrics.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            rows.extend(_flatten_metrics(value, path))
        else:
            rows.append((path, value))
    return rows


@dataclass(frozen=True)
class EvaluationReport:
    """Bundle metric values with the protocol context that makes them comparable."""

    context: EvaluationContext
    metrics: dict[str, float | dict[str, float]]
    artifacts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "context": self.context.to_dict(),
            "metrics": self.metrics,
            "artifacts": self.artifacts,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        lines = [
            f"- observer: `{self.context.observer}`",
            f"- channel: `{self.context.channel}`",
            f"- task: `{self.context.task}`",
            f"- protocol: `{self.context.protocol}`",
        ]
        if self.context.notes:
            lines.append(f"- notes: {self.context.notes}")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | --- |")
        for name, value in _flatten_metrics(self.metrics):
            lines.append(f"| {name} | {value} |")
        return "\n".join(lines)


def build_protocol_manifest(
    context: EvaluationContext,
    pred_dir: str,
    gt_dir: str,
    metrics: list[str],
    *,
    name: str | None = None,
    pred_source: str | None = None,
    gt_source: str | None = None,
) -> dict[str, object]:
    """Build an executable evaluation manifest from protocol metadata."""

    if not pred_dir:
        raise ValueError("pred_dir must be a non-empty string.")
    if not gt_dir:
        raise ValueError("gt_dir must be a non-empty string.")
    if not metrics or not all(isinstance(metric, str) and metric for metric in metrics):
        raise ValueError("metrics must be a non-empty list of metric names.")

    manifest: dict[str, object] = {
        **context.to_dict(),
        "pred_dir": pred_dir,
        "gt_dir": gt_dir,
        "metrics": metrics,
    }
    if name:
        manifest["name"] = name
    if pred_source:
        manifest["pred_source"] = pred_source
    if gt_source:
        manifest["gt_source"] = gt_source
    return manifest


def load_protocol_manifest(manifest_path: str | Path) -> dict[str, object]:
    """Load a protocol manifest from JSON."""

    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "observer",
        "channel",
        "task",
        "protocol",
        "pred_dir",
        "gt_dir",
        "metrics",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"Manifest missing required keys: {missing}")
    if not isinstance(payload["metrics"], list) or not payload["metrics"]:
        raise ValueError("Manifest field 'metrics' must be a non-empty list.")
    if not all(isinstance(metric, str) and metric for metric in payload["metrics"]):
        raise ValueError(
            "Manifest field 'metrics' must contain only non-empty strings."
        )
    for key in ("pred_dir", "gt_dir", "protocol", "observer", "channel", "task"):
        if not isinstance(payload[key], str) or not payload[key]:
            raise ValueError(f"Manifest field {key!r} must be a non-empty string.")
    return payload
