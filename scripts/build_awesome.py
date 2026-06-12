#!/usr/bin/env python3
"""Build generated Markdown surfaces from ``data/*.yaml``."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AWESOME_OUT = ROOT / "awesome" / "README.md"
WEB = ROOT / "web"

PILLAR_ORDER = ["generation", "evaluation", "detection"]
PILLAR_TITLES = {
    "generation": "Generation",
    "detection": "Detection",
    "evaluation": "Evaluation",
}


def load_yaml(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def load_data() -> tuple[list[dict], list[dict], list[dict]]:
    papers = load_yaml("papers.yaml")["papers"]
    datasets = load_yaml("datasets.yaml")["datasets"]
    leaderboard = load_yaml("leaderboard.yaml")["leaderboard"]
    return papers, datasets, leaderboard


def format_authors(authors: str | list[str]) -> str:
    if isinstance(authors, list):
        return ", ".join(authors)
    return str(authors)


def format_link(label: str, url: str | None) -> str:
    if not url:
        return ""
    return f" [{label}]({url})"


def format_optional_url(url: str | None, label: str) -> str:
    if not url:
        return ""
    return f"[{label}]({url})"


def format_reference_url(entry: dict) -> str:
    return format_optional_url(entry.get("paper"), "paper")


def format_dataset_link(entry: dict) -> str:
    return format_optional_url(entry.get("link"), "link")


def render_paper_bullet(entry: dict) -> str:
    suffix = [
        f"{format_authors(entry['authors'])}, *{entry['venue']}* {entry['year']}",
        f"`{entry['task']}`",
        f"`{entry['domain']}`",
        f"`{entry['perspective']}`",
    ]
    text = f"- **{entry['title']}** -- " + " | ".join(suffix)
    text += format_link("paper", entry["paper"])
    text += format_link("code", entry.get("code"))
    return text


def sort_papers(papers: list[dict]) -> list[dict]:
    return sorted(papers, key=lambda item: (-item["year"], item["title"].lower()))


def sort_datasets(datasets: list[dict]) -> list[dict]:
    return sorted(datasets, key=lambda item: item["name"].lower())


def sort_verified_rows(leaderboard: list[dict]) -> list[dict]:
    return sorted(
        [row for row in leaderboard if row["verified"]],
        key=lambda item: (item["dataset"], item["method"].lower()),
    )


def render_awesome() -> str:
    papers, datasets, leaderboard = load_data()
    papers_sorted = sort_papers(papers)
    datasets_sorted = sort_datasets(datasets)
    verified_rows = sort_verified_rows(leaderboard)

    lines = [
        "# Awesome Camouflage",
        "",
        "> A generated, schema-backed list of camouflage resources maintained by CamoGED.",
        "> Edit `data/*.yaml`; do not hand-edit this file.",
        "",
        f"- Papers/methods: **{len(papers_sorted)}**",
        f"- Datasets: **{len(datasets_sorted)}**",
        f"- Verified leaderboard rows: **{len(verified_rows)}**",
        "",
        "## Papers by Pillar",
        "",
    ]

    for pillar in PILLAR_ORDER:
        lines.append(f"### {PILLAR_TITLES[pillar]}")
        pillar_entries = [entry for entry in papers_sorted if entry["pillar"] == pillar]
        if not pillar_entries:
            lines.extend(["", "_No entries yet._", ""])
            continue
        lines.append("")
        for entry in pillar_entries:
            lines.append(render_paper_bullet(entry))
        lines.append("")

    lines.extend(
        [
            "## Datasets",
            "",
            "| Name | ID | Task | Modality | Year | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in datasets_sorted:
        year = "" if entry["year"] is None else str(entry["year"])
        notes = entry["notes"] or ""
        lines.append(
            f"| {entry['name']} | `{entry['id']}` | `{entry['task']}` | `{entry['modality']}` | {year} | {notes} |"
        )
    lines.append("")

    lines.extend(["## Leaderboard", ""])
    if verified_rows:
        lines.extend(
            [
                "| Method | Dataset | Task | Metrics | Source |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in verified_rows:
            metrics = ", ".join(
                f"{key}={value}" for key, value in row["metrics"].items() if value is not None
            )
            lines.append(
                f"| {row['method']} | `{row['dataset']}` | `{row['task']}` | {metrics} | {row['source']} |"
            )
    else:
        lines.append("_No verified leaderboard entries yet._")
    lines.append("")

    lines.extend(
        [
            "## Acknowledgements",
            "",
            "- [visionxiang/awesome-camouflaged-object-detection](https://github.com/visionxiang/awesome-camouflaged-object-detection)",
            "- [ChunmingHe/awesome-concealed-object-segmentation](https://github.com/ChunmingHe/awesome-concealed-object-segmentation)",
            "- [clelouch/Awesome-Camouflaged-Object-Detection](https://github.com/clelouch/Awesome-Camouflaged-Object-Detection)",
            "- [GuoleiSun/Awesome-SAM2](https://github.com/GuoleiSun/Awesome-SAM2)",
            "",
        ]
    )
    return "\n".join(lines)


def render_papers_page(papers: list[dict]) -> str:
    papers_sorted = sort_papers(papers)
    lines = [
        "# Papers",
        "",
        "> Generated from `data/papers.yaml`.",
        "",
        f"- Total entries: **{len(papers_sorted)}**",
        "",
    ]
    for pillar in PILLAR_ORDER:
        lines.append(f"## {PILLAR_TITLES[pillar]}")
        lines.append("")
        entries = [entry for entry in papers_sorted if entry["pillar"] == pillar]
        if not entries:
            lines.extend(["_No entries yet._", ""])
            continue
        lines.extend(
            [
                "| Title | Year | Domain | Task | Links |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for entry in entries:
            links = " ".join(
                filter(
                    None,
                    [
                        format_reference_url(entry),
                        format_optional_url(entry.get("code"), "code"),
                    ],
                )
            )
            lines.append(
                f"| {entry['title']} | {entry['year']} | `{entry['domain']}` | `{entry['task']}` | {links} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_models_page(papers: list[dict]) -> str:
    code_entries = [entry for entry in sort_papers(papers) if entry.get("code")]
    groups = [
        (
            "Methods and models",
            [
                entry
                for entry in code_entries
                if entry["task"] not in {"dataset", "survey"} and entry["pillar"] != "evaluation"
            ],
        ),
        (
            "Evaluation tools",
            [
                entry
                for entry in code_entries
                if entry["pillar"] == "evaluation" and entry["task"] != "dataset"
            ],
        ),
        (
            "Dataset and project releases",
            [entry for entry in code_entries if entry["task"] == "dataset"],
        ),
        (
            "Survey and curated indexes",
            [entry for entry in code_entries if entry["task"] == "survey"],
        ),
    ]
    lines = [
        "# Code",
        "",
        "> Code, dataset, and project links derived from `data/papers.yaml`.",
        "",
        f"- Entries with links: **{len(code_entries)}**",
        "",
    ]
    if not code_entries:
        lines.extend(["_No code-linked entries yet._", ""])
        return "\n".join(lines) + "\n"

    for title, entries in groups:
        if not entries:
            continue
        lines.extend(
            [
                f"## {title}",
                "",
                "| Title | Year | Pillar | Task | Link | Paper |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for entry in entries:
            lines.append(
                f"| {entry['title']} | {entry['year']} | `{entry['pillar']}` | `{entry['task']}` | "
                f"{format_optional_url(entry['code'], 'link')} | {format_reference_url(entry)} |"
            )
        lines.append("")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_datasets_page(datasets: list[dict]) -> str:
    datasets_sorted = sort_datasets(datasets)
    lines = [
        "# Datasets",
        "",
        "> Generated from `data/datasets.yaml`.",
        "",
        f"- Total datasets: **{len(datasets_sorted)}**",
        "",
        "| Name | Task | Modality | Size | Split | Year | Link | License | Reference |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in datasets_sorted:
        lines.append(
            f"| {entry['name']} | `{entry['task']}` | `{entry['modality']}` | {entry.get('size') or ''} | "
            f"{entry.get('split') or ''} | {entry.get('year') or ''} | {format_dataset_link(entry)} | "
            f"{entry.get('license') or ''} | `{entry.get('bibtex_key') or ''}` |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def render_leaderboard_page(leaderboard: list[dict]) -> str:
    verified_rows = sort_verified_rows(leaderboard)
    tracked_rows = sorted(leaderboard, key=lambda item: (item["dataset"], item["method"].lower()))
    unverified_rows = [row for row in tracked_rows if not row["verified"]]
    lines = [
        "# Leaderboard",
        "",
        "> Generated from `data/leaderboard.yaml`.",
        "",
        f"- Tracked rows: **{len(tracked_rows)}**",
        f"- Verified rows: **{len(verified_rows)}**",
        "",
        "## Verified results",
        "",
    ]
    if verified_rows:
        lines.extend(
            [
                "| Method | Dataset | Task | Metrics | Protocol | Source |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in verified_rows:
            metrics = ", ".join(
                f"{key}={value}" for key, value in row["metrics"].items() if value is not None
            )
            lines.append(
                f"| {row['method']} | `{row['dataset']}` | `{row['task']}` | {metrics} | "
                f"{row.get('protocol') or ''} | {row['source']} |"
            )
    else:
        lines.append("_No verified leaderboard rows yet. Unverified metrics stay null by policy._")
    lines.extend(
        [
            "",
            "## Tracked methods awaiting verification",
            "",
        ]
    )
    if unverified_rows:
        lines.extend(
            [
                "| Method | Dataset | Status | Source |",
                "| --- | --- | --- | --- |",
            ]
        )
        for row in unverified_rows:
            lines.append(
                f"| {row['method']} | `{row['dataset']}` | `{row['status']}` | {row['source']} |"
            )
    else:
        lines.append("_No unverified tracked rows._")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_demo_page() -> str:
    lines = [
        "# Demo",
        "",
        "This page covers camouflage metrics that can run without large datasets, model weights, or external services. Heavy learned backends remain out of scope for the browser demo; the repository exposes lightweight, deterministic surrogates where that is useful for smoke tests and protocol comparisons.",
        "",
        "## Quick artifacts",
        "",
        "| Bundle | Overlay | Error map | PR curve | Scores | Diagnostics |",
        "| --- | --- | --- | --- | --- | --- |",
        "| COD sample 1 | [overlay](./demo-artifacts/cod-sample1/mask_overlay.png) | [error](./demo-artifacts/cod-sample1/error_map.png) | [PR](./demo-artifacts/cod-sample1/pr_curve.png) | [scores](./demo-artifacts/cod-sample1/scores.json) | [diagnostics](./demo-artifacts/cod-sample1/diagnostics.json) |",
        "| COD sample 2 | [overlay](./demo-artifacts/cod-sample2/mask_overlay.png) | [error](./demo-artifacts/cod-sample2/error_map.png) | [PR](./demo-artifacts/cod-sample2/pr_curve.png) | [scores](./demo-artifacts/cod-sample2/scores.json) | [diagnostics](./demo-artifacts/cod-sample2/diagnostics.json) |",
        "| Demo-set generation surrogate | - | - | - | [generation distances](./demo-artifacts/cod-demo-generation.json) | - |",
        "",
        "## Metric coverage",
        "",
        "| Family | Metrics | Browser/HF | CLI/Colab | Default threshold or assumption |",
        "| --- | --- | --- | --- | --- |",
        "| Detection | MAE, weighted F, S-measure, E-measure, F-measure | yes | yes | mask threshold `0.5` for binary visualizations |",
        "| PR diagnostics | precision, recall, PR curve | static artifacts; HF JSON | yes | adaptive and sweep thresholds from `camo-eval` |",
        "| Region/boundary | IoU, Dice, BoundaryIoU | yes | yes | mask threshold `0.5`; boundary dilation ratio from API default |",
        "| Perceptual mask similarity | SSIM, MS-SSIM | yes | yes | normalized grayscale/RGB inputs in `[0,1]` or `[0,255]` |",
        "| Lightweight generation similarity | FID_lite, KID_lite, LPIPS_lite, DISTS_lite | static artifacts for bundled data; pairwise in HF | yes | deterministic handcrafted features; no Inception/LPIPS weights |",
        "| Clutter and difficulty | edge density, subband entropy, feature congestion, camouflage difficulty | static artifacts; HF when a scene is supplied | yes | adaptive edge threshold `mean + std`; near-background ring default |",
        "| Signature analysis | thermal contrast, signal-to-clutter ratio, spectral angle mapper | documented CLI/API path | yes | caller supplies target/background or signatures |",
        "| Robustness | attack success rate, AP drop, transferability | API/CLI-adjacent only | yes | requires paired clean/attacked outputs supplied by caller |",
        "",
        "## Run surfaces",
        "",
        "- Web: this page hosts static outputs generated from `camo-eval/demo_data/cod_sota_masks`.",
        "- HF Space: source is ready in [web/hf-space](https://github.com/MichaelCSHN/CamoGED/tree/main/web/hf-space); deploy it as a Gradio Space when an interactive hosted endpoint is needed.",
        "- Colab: open the notebook at [camo_eval_colab_demo.ipynb](https://colab.research.google.com/github/MichaelCSHN/CamoGED/blob/main/camo-eval/notebooks/camo_eval_colab_demo.ipynb).",
        "- GitHub/CLI: install with `pip install -e ./camo-eval[full]`, then run the commands below.",
        "",
        "```bash",
        "camo-eval list-metrics",
        "camo-eval visualize --pred camo-eval/demo_data/cod_sota_masks/pred/sample1.png --gt camo-eval/demo_data/cod_sota_masks/gt/sample1.png --output-dir demo-output",
        "camo-eval image-diagnostics --image camo-eval/demo_data/cod_sota_masks/images/sample1.png --mask camo-eval/demo_data/cod_sota_masks/gt/sample1.png",
        "camo-eval generation-distance --real-dir camo-eval/demo_data/cod_sota_masks/gt --fake-dir camo-eval/demo_data/cod_sota_masks/pred",
        "```",
        "",
        "## Explicit non-goals",
        "",
        "- The web demo does not download large pretrained models or benchmark datasets.",
        "- `FID_lite`, `KID_lite`, `LPIPS_lite`, and `DISTS_lite` are lightweight reproducibility surrogates, not replacements for heavyweight learned backends in final papers.",
        "- Full benchmark claims belong in verified leaderboard entries with resolvable sources, not in ad hoc demo artifacts.",
        "",
    ]
    return "\n".join(lines)


def render_awesome_page() -> str:
    awesome_body = render_awesome().splitlines()
    lines = [
        "# Awesome",
        "",
        "> Mirror of the generated Awesome index.",
        "",
    ]
    lines.extend(awesome_body[1:])
    return "\n".join(lines) + "\n"


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_outputs() -> None:
    papers, datasets, leaderboard = load_data()
    write_text(AWESOME_OUT, render_awesome())
    write_text(WEB / "papers.md", render_papers_page(papers))
    write_text(WEB / "models.md", render_models_page(papers))
    write_text(WEB / "datasets.md", render_datasets_page(datasets))
    write_text(WEB / "leaderboard.md", render_leaderboard_page(leaderboard))
    write_text(WEB / "demo.md", render_demo_page())
    write_text(WEB / "awesome.md", render_awesome_page())


def render() -> str:
    """Backward-compatible helper used by ``check_data.py``."""

    return render_awesome()


def main() -> int:
    write_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
