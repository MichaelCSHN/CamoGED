#!/usr/bin/env python3
"""Apply small compatibility patches before the one-shot Awesome migration."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/build_awesome.py"
text = path.read_text(encoding="utf-8")
marker = "\ndef main() -> None:\n"
render_function = '''\ndef render() -> str:\n    """Return the generated curated README for legacy deterministic checks."""\n\n    resources, datasets, _results, config = load_data()\n    return render_curated(config, resources, datasets)\n\n\n'''
if "def render() -> str:" not in text:
    if marker not in text:
        raise SystemExit("build_awesome main marker not found")
    text = text.replace(marker, render_function + marker, 1)
path.write_text(text, encoding="utf-8")
print("Awesome compatibility hook prepared.")
