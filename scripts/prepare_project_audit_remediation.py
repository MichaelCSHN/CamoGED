#!/usr/bin/env python3
"""Patch literal escapes in the one-shot project remediation script."""

from pathlib import Path

path = Path(__file__).with_name("apply_project_audit_remediation.py")
text = path.read_text(encoding="utf-8")
old = '    expected = render().rstrip() + "\\n"\n'
new = '    expected = render().rstrip() + "\\\\n"\n'
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("expected generated-newline marker not found")
path.write_text(text, encoding="utf-8")
print("Prepared project audit remediation script.")
