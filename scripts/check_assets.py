#!/usr/bin/env python3
"""Enforce CamoGED's third-party asset registration policy."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "THIRD_PARTY_ASSETS.yml"
RISKY_PUBLIC_ROOTS = [ROOT / "web/public/demo-artifacts"]
REQUIRED_ASSET_FIELDS = {
    "id",
    "path",
    "source",
    "owner",
    "license",
    "redistribution_allowed",
    "last_verified",
}


def main() -> int:
    errors: list[str] = []
    if not LEDGER.exists():
        errors.append("THIRD_PARTY_ASSETS.yml is missing")
        document = {}
    else:
        document = yaml.safe_load(LEDGER.read_text(encoding="utf-8")) or {}

    entries = document.get("assets") or []
    if not isinstance(entries, list):
        errors.append("assets must be a list")
        entries = []

    registered_paths: set[str] = set()
    for index, entry in enumerate(entries):
        where = f"assets[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = sorted(REQUIRED_ASSET_FIELDS - set(entry))
        if missing:
            errors.append(f"{where} missing fields: {', '.join(missing)}")
            continue
        relative_path = str(entry["path"])
        registered_paths.add(relative_path.rstrip("/"))
        if entry["redistribution_allowed"] is not True:
            errors.append(f"{where} is registered but not permitted for redistribution")
        if not (ROOT / relative_path).exists():
            errors.append(f"{where} path does not exist: {relative_path}")

    for root in RISKY_PUBLIC_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative not in registered_paths and not any(
                relative.startswith(prefix + "/") for prefix in registered_paths
            ):
                errors.append(f"unregistered public demo asset: {relative}")

    for error in errors:
        print(f"ERROR {error}")
    print(f"check_assets: {len(errors)} error(s), {len(entries)} registered asset(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
