#!/usr/bin/env python3
"""Validate the Awesome/catalog specialist acceptance criteria."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)
DOI = re.compile(r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/\S+)", re.I)

REQUIRED_AXES = {
    "resource_type",
    "pillars",
    "tasks",
    "modalities",
    "supervision",
    "method_families",
    "contexts",
    "description",
    "curated",
    "curation_tier",
    "date_added",
    "discovery_status",
    "canonical_url",
}
REQUIRED_TASK_COVERAGE = {
    "image-cod",
    "video-cod",
    "instance-cod",
    "bbox-rcod",
    "tracking",
    "weakly-supervised-cod",
    "semi-supervised-cod",
    "unsupervised-cod",
    "zero-shot-cod",
    "open-vocabulary",
    "vision-language",
    "generation",
    "camouflage-assessment",
}
REQUIRED_CONTEXT_COVERAGE = {"computer-vision", "biological", "military", "art-design"}
REQUIRED_MODALITY_COVERAGE = {
    "rgb",
    "video",
    "depth",
    "multispectral",
    "multimodal",
    "vision-language",
}


def load(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


def values(entry: dict, field: str) -> list[str]:
    value = entry.get(field)
    if isinstance(value, list):
        return [str(item) for item in value]
    return [] if value is None else [str(value)]


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def identifier(url: str | None) -> tuple[str, str] | None:
    if not url:
        return None
    arxiv = ARXIV.search(url)
    if arxiv:
        return ("arxiv", arxiv.group(1))
    doi = DOI.search(url)
    if doi:
        return ("doi", doi.group(1).rstrip(".,)").lower())
    return None


def matches(entry: dict, rule: dict) -> bool:
    return any(
        set(values(entry, field)) & set(expected) for field, expected in rule.items()
    )


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    resources = load("papers.yaml").get("papers", [])
    datasets = load("datasets.yaml").get("datasets", [])
    config = load("awesome.yaml")
    discovery = load("discovery_queries.yaml")

    if len(resources) < 60:
        errors.append(
            f"catalog requires at least 60 accepted resources; found {len(resources)}"
        )
    curated = [item for item in resources if item.get("curated") is True]
    if len(curated) < 25:
        errors.append(
            f"curated Awesome requires at least 25 resources; found {len(curated)}"
        )
    if len(datasets) < 20:
        errors.append(
            f"dataset index requires at least 20 records; found {len(datasets)}"
        )

    seen_titles: dict[str, str] = {}
    seen_ids: dict[tuple[str, str], str] = {}
    all_tasks: Counter[str] = Counter()
    all_contexts: Counter[str] = Counter()
    all_modalities: Counter[str] = Counter()

    for index, item in enumerate(resources):
        where = f"papers[{index}]/{item.get('id')}"
        missing = sorted(REQUIRED_AXES - set(item))
        if missing:
            errors.append(f"{where}: missing Awesome fields {missing}")
            continue
        for field in (
            "pillars",
            "tasks",
            "modalities",
            "supervision",
            "method_families",
            "contexts",
        ):
            if not isinstance(item.get(field), list) or not item[field]:
                errors.append(f"{where}: {field} must be a non-empty list")
        if (
            not isinstance(item.get("description"), str)
            or len(item["description"].strip()) < 25
        ):
            errors.append(f"{where}: description is missing or too short")
        if item.get("curation_tier") not in {"core", "recommended", "catalog"}:
            errors.append(f"{where}: invalid curation_tier")
        if item.get("discovery_status") not in {"accepted", "deferred", "rejected"}:
            errors.append(f"{where}: invalid discovery_status")
        for field in ("date_added", "last_verified"):
            value = item.get(field)
            if value is not None and (
                not isinstance(value, str) or not DATE.match(value)
            ):
                errors.append(f"{where}: {field} must be YYYY-MM-DD or null")
        canonical = item.get("canonical_url")
        if not isinstance(canonical, str) or urlparse(canonical).scheme not in {
            "http",
            "https",
        }:
            errors.append(f"{where}: canonical_url must be http(s)")

        normalized = normalize_title(str(item.get("title", "")))
        if normalized in seen_titles:
            errors.append(
                f"{where}: duplicate normalized title with {seen_titles[normalized]}"
            )
        seen_titles[normalized] = str(item.get("id"))
        external_id = identifier(canonical)
        if external_id and external_id in seen_ids:
            errors.append(
                f"{where}: duplicate {external_id[0]} identifier with {seen_ids[external_id]}"
            )
        elif external_id:
            seen_ids[external_id] = str(item.get("id"))

        all_tasks.update(values(item, "tasks"))
        all_contexts.update(values(item, "contexts"))
        all_modalities.update(values(item, "modalities"))

    missing_tasks = sorted(REQUIRED_TASK_COVERAGE - set(all_tasks))
    missing_contexts = sorted(REQUIRED_CONTEXT_COVERAGE - set(all_contexts))
    missing_modalities = sorted(REQUIRED_MODALITY_COVERAGE - set(all_modalities))
    if missing_tasks:
        errors.append(f"missing task coverage: {missing_tasks}")
    if missing_contexts:
        errors.append(f"missing context coverage: {missing_contexts}")
    if missing_modalities:
        errors.append(f"missing modality coverage: {missing_modalities}")

    recent = [item for item in resources if int(item.get("year") or 0) >= 2025]
    current = [item for item in resources if int(item.get("year") or 0) >= 2026]
    if len(recent) < 15:
        errors.append(
            f"freshness gate requires at least 15 records from 2025+; found {len(recent)}"
        )
    if len(current) < 3:
        errors.append(
            f"freshness gate requires at least 3 records from 2026+; found {len(current)}"
        )

    by_id = {item.get("id"): item for item in resources}
    for item_id in config.get("core_reading", []):
        if item_id not in by_id:
            errors.append(
                f"awesome.yaml core_reading references unknown id {item_id!r}"
            )
        elif by_id[item_id].get("curated") is not True:
            errors.append(f"core resource {item_id!r} is not curated")
    for section in config.get("sections", []):
        section_entries = [
            item for item in curated if matches(item, section.get("match", {}))
        ]
        if not section_entries:
            errors.append(f"curated section {section.get('id')!r} has no entries")
    if len(config.get("sections", [])) < 10:
        errors.append("awesome.yaml requires at least 10 curated sections")

    queries = discovery.get("queries", [])
    query_ids = [item.get("id") for item in queries]
    if len(queries) < 10:
        errors.append(
            f"dynamic discovery requires at least 10 queries; found {len(queries)}"
        )
    if len(query_ids) != len(set(query_ids)):
        errors.append("discovery query ids must be unique")
    sources = {item.get("source") for item in queries}
    if not {"arxiv", "crossref"}.issubset(sources):
        errors.append("discovery queries must cover arxiv and crossref")

    required_files = [
        "awesome/README.md",
        "web/catalog.md",
        "web/updates.md",
        "scripts/discover_awesome.py",
        "scripts/accept_awesome_candidates.py",
        "docs/AWESOME_GOVERNANCE.md",
        ".github/workflows/awesome-discovery.yml",
        ".github/workflows/awesome-curation.yml",
    ]
    for relative in required_files:
        if not (ROOT / relative).exists():
            errors.append(f"missing Awesome maintenance surface: {relative}")

    if config.get("last_human_review") != config.get("coverage_through"):
        warnings.append(
            "last_human_review differs from coverage_through; verify that this is intentional"
        )

    for warning in warnings:
        print(f"WARN {warning}")
    for error in errors:
        print(f"ERROR {error}")
    print(
        "check_awesome: "
        f"{len(errors)} error(s), {len(warnings)} warning(s); "
        f"resources={len(resources)}, curated={len(curated)}, datasets={len(datasets)}, "
        f"recent={len(recent)}, current={len(current)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
