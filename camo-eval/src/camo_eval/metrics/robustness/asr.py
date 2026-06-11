"""Robustness helpers with the frozen Sprint 1 API."""

from __future__ import annotations


def attack_success_rate(clean_outputs, attacked_outputs, criterion) -> float:
    """Compute the fraction of samples for which ``criterion`` reports success."""

    clean_list = list(clean_outputs)
    attacked_list = list(attacked_outputs)
    if len(clean_list) != len(attacked_list):
        raise ValueError(
            "clean_outputs and attacked_outputs must have the same length."
        )
    if not clean_list:
        raise ValueError("At least one sample is required to compute ASR.")
    successes = [
        bool(criterion(clean, attacked))
        for clean, attacked in zip(clean_list, attacked_list)
    ]
    return float(sum(successes) / len(successes))


def ap_drop(clean_ap: float, attacked_ap: float) -> float:
    """Return the absolute AP drop introduced by the attack."""

    return float(clean_ap - attacked_ap)


def transferability(asr_by_model: dict) -> dict:
    """Aggregate transferability statistics from per-model ASR values."""

    if not isinstance(asr_by_model, dict) or not asr_by_model:
        raise ValueError("asr_by_model must be a non-empty dict of model -> ASR.")
    values = [float(value) for value in asr_by_model.values()]
    return {
        "per_model": {str(key): float(value) for key, value in asr_by_model.items()},
        "mean": float(sum(values) / len(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }
