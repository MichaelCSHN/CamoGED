#!/usr/bin/env python3
"""Normalize exact source markers before running the one-shot editorial rewrite."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/apply_book_editorial_revision.py"
text = path.read_text(encoding="utf-8")
replacements = {
    "## 11.7 [原创] coder：本平台的图像 COD 锚点 {#sec-11-coder}":
        "## 11.7 [原创] coder：图像 COD 原创方法 {#sec-coder}",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"editorial script marker not found: {old}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
print("Editorial script markers normalized.")
