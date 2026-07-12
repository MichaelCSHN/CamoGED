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
    """Protocol and provenance metadata for a single evaluation setting."""

    observer: str
    channel: str
    task: str
    protocol: str
    notes: str | None = None
    implementation_version: str = "0.2.0.dev0"
    dataset_version: str | None = None
    prediction_revision: str | None = None
    threshold_policy: str | None = None
    seed: int | None = None
    environment: str | None = None
    uncertainty: str | None = None

    def __post_init__(self) -> None:
        if self.observer not in ALLOWED_OBSERVERS:
            raise ValueError(f"observer must be one of {sorted(ALLOWED_OBSERVERS)}")
        if self.channel not in ALLOWED_CHANNELS:
            raise ValueError(f"channel must be one of {sorted(ALLOWED_CHANNELS)}")
        if self.task not in ALLOWED_TASKS:
            raise ValueError(f"task must be one of {sorted(ALLOWED_TASKS)}")
        if not isinstance(self.protocol, str) or not self.protocol.strip():
            raise ValueError("protocol must be a non-empty string.")
        if not isinstance(self.implementation_version, str) or not self.implementation_version:
            raise ValueError("implementation_version must be a non-empty string.")
        if self.seed is not None and not isinstance(self.seed, int):
            raise ValueError("seed must be an integer or null.")

    def to_dict(self) -> dict[str, object]:
        return {
            "observer": self.observer,
            "channel": self.channel,
            "task": self.task,
            "protocol": self.protocol,
            "notes": self.notes,
            "implementation_version": self.implementation_version,
            "dataset_version": self.dataset_version,
            "prediction_revision": self.prediction_revision,
            "threshold_policy": self.threshold_policy,
            "seed": self.seed,
            "environment": self.environment,
            "uncertainty": self.uncertainty,
        }

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> "EvaluationContext":
        return cls(
            observer=str(payload["observer"]),
            channel=str(payload["channel"]),
            task=str(payload["task"]),
            protocol=str(payload["protocol"]),
            notes=_optional_str(payload.get("notes")),
            implementation_version=str(payload.get("implementation_version") or "0.2.0.dev0"),
            dataset_version=_optional_str(payload.get("dataset_version")),
            prediction_revision=_optional_str(payload.get("prediction_revision")),
            threshold_policy=_optional_str(payload.get("threshold_policy")),
            seed=_optional_int(payload.get("seed")),
            environment=_optional_str(payload.get("environment")),
            uncertainty=_optional_str(payload.get("uncertainty")),
        )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"expected string or null, got {type(value).__name__}")
    return value


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"expected integer or null, got {type(value).__name__}")
    return value


def _flatten_metrics(metrics: dict[str, object], prefix: str = "") -> list[tuple[str, object]]:
    """Flatten nested metric mappings into dotted scalar rows."""

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
    """Bundle metric values with the context that makes them comparable."""

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
        lines: list[str] = []
        for key, value in self.context.to_dict().items():
            if value is not None:
                lines.append(f"- {key}: `{value}`")
        if self.artifacts:
            lines.append("")
            lines.append("### Artifacts")
            for key, value in self.artifacts.items():
                lines.append(f"- {key}: `{value}`")
        lines.extend(["", "| Metric | Value |", "| --- | --- |"])
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
    """Load and validate a JSON protocol manifest."""

    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifest must contain a JSON object.")
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
    for key in ("pred_dir", "gt_dir"):
        if not isinstance(payload[key], str) or not payload[key]:
            raise ValueError(f"Manifest field {key!r} must be a non-empty string.")
    if not isinstance(payload["metrics"], list) or not payload["metrics"]:
        raise ValueError("Manifest field 'metrics' must be a non-empty list.")
    if not all(isinstance(metric, str) and metric for metric in payload["metrics"]):
        raise ValueError("Manifest field 'metrics' must contain only non-empty strings.")
    EvaluationContext.from_mapping(payload)
    return payload
