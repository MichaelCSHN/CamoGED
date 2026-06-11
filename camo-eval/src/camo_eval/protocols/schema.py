"""Schemas for observer/channel/task/protocol-aware evaluation records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field


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
        for name, value in self.metrics.items():
            if isinstance(value, dict):
                for sub_name, sub_value in value.items():
                    lines.append(f"| {name}.{sub_name} | {sub_value} |")
            else:
                lines.append(f"| {name} | {value} |")
        return "\n".join(lines)
