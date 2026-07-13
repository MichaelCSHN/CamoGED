#!/usr/bin/env python3
"""Apply compatibility and editorial patches after the one-shot migration."""

from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]

build_path = root / "scripts/build_awesome.py"
text = build_path.read_text(encoding="utf-8")
marker = "\ndef main() -> None:\n"
render_function = '''\ndef render() -> str:\n    """Return the generated curated README for legacy deterministic checks."""\n\n    resources, datasets, _results, config = load_data()\n    return render_curated(config, resources, datasets)\n\n\n'''
if "def render() -> str:" not in text:
    if marker not in text:
        raise SystemExit("build_awesome main marker not found")
    text = text.replace(marker, render_function + marker, 1)
build_path.write_text(text, encoding="utf-8")

papers_path = root / "data/papers.yaml"
document = yaml.safe_load(papers_path.read_text(encoding="utf-8")) or {"papers": []}
descriptions = {
    "hginet2024": "Graph-interaction transformer using dynamic token clustering for fine-grained camouflaged object segmentation.",
    "samvcos2025": "Systematic evaluation and adaptation study of SAM2 under video camouflaged object segmentation protocols.",
    "camosam2-2025": "Automatic motion-appearance prompt induction and multi-prompt refinement framework built around SAM2.",
    "camdiff2023": "Diffusion-based camouflage image augmentation study evaluating synthetic data for downstream COD training.",
    "talas2017military": "Comparative study of how military camouflage patterns evolve under perceptual, cultural, and operational pressures.",
    "heusel2017fid": "Foundational GAN evaluation paper introducing the Fréchet Inception Distance for distribution-level comparison.",
    "zhang2018lpips": "Foundational learned perceptual similarity study introducing LPIPS and validating deep features against human judgments.",
}
for item in document.get("papers", []):
    replacement = descriptions.get(item.get("id"))
    if replacement:
        item["description"] = replacement
        if not item.get("notes"):
            item["notes"] = replacement
papers_path.write_text(
    yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=100),
    encoding="utf-8",
)
print("Awesome compatibility and legacy descriptions prepared.")
