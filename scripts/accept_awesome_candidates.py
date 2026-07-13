#!/usr/bin/env python3
"""Accept selected discovery candidates into the metadata-only catalog.

This tool is intended for the manually triggered ``awesome-curation`` workflow.
It never promotes a candidate to ``verified`` or to the curated Awesome layer.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "data/papers.yaml"
BEGIN = "<!-- CAMOGED_CANDIDATES_JSON_BEGIN -->"
END = "<!-- CAMOGED_CANDIDATES_JSON_END -->"
ALLOWED_LEGACY_TASKS = {
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


def parse_candidates(markdown: str) -> list[dict]:
    if BEGIN not in markdown or END not in markdown:
        raise ValueError("issue does not contain a CamoGED candidate JSON block")
    block = markdown.split(BEGIN, 1)[1].split(END, 1)[0]
    match = re.search(r"```json\s*(.*?)\s*```", block, re.S)
    if not match:
        raise ValueError("candidate JSON code block not found")
    payload = json.loads(match.group(1))
    if not isinstance(payload, list):
        raise ValueError("candidate block must contain a JSON list")
    return payload


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized[:72] or "resource"


def infer_legacy_task(tags: list[str]) -> str:
    for candidate in tags:
        if candidate in ALLOWED_LEGACY_TASKS:
            return candidate
    if "bbox-rcod" in tags:
        return "application"
    if "tracking" in tags:
        return "application"
    if "zero-shot-cod" in tags or "vision-language" in tags:
        return "foundation-model"
    if "camouflage-assessment" in tags or "robustness" in tags:
        return "application"
    return "application"


def infer_axes(
    tags: list[str],
) -> tuple[str, str, str, list[str], list[str], list[str], list[str]]:
    pillar = (
        "generation"
        if any(tag in {"generation", "physical-adversarial"} for tag in tags)
        else "detection"
    )
    if any(tag in {"camouflage-assessment", "dataset", "robustness"} for tag in tags):
        pillar = "evaluation"
    domain = (
        "physical"
        if any(
            tag
            in {
                "physical-adversarial",
                "biological-camouflage",
                "military-camouflage",
                "art-design",
            }
            for tag in tags
        )
        else "intelligent"
    )
    if "biological-camouflage" in tags:
        perspective = "nature"
    elif "military-camouflage" in tags:
        perspective = "war"
    elif "art-design" in tags:
        perspective = "art"
    else:
        perspective = "ai"

    modalities = (
        ["video"] if any(tag in {"video-cod", "tracking"} for tag in tags) else ["rgb"]
    )
    if any(
        tag in {"vision-language", "open-vocabulary", "zero-shot-cod"} for tag in tags
    ):
        modalities.append("vision-language")
    if "multimodal" in tags:
        modalities.append("multimodal")

    supervision = ["not-applicable"]
    mapping = {
        "weakly-supervised-cod": "weakly-supervised",
        "semi-supervised-cod": "semi-supervised",
        "unsupervised-cod": "unsupervised",
        "zero-shot-cod": "zero-shot",
    }
    selected = [value for key, value in mapping.items() if key in tags]
    if selected:
        supervision = selected
    elif pillar == "detection":
        supervision = ["fully-supervised"]
    elif pillar == "generation":
        supervision = ["optimization-based"]

    families = ["deep-learning"]
    if "vision-language" in tags:
        families.append("vision-language")
    if "open-vocabulary" in tags:
        families.append("open-vocabulary")
    if "physical-adversarial" in tags:
        families.append("physical-adversarial")
    if "camouflage-assessment" in tags:
        families.append("assessment")

    contexts = ["computer-vision"]
    if perspective == "nature":
        contexts = ["biological", "wildlife"]
    elif perspective == "war":
        contexts = ["military"]
    elif perspective == "art":
        contexts = ["art-design", "cultural-history"]
    return pillar, domain, perspective, modalities, supervision, families, contexts


def candidate_to_record(candidate: dict, reviewer: str, review_date: str) -> dict:
    tags = sorted(set(str(tag) for tag in candidate.get("suggested_tags") or []))
    pillar, domain, perspective, modalities, supervision, families, contexts = (
        infer_axes(tags)
    )
    title = str(candidate["title"]).strip()
    authors = candidate.get("authors") or "Unknown authors"
    abstract = re.sub(r"\s+", " ", str(candidate.get("abstract") or "")).strip()
    description = (
        abstract[:320].rstrip()
        or "Candidate accepted after metadata screening; substantive review remains pending."
    )
    paper = str(candidate.get("paper") or "").strip()
    if not paper.startswith(("http://", "https://")):
        raise ValueError(
            f"candidate {candidate.get('candidate_id')} has no valid source URL"
        )
    return {
        "id": slug(f"{candidate.get('year') or 'undated'}-{title}"),
        "title": title,
        "authors": authors,
        "venue": candidate.get("venue") or "Candidate source",
        "year": candidate.get("year"),
        "pillar": pillar,
        "domain": domain,
        "perspective": perspective,
        "task": infer_legacy_task(tags),
        "paper": paper,
        "code": None,
        "datasets": [],
        "bibtex_key": None,
        "notes": description,
        "publication_status": candidate.get("publication_status") or "preprint",
        "source_type": "primary",
        "verification_status": "metadata-only",
        "last_verified": review_date,
        "verified_by": reviewer,
        "license": None,
        "resource_type": "paper",
        "pillars": [pillar],
        "tasks": tags or [infer_legacy_task(tags)],
        "modalities": sorted(set(modalities)),
        "supervision": supervision,
        "method_families": sorted(set(families)),
        "contexts": contexts,
        "description": description,
        "curated": False,
        "curation_tier": "catalog",
        "date_added": review_date,
        "discovery_status": "accepted",
        "canonical_url": paper,
        "discovery_provenance": {
            "candidate_id": candidate.get("candidate_id"),
            "source": candidate.get("source"),
            "external_id": candidate.get("external_id"),
            "discovered_by": candidate.get("discovered_by") or [],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-markdown", required=True)
    parser.add_argument(
        "--accepted-ids", required=True, help="comma-separated candidate ids"
    )
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--review-date", default=date.today().isoformat())
    args = parser.parse_args()

    requested = {
        value.strip() for value in args.accepted_ids.split(",") if value.strip()
    }
    if not requested:
        raise ValueError("accepted-ids is empty")
    candidates = parse_candidates(Path(args.issue_markdown).read_text(encoding="utf-8"))
    by_id = {str(item.get("candidate_id")): item for item in candidates}
    missing = sorted(requested - set(by_id))
    if missing:
        raise ValueError(f"accepted candidate ids not found in issue: {missing}")

    document = yaml.safe_load(PAPERS.read_text(encoding="utf-8")) or {"papers": []}
    records = document.setdefault("papers", [])
    existing_ids = {item.get("id") for item in records}
    existing_titles = {
        re.sub(r"[^a-z0-9]+", "", str(item.get("title", "")).lower())
        for item in records
    }
    added = 0
    for candidate_id in sorted(requested):
        record = candidate_to_record(
            by_id[candidate_id], args.reviewer, args.review_date
        )
        normalized = re.sub(r"[^a-z0-9]+", "", record["title"].lower())
        if normalized in existing_titles:
            print(f"skip duplicate title: {record['title']}")
            continue
        base_id = record["id"]
        suffix = 2
        while record["id"] in existing_ids:
            record["id"] = f"{base_id}-{suffix}"
            suffix += 1
        records.append(record)
        existing_ids.add(record["id"])
        existing_titles.add(normalized)
        added += 1

    PAPERS.write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    subprocess.run(["python", "scripts/build_awesome.py"], cwd=ROOT, check=True)
    subprocess.run(["python", "scripts/check_data.py"], cwd=ROOT, check=True)
    subprocess.run(["python", "scripts/check_awesome.py"], cwd=ROOT, check=True)
    print(f"accept_awesome_candidates: added {added} metadata-only record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
