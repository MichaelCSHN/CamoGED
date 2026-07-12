#!/usr/bin/env python3
"""Validate CamoGED metadata schema 2.0 and generated-page determinism."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BIB = ROOT / "book/references.bib"
AWESOME = ROOT / "awesome/README.md"

PILLAR = {"generation", "detection", "evaluation"}
DOMAIN = {"physical", "digital", "intelligent"}
PERSPECTIVE = {"nature", "war", "art", "ai"}
MODALITY = {
    "rgb",
    "video",
    "multispectral",
    "multimodal",
    "thermal",
    "polarization",
    "depth",
}
TASK = {
    "image-cod",
    "video-cod",
    "instance-cod",
    "referring-cod",
    "collaborative-cod",
    "open-vocab-cos",
    "survey",
    "generation",
    "physical-adversarial",
    "digital-adversarial",
    "foundation-model",
    "dataset",
    "application",
}
PUBLICATION_STATUS = {
    "published",
    "preprint",
    "unpublished",
    "project-page",
    "released",
}
VERIFICATION_STATUS = {"verified", "metadata-only", "unverified"}
SOURCE_TYPE = {"primary", "official-project", "secondary"}
LICENSE_STATUS = {"verified", "unknown", "restricted"}
RESULT_STATUS = {"reported", "reproduced"}
METRIC_KEYS = {"Sm", "Fw", "Em", "MAE", "maxF", "meanF", "AP", "AR", "JF", "temporal"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL = re.compile(r"^https?://", re.IGNORECASE)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors: list[str] = []
warnings: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def require(entry: dict, fields: set[str], where: str) -> None:
    for field in sorted(fields):
        if field not in entry:
            err(f"{where}: missing field {field!r}")


def check_date(value, where: str, field: str) -> None:
    if value is not None and (not isinstance(value, str) or not DATE.match(value)):
        err(f"{where}: {field} must be ISO YYYY-MM-DD or null")


def check_url(value, where: str, field: str, nullable: bool = True) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not URL.match(value):
        err(
            f"{where}: {field} must be an http(s) URL"
            + (" or null" if nullable else "")
        )


def bib_keys() -> set[str]:
    if not BIB.exists():
        return set()
    return set(re.findall(r"@\w+\{([^,]+),", BIB.read_text(encoding="utf-8")))


def main() -> int:
    papers = load("papers.yaml").get("papers", [])
    datasets = load("datasets.yaml").get("datasets", [])
    results = load("leaderboard.yaml").get("leaderboard", [])
    seen: set[str] = set()
    dataset_ids = {entry.get("id") for entry in datasets}
    dataset_names = {entry.get("name") for entry in datasets}
    data_bib: set[str] = set()

    paper_required = {
        "id",
        "title",
        "authors",
        "venue",
        "year",
        "pillar",
        "domain",
        "perspective",
        "task",
        "paper",
        "publication_status",
        "source_type",
        "verification_status",
        "last_verified",
        "verified_by",
    }
    for index, entry in enumerate(papers):
        where = f"papers[{index}]"
        require(entry, paper_required, where)
        item_id = entry.get("id")
        if not isinstance(item_id, str) or not KEBAB.match(item_id):
            err(f"{where}: invalid kebab-case id")
        if item_id in seen:
            err(f"{where}: duplicate id {item_id!r}")
        seen.add(item_id)
        for field, allowed in (
            ("pillar", PILLAR),
            ("domain", DOMAIN),
            ("perspective", PERSPECTIVE),
            ("task", TASK),
            ("publication_status", PUBLICATION_STATUS),
            ("source_type", SOURCE_TYPE),
            ("verification_status", VERIFICATION_STATUS),
        ):
            if entry.get(field) not in allowed:
                err(f"{where}: {field}={entry.get(field)!r} is invalid")
        check_url(entry.get("paper"), where, "paper", nullable=False)
        check_url(entry.get("code"), where, "code")
        check_date(entry.get("last_verified"), where, "last_verified")
        if entry.get("verification_status") == "verified" and not entry.get(
            "verified_by"
        ):
            err(f"{where}: verified entry requires verified_by")
        for dataset in entry.get("datasets") or []:
            if dataset not in dataset_ids and dataset not in dataset_names:
                err(f"{where}: unknown dataset reference {dataset!r}")
        if entry.get("bibtex_key"):
            data_bib.add(entry["bibtex_key"])

    dataset_required = {
        "id",
        "name",
        "task",
        "modality",
        "year",
        "link",
        "publication_status",
        "verification_status",
        "last_verified",
        "verified_by",
        "license_status",
    }
    for index, entry in enumerate(datasets):
        where = f"datasets[{index}]"
        require(entry, dataset_required, where)
        item_id = entry.get("id")
        if not isinstance(item_id, str) or not KEBAB.match(item_id):
            err(f"{where}: invalid kebab-case id")
        if item_id in seen:
            err(f"{where}: duplicate global id {item_id!r}")
        seen.add(item_id)
        if entry.get("task") not in TASK:
            err(f"{where}: invalid task")
        if entry.get("modality") not in MODALITY:
            err(f"{where}: invalid modality")
        if entry.get("publication_status") not in PUBLICATION_STATUS:
            err(f"{where}: invalid publication_status")
        if entry.get("verification_status") not in VERIFICATION_STATUS:
            err(f"{where}: invalid verification_status")
        if entry.get("license_status") not in LICENSE_STATUS:
            err(f"{where}: invalid license_status")
        if entry.get("license_status") == "verified" and not entry.get("license"):
            err(f"{where}: verified license_status requires a license value")
        check_url(entry.get("link"), where, "link")
        check_date(entry.get("last_verified"), where, "last_verified")
        if entry.get("bibtex_key"):
            data_bib.add(entry["bibtex_key"])

    result_required = {
        "id",
        "method",
        "dataset",
        "task",
        "metrics",
        "status",
        "source",
        "verified",
        "verification_status",
        "last_verified",
        "verified_by",
        "protocol",
        "metric_implementation",
    }
    for index, entry in enumerate(results):
        where = f"leaderboard[{index}]"
        require(entry, result_required, where)
        item_id = entry.get("id")
        if not isinstance(item_id, str) or not KEBAB.match(item_id):
            err(f"{where}: invalid id")
        if item_id in seen:
            err(f"{where}: duplicate global id {item_id!r}")
        seen.add(item_id)
        if (
            entry.get("dataset") not in dataset_ids
            and entry.get("dataset") not in dataset_names
        ):
            err(f"{where}: unknown dataset")
        if entry.get("task") not in TASK or entry.get("status") not in RESULT_STATUS:
            err(f"{where}: invalid task/status")
        if (
            entry.get("verified") is not True
            or entry.get("verification_status") != "verified"
        ):
            err(f"{where}: registry rows must be verified")
        if not entry.get("verified_by") or not entry.get("last_verified"):
            err(f"{where}: verified row requires reviewer and date")
        check_date(entry.get("last_verified"), where, "last_verified")
        source = entry.get("source")
        if not (
            isinstance(source, str) and (URL.match(source) or (ROOT / source).exists())
        ):
            err(f"{where}: source is not resolvable")
        metrics = entry.get("metrics")
        if not isinstance(metrics, dict):
            err(f"{where}: metrics must be a mapping")
            continue
        for key, value in metrics.items():
            if key not in METRIC_KEYS:
                err(f"{where}: unsupported standard metric key {key!r}")
            if value is not None and not isinstance(value, (int, float)):
                err(f"{where}: metric {key} must be numeric or null")
        if entry.get("status") == "reproduced":
            if URL.match(str(source)) or not str(source).endswith(
                (".json", ".yaml", ".yml")
            ):
                err(f"{where}: reproduced result requires a repository manifest path")

    keys = bib_keys()
    for key in sorted(data_bib - keys):
        warn(f"bibtex_key {key!r} exists in data but not references.bib")

    from build_awesome import render

    expected = render().rstrip() + "\n"
    if not AWESOME.exists() or AWESOME.read_text(encoding="utf-8") != expected:
        err("awesome/README.md is out of sync with scripts/build_awesome.py")

    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"check_data: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
