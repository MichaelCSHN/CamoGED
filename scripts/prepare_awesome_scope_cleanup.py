#!/usr/bin/env python3
"""Remove Demo page generation from the Awesome specialist surface."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/build_awesome.py"
text = path.read_text(encoding="utf-8")
old = '    write(WEB / "demo.md", render_demo_page())\n'
if old in text:
    text = text.replace(old, "", 1)
elif 'write(WEB / "demo.md"' in text:
    raise SystemExit("unexpected demo generation call")
path.write_text(text, encoding="utf-8")
print("Demo page removed from Awesome generation scope.")
