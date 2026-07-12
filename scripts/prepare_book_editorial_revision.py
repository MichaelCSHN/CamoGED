#!/usr/bin/env python3
"""Normalize exact source markers and patch the one-shot editorial rewrite safely."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/apply_book_editorial_revision.py"
text = path.read_text(encoding="utf-8")

# Normalize a heading marker. The preparation step must be idempotent because
# push and pull-request events may briefly overlap on the same branch.
old_heading = "## 11.7 [原创] coder：本平台的图像 COD 锚点 {#sec-11-coder}"
new_heading = "## 11.7 [原创] coder：图像 COD 原创方法 {#sec-coder}"
if old_heading in text:
    text = text.replace(old_heading, new_heading)
elif new_heading not in text:
    raise SystemExit("neither the old nor normalized coder heading marker was found")

# re.sub treats backslashes in a replacement string as escape sequences. The
# editorial summaries contain LaTeX, so use a callable replacement to preserve
# those backslashes literally.
old_subn = "new, n = re.subn(pattern, repl, text, count=count, flags=flags)"
new_subn = "new, n = re.subn(pattern, lambda _match: repl, text, count=count, flags=flags)"
if old_subn in text:
    text = text.replace(old_subn, new_subn)
elif new_subn not in text:
    raise SystemExit("regex replacement implementation marker was not found")

path.write_text(text, encoding="utf-8")
print("Editorial script markers normalized and regex replacement made literal-safe.")
