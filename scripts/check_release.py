#!/usr/bin/env python3
"""Validate release metadata against the repository's preview/release state."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "RELEASE_MANIFEST.yml"
PYPROJECT = ROOT / "camo-eval/pyproject.toml"
INIT = ROOT / "camo-eval/src/camo_eval/__init__.py"
WEB_PACKAGE = ROOT / "web/package.json"
CITATION = ROOT / "CITATION.cff"


def _extract(pattern: str, text: str, source: str, errors: list[str]) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        errors.append(f"could not extract version from {source}")
        return None
    return match.group(1)


def main() -> int:
    errors: list[str] = []
    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    status = document.get("release_status")
    tag = document.get("release_tag")
    date = document.get("release_date")
    source_commit = document.get("source_commit")

    if status == "unreleased-research-preview":
        if any(value is not None for value in (tag, date, source_commit)):
            errors.append(
                "unreleased preview must keep tag, date, and source_commit null"
            )
    elif status == "released":
        if not all(
            isinstance(value, str) and value for value in (tag, date, source_commit)
        ):
            errors.append("released status requires tag, date, and source_commit")
    else:
        errors.append(f"unsupported release_status: {status!r}")

    components = document.get("components", {})
    camo_eval_version = components.get("camo_eval", {}).get("version")
    pyproject_version = _extract(
        r'^version\s*=\s*"([^"]+)"',
        PYPROJECT.read_text(encoding="utf-8"),
        "camo-eval/pyproject.toml",
        errors,
    )
    init_version = _extract(
        r'^__version__\s*=\s*"([^"]+)"',
        INIT.read_text(encoding="utf-8"),
        "camo_eval/__init__.py",
        errors,
    )
    if camo_eval_version != pyproject_version or camo_eval_version != init_version:
        errors.append(
            "camo-eval version drift: "
            f"manifest={camo_eval_version!r}, pyproject={pyproject_version!r}, "
            f"init={init_version!r}"
        )

    web_package = json.loads(WEB_PACKAGE.read_text(encoding="utf-8"))
    web_manifest = components.get("website", {})
    if web_manifest.get("version") != web_package.get("version"):
        errors.append(
            "website version drift: "
            f"manifest={web_manifest.get('version')!r}, package={web_package.get('version')!r}"
        )
    if web_package.get("license") != "MIT" or "MIT" not in str(
        web_manifest.get("license")
    ):
        errors.append("website MIT sub-license is not consistently recorded")

    citation = yaml.safe_load(CITATION.read_text(encoding="utf-8")) or {}
    citation_version = citation.get("version")
    if status == "unreleased-research-preview" and not str(citation_version).endswith(
        "-pre"
    ):
        errors.append("unreleased root citation version must end with '-pre'")
    if citation.get("date-released") is not None and status != "released":
        errors.append("date-released is forbidden before a tagged release")

    for error in errors:
        print(f"ERROR {error}")
    print(f"check_release: {len(errors)} error(s); status={status}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
