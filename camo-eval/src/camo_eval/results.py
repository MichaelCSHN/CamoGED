"""Shared result container."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultsTable:
    """A small immutable tabular container used by the public API."""

    rows: list[dict[str, object]]
    columns: list[str]
