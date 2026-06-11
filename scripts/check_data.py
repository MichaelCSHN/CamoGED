#!/usr/bin/env python3
"""Validate data/*.yaml against data/SCHEMA.md (schema_version 1.0).

This is the executable form of SCHEMA.md §6 and a CI gate. It is intentionally
strict: until the existing YAML is aligned to the schema (task B1) it will report
errors — that is the point. Run:

    python scripts/check_data.py

Exit code 0 if there are no ERRORS (WARNINGS are allowed), 1 otherwise.
Only dependency: PyYAML (`pip install pyyaml`).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML is required. Install with: pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BIB = ROOT / "book" / "references.bib"

# ---- Controlled vocabularies (mirror SCHEMA.md §3) ----
PILLAR = {"generation", "detection", "evaluation"}
DOMAIN = {"physical", "digital", "intelligent"}
PERSPECTIVE = {"nature", "war", "art", "ai"}
MODALITY = {"rgb", "video", "multispectral", "multimodal", "thermal", "polarization", "depth"}
TASK = {
    "image-cod", "video-cod", "instance-cod", "referring-cod", "collaborative-cod",
    "open-vocab-cos", "survey", "generation", "physical-adversarial", "digital-adversarial",
    "foundation-model", "dataset", "application",
}
STATUS = {"reported", "reproduced"}
METRIC_KEYS = {"Sm", "Fw", "Em", "MAE", "maxF", "meanF", "AP", "AR", "JF", "temporal"}

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL = re.compile(r"^https?://", re.IGNORECASE)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load(name: str):
    p = DATA / name
    if not p.exists():
        err(f"{name}: file missing")
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        err(f"{name}: YAML parse error: {e}")
        return None


def require(entry: dict, fields: list[str], where: str) -> None:
    for f in fields:
        if f not in entry:
            err(f"{where}: missing required field '{f}'")
        elif entry[f] is None or entry[f] == "":
            err(f"{where}: required field '{f}' is null/empty")


def enum(entry: dict, field: str, allowed: set[str], where: str) -> None:
    v = entry.get(field)
    if v is not None and v not in allowed:
        err(f"{where}: '{field}'={v!r} not in {sorted(allowed)}")


def is_source_resolvable(src: str) -> bool:
    if not isinstance(src, str) or not src:
        return False
    if URL.match(src):
        return True
    # otherwise treat as a repo-relative path (e.g. 'projects/coder')
    return (ROOT / src).exists()


def bib_keys() -> set[str]:
    if not BIB.exists():
        warn("book/references.bib not found; skipping bibtex_key consistency check")
        return set()
    return set(re.findall(r"@\w+\{([^,]+),", BIB.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
seen_ids: dict[str, str] = {}        # id -> file (global uniqueness across papers+datasets)
dataset_ids: set[str] = set()
dataset_names: set[str] = set()
data_bibkeys: set[str] = set()


def check_id(entry: dict, where: str) -> str | None:
    _id = entry.get("id")
    if not _id:
        err(f"{where}: missing required field 'id'")
        return None
    if not KEBAB.match(str(_id)):
        err(f"{where}: id '{_id}' is not kebab-case")
    if _id in seen_ids:
        err(f"{where}: duplicate id '{_id}' (also in {seen_ids[_id]})")
    else:
        seen_ids[_id] = where
    return _id


def check_papers(doc) -> None:
    if not isinstance(doc, dict) or "papers" not in doc:
        err("papers.yaml: top-level key 'papers:' missing")
        return
    items = doc["papers"] or []
    if not isinstance(items, list):
        err("papers.yaml: 'papers' must be a list")
        return
    for i, e in enumerate(items):
        where = f"papers[{i}] ({e.get('id', e.get('title', '?'))})"
        if not isinstance(e, dict):
            err(f"{where}: entry is not a mapping"); continue
        check_id(e, where)
        require(e, ["title", "authors", "venue", "year", "pillar", "domain",
                    "perspective", "task", "paper"], where)
        enum(e, "pillar", PILLAR, where)
        enum(e, "domain", DOMAIN, where)
        enum(e, "perspective", PERSPECTIVE, where)
        enum(e, "task", TASK, where)
        if isinstance(e.get("year"), int):
            if not (1850 <= e["year"] <= 2100):
                err(f"{where}: year {e['year']} out of range")
        elif "year" in e:
            err(f"{where}: year must be an integer")
        paper = e.get("paper")
        if paper and not URL.match(str(paper)):
            err(f"{where}: 'paper' must be an http(s) URL")
        code = e.get("code")
        if code and not URL.match(str(code)):
            err(f"{where}: 'code' must be an http(s) URL or null")
        if e.get("bibtex_key"):
            data_bibkeys.add(e["bibtex_key"])
        # referential integrity recorded after datasets are loaded (see resolve_refs)
        e["__where__"] = where  # stash for second pass


def check_datasets(doc) -> None:
    if not isinstance(doc, dict) or "datasets" not in doc:
        err("datasets.yaml: top-level key 'datasets:' missing")
        return
    items = doc["datasets"] or []
    if not isinstance(items, list):
        err("datasets.yaml: 'datasets' must be a list")
        return
    for i, e in enumerate(items):
        where = f"datasets[{i}] ({e.get('id', e.get('name', '?'))})"
        if not isinstance(e, dict):
            err(f"{where}: entry is not a mapping"); continue
        _id = check_id(e, where)
        require(e, ["name", "task", "modality"], where)
        enum(e, "task", TASK, where)
        enum(e, "modality", MODALITY, where)
        link = e.get("link")
        if link and not URL.match(str(link)):
            err(f"{where}: 'link' must be an http(s) URL or null")
        if _id:
            dataset_ids.add(_id)
        if e.get("name"):
            dataset_names.add(e["name"])
        if e.get("bibtex_key"):
            data_bibkeys.add(e["bibtex_key"])


def check_leaderboard(doc) -> None:
    if not isinstance(doc, dict) or "leaderboard" not in doc:
        err("leaderboard.yaml: top-level key 'leaderboard:' missing")
        return
    items = doc["leaderboard"] or []
    if not isinstance(items, list):
        err("leaderboard.yaml: 'leaderboard' must be a list")
        return
    for i, e in enumerate(items):
        where = f"leaderboard[{i}] ({e.get('method', '?')} on {e.get('dataset', '?')})"
        if not isinstance(e, dict):
            err(f"{where}: entry is not a mapping"); continue
        require(e, ["method", "dataset", "task", "metrics", "status", "source", "verified"], where)
        enum(e, "task", TASK, where)
        enum(e, "status", STATUS, where)
        if "verified" in e and not isinstance(e["verified"], bool):
            err(f"{where}: 'verified' must be a boolean")
        # referential integrity: dataset must exist (by id or name)
        ds = e.get("dataset")
        if ds and ds not in dataset_ids and ds not in dataset_names:
            err(f"{where}: dataset '{ds}' not found in datasets.yaml")
        # NO-FABRICATION rule
        metrics = e.get("metrics") or {}
        if not isinstance(metrics, dict):
            err(f"{where}: 'metrics' must be a mapping")
            metrics = {}
        for k, v in metrics.items():
            if k not in METRIC_KEYS:
                err(f"{where}: metric key '{k}' not in {sorted(METRIC_KEYS)}")
            if v is not None:
                if e.get("verified") is not True:
                    err(f"{where}: metric '{k}'={v} is non-null but verified is not true "
                        f"(NO-FABRICATION rule)")
                if not is_source_resolvable(e.get("source", "")):
                    err(f"{where}: metric '{k}'={v} is non-null but 'source' is not "
                        f"resolvable (need URL or existing repo path)")


def resolve_refs(papers_doc) -> None:
    """Second pass: papers.datasets[] must point to existing datasets."""
    if not isinstance(papers_doc, dict):
        return
    for e in papers_doc.get("papers", []) or []:
        if not isinstance(e, dict):
            continue
        where = e.get("__where__", "papers[?]")
        for d in e.get("datasets", []) or []:
            if d not in dataset_ids and d not in dataset_names:
                err(f"{where}: referenced dataset '{d}' not found in datasets.yaml")


def main() -> int:
    papers = load("papers.yaml")
    datasets = load("datasets.yaml")
    leaderboard = load("leaderboard.yaml")

    # datasets first so referential checks can see ids/names
    if datasets is not None:
        check_datasets(datasets)
    if papers is not None:
        check_papers(papers)
    if leaderboard is not None:
        check_leaderboard(leaderboard)
    if papers is not None:
        resolve_refs(papers)

    # WARN-level: bibtex_key vs references.bib (never blocks)
    bk = bib_keys()
    if bk:
        for k in sorted(data_bibkeys - bk):
            warn(f"bibtex_key '{k}' used in data/ but not found in references.bib")

    # Note: rule 7 (awesome/README.md == build_awesome.py output) is enforced in CI
    # via the build-diff step, not here.

    print("=" * 60)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print("=" * 60)
    print(f"check_data: {len(errors)} error(s), {len(warnings)} warning(s)")
    if not errors:
        print("OK — data/*.yaml conforms to SCHEMA.md")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
