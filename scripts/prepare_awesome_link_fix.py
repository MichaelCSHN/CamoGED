#!/usr/bin/env python3
"""Correct the generated website link for source-level offline link checks."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/build_awesome.py"
text = path.read_text(encoding="utf-8")
old = 'catalog_link="./catalog"'
new = 'catalog_link="./catalog.md"'
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("catalog link marker not found")
path.write_text(text, encoding="utf-8")
print("Awesome website catalog link corrected.")
