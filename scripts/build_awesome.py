#!/usr/bin/env python3
"""Build `awesome/README.md` from `data/*.yaml`."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "awesome" / "README.md"

PILLAR_ORDER = ["generation", "detection", "evaluation"]
PILLAR_TITLES = {
    "generation": "Generation",
    "detection": "Detection",
    "evaluation": "Evaluation",
}


def load_yaml(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def format_authors(authors) -> str:
    if isinstance(authors, list):
        return ", ".join(authors)
    return str(authors)


def format_link(label: str, url: str | None) -> str:
    if not url:
        return ""
    return f" [{label}]({url})"


def render_paper(entry: dict) -> str:
    suffix = []
    suffix.append(
        f"{format_authors(entry['authors'])}, *{entry['venue']}* {entry['year']}"
    )
    suffix.append(f"`{entry['task']}`")
    suffix.append(f"`{entry['domain']}`")
    suffix.append(f"`{entry['perspective']}`")
    text = f"- **{entry['title']}** — " + " · ".join(suffix)
    text += format_link("paper", entry["paper"])
    text += format_link("code", entry.get("code"))
    return text


def render() -> str:
    papers = load_yaml("papers.yaml")["papers"]
    datasets = load_yaml("datasets.yaml")["datasets"]
    leaderboard = load_yaml("leaderboard.yaml")["leaderboard"]

    papers_sorted = sorted(papers, key=lambda item: (-item["year"], item["title"]))
    datasets_sorted = sorted(datasets, key=lambda item: item["name"].lower())
    verified_rows = sorted(
        [row for row in leaderboard if row["verified"]],
        key=lambda item: (item["dataset"], item["method"].lower()),
    )

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
            lines.append("")
            lines.append("_No entries yet._")
            lines.append("")
            continue
        lines.append("")
        for entry in pillar_entries:
            lines.append(render_paper(entry))
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

    lines.append("## Leaderboard")
    lines.append("")
    if verified_rows:
        lines.extend(
            [
                "| Method | Dataset | Task | Metrics | Source |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in verified_rows:
            metrics = ", ".join(
                f"{key}={value}"
                for key, value in row["metrics"].items()
                if value is not None
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


def main() -> int:
    content = render().rstrip() + "\n"
    OUT.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
