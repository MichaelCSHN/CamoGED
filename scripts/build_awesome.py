#!/usr/bin/env python3
"""Build the curated Awesome list and the complete CamoGED research catalog.

The accepted metadata lives in ``data/papers.yaml`` and ``data/datasets.yaml``.
``data/awesome.yaml`` controls only human curation and presentation; automated
discovery never writes directly to accepted metadata.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AWESOME_OUT = ROOT / "awesome" / "README.md"
WEB = ROOT / "web"


def load_yaml(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


def load_data() -> tuple[list[dict], list[dict], list[dict], dict]:
    papers = load_yaml("papers.yaml").get("papers", [])
    datasets = load_yaml("datasets.yaml").get("datasets", [])
    results = load_yaml("leaderboard.yaml").get("leaderboard", [])
    config = load_yaml("awesome.yaml")
    return papers, datasets, results, config


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def authors(value: str | list[str]) -> str:
    return ", ".join(value) if isinstance(value, list) else str(value)


def link(label: str, url: str | None) -> str:
    return f"[{label}]({url})" if url else ""


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def sort_resources(resources: Iterable[dict]) -> list[dict]:
    return sorted(
        resources, key=lambda item: (-int(item.get("year") or 0), item["title"].lower())
    )


def matches(entry: dict, rule: dict) -> bool:
    """Match if any configured axis intersects; a section is intentionally broad."""

    for field, wanted in rule.items():
        current = as_list(entry.get(field))
        if set(current) & set(as_list(wanted)):
            return True
    return False


def badge(entry: dict) -> str:
    status = entry.get("verification_status", "unverified")
    publication = entry.get("publication_status", "unknown")
    return f"`{publication}` · `{status}`"


def resource_bullet(entry: dict) -> str:
    links = " · ".join(
        item
        for item in [
            link("source", entry.get("paper")),
            link("code/project", entry.get("code")),
        ]
        if item
    )
    axis = ", ".join(as_list(entry.get("tasks"))[:4])
    description = entry.get("description") or entry.get("notes") or ""
    return (
        f"- **{entry['title']}** — {authors(entry['authors'])}, *{entry['venue']}* "
        f"({entry['year']}). {md_escape(description)}  \n"
        f"  {badge(entry)} · `{md_escape(entry.get('resource_type', 'paper'))}` · "
        f"{md_escape(axis)}" + (f" · {links}" if links else "")
    )


def curated_resources(resources: list[dict]) -> list[dict]:
    return sort_resources(item for item in resources if item.get("curated") is True)


def latest_resources(resources: list[dict], limit: int = 12) -> list[dict]:
    return sorted(
        resources,
        key=lambda item: (
            str(item.get("date_added") or ""),
            int(item.get("year") or 0),
        ),
        reverse=True,
    )[:limit]


def render_curated(
    config: dict, resources: list[dict], datasets: list[dict], *, catalog_link: str
) -> str:
    selected = curated_resources(resources)
    by_id = {item["id"]: item for item in resources}
    core = [
        by_id[item_id] for item_id in config.get("core_reading", []) if item_id in by_id
    ]
    latest = latest_resources(resources)

    lines = [
        "# Awesome Camouflage",
        "",
        "> A human-curated reading map across camouflage vision, natural camouflage, military history,",
        "> art/design, generation, and assessment. The complete schema-backed catalog is published",
        f"> separately at [Research Catalog]({catalog_link}).",
        "",
        f"- Curated resources: **{len(selected)}**",
        f"- Accepted catalog records: **{len(resources)}**",
        f"- Datasets/benchmarks: **{len(datasets)}**",
        f"- Coverage reviewed through: **{config.get('coverage_through', 'unknown')}**",
        f"- Last human review: **{config.get('last_human_review', 'unknown')}**",
        "- Update policy: **automated discovery, human acceptance**",
        "",
        "## Scope and status",
        "",
        config.get("scope_note", ""),
        "",
        "This README is the concise curated layer. Metadata-only or experimental records may appear in",
        "the full catalog but are not automatically promoted here. Automated scans open triage issues;",
        "they never merge entries directly.",
        "",
        "## Start here",
        "",
    ]
    lines.extend(resource_bullet(item) for item in core)

    lines.extend(["", "## Latest accepted additions", ""])
    lines.extend(resource_bullet(item) for item in latest)

    for section in config.get("sections", []):
        entries = [item for item in selected if matches(item, section.get("match", {}))]
        if not entries:
            continue
        lines.extend(["", f"## {section['title']}", ""])
        lines.extend(resource_bullet(item) for item in entries)

    lines.extend(
        [
            "",
            "## Dataset and benchmark index",
            "",
            "| Dataset | Task | Modality | Year | Availability | License status | Last reviewed |",
            "|---|---|---:|---:|---|---|---|",
        ]
    )
    for item in sorted(
        datasets,
        key=lambda value: (-int(value.get("year") or 0), value["name"].lower()),
    ):
        lines.append(
            f"| {link(item['name'], item.get('link')) or item['name']} | `{item['task']}` | "
            f"`{item['modality']}` | {item.get('year') or ''} | "
            f"{item.get('publication_status') or ''} | `{item.get('license_status') or 'unknown'}` | "
            f"{item.get('last_verified') or ''} |"
        )

    lines.extend(
        [
            "",
            "## Dynamic maintenance",
            "",
            "- Weekly discovery workflow: `.github/workflows/awesome-discovery.yml`.",
            "- Candidate reports: GitHub issues carrying the `awesome:triage` label.",
            "- Human acceptance workflow: `.github/workflows/awesome-curation.yml`.",
            "- Query definitions: `data/discovery_queries.yaml`.",
            "- Curation rules and evidence levels: `docs/AWESOME_GOVERNANCE.md`.",
            "",
            "## Related curated lists",
            "",
        ]
    )
    for url in config.get("external_candidate_sources", []):
        lines.append(f"- {url}")
    lines.append("")
    return "\n".join(lines)


def render_catalog(resources: list[dict], config: dict) -> str:
    type_counts = Counter(item.get("resource_type", "paper") for item in resources)
    task_counts = Counter(
        task for item in resources for task in as_list(item.get("tasks"))
    )
    modality_counts = Counter(
        modality for item in resources for modality in as_list(item.get("modalities"))
    )
    context_counts = Counter(
        context for item in resources for context in as_list(item.get("contexts"))
    )

    lines = [
        "# CamoGED Research Catalog",
        "",
        "> Complete accepted metadata catalog. Inclusion does not imply endorsement, full-text availability,",
        "> reproduced results, or a verified license. Use the status columns.",
        "",
        f"- Accepted records: **{len(resources)}**",
        f"- Coverage reviewed through: **{config.get('coverage_through', 'unknown')}**",
        f"- Verified metadata: **{sum(item.get('verification_status') == 'verified' for item in resources)}**",
        f"- Metadata-only: **{sum(item.get('verification_status') == 'metadata-only' for item in resources)}**",
        "",
        "## Coverage matrix",
        "",
        f"- Resource types: {', '.join(f'`{key}` {value}' for key, value in type_counts.most_common())}",
        f"- Leading tasks: {', '.join(f'`{key}` {value}' for key, value in task_counts.most_common(15))}",
        f"- Modalities: {', '.join(f'`{key}` {value}' for key, value in modality_counts.most_common())}",
        f"- Contexts: {', '.join(f'`{key}` {value}' for key, value in context_counts.most_common())}",
        "",
        "## All resources",
        "",
        "| Year | Resource | Type | Tasks | Modalities | Supervision | Status | Links |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for item in sort_resources(resources):
        links = " ".join(
            value
            for value in [
                link("source", item.get("paper")),
                link("code", item.get("code")),
            ]
            if value
        )
        lines.append(
            f"| {item.get('year') or ''} | **{md_escape(item['title'])}**<br>{md_escape(item.get('description') or '')} | "
            f"`{md_escape(item.get('resource_type', 'paper'))}` | "
            f"{md_escape(', '.join(as_list(item.get('tasks'))))} | "
            f"{md_escape(', '.join(as_list(item.get('modalities'))))} | "
            f"{md_escape(', '.join(as_list(item.get('supervision'))))} | "
            f"{badge(item)}<br>reviewed {item.get('last_verified') or ''} | {links} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_updates(config: dict, resources: list[dict]) -> str:
    latest = latest_resources(resources, 20)
    lines = [
        "# Awesome update status",
        "",
        f"- Coverage reviewed through: **{config.get('coverage_through', 'unknown')}**",
        f"- Last human review: **{config.get('last_human_review', 'unknown')}**",
        "- Automated scan: see the latest GitHub issue labeled `awesome:triage`.",
        "- Automated candidates are not accepted records until a human-reviewed PR is merged.",
        "",
        "## Latest accepted records",
        "",
    ]
    lines.extend(resource_bullet(item) for item in latest)
    lines.extend(
        [
            "",
            "## Maintenance surfaces",
            "",
            "- Discovery query configuration: `data/discovery_queries.yaml`",
            "- Candidate scanner: `scripts/discover_awesome.py`",
            "- Candidate acceptance tool: `scripts/accept_awesome_candidates.py`",
            "- Governance: `docs/AWESOME_GOVERNANCE.md`",
            "",
        ]
    )
    return "\n".join(lines)


def render_papers_page(resources: list[dict]) -> str:
    return "# Papers and resources\n\nThe complete multi-axis catalog has moved to [Research Catalog](./catalog.md).\n"


def render_models_page(resources: list[dict]) -> str:
    entries = [item for item in sort_resources(resources) if item.get("code")]
    lines = [
        "# Code & Resources",
        "",
        "> Project and code links from accepted catalog records. A link is not a reproduction claim.",
        "",
        "| Resource | Year | Tasks | Status | Link |",
        "|---|---:|---|---|---|",
    ]
    for item in entries:
        lines.append(
            f"| {md_escape(item['title'])} | {item.get('year') or ''} | "
            f"{md_escape(', '.join(as_list(item.get('tasks'))))} | {badge(item)} | "
            f"{link('project', item.get('code'))} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_datasets_page(datasets: list[dict]) -> str:
    lines = [
        "# Datasets and benchmarks",
        "",
        "> Metadata registry only. Unknown or restricted licenses prohibit redistribution by CamoGED.",
        "",
        "| Dataset | Task | Modality | Size | Split | Year | License | Status | Last reviewed |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    for item in sorted(
        datasets,
        key=lambda value: (-int(value.get("year") or 0), value["name"].lower()),
    ):
        lines.append(
            f"| {link(item['name'], item.get('link')) or item['name']} | `{item['task']}` | "
            f"`{item['modality']}` | {md_escape(item.get('size') or '')} | "
            f"{md_escape(item.get('split') or '')} | {item.get('year') or ''} | "
            f"{md_escape(item.get('license') or 'unknown')} | `{item.get('license_status') or 'unknown'}` | "
            f"{item.get('last_verified') or ''} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_results(results: list[dict]) -> str:
    rows = sorted(
        [item for item in results if item.get("verified") is True],
        key=lambda item: (item["dataset"], item["method"].lower()),
    )
    lines = [
        "# Verified Results Registry",
        "",
        "> Source-checked result records. This is not a comprehensive SOTA ranking.",
        "",
        "| Method | Dataset | Task | Metrics | Protocol | Implementation | Verified | Source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in rows:
        metrics = ", ".join(
            f"{key}={value}"
            for key, value in item["metrics"].items()
            if value is not None
        )
        lines.append(
            f"| {item['method']} | `{item['dataset']}` | `{item['task']}` | {metrics} | "
            f"{md_escape(item.get('protocol') or '')} | `{item['metric_implementation']}` | "
            f"{item['last_verified']} / {item['verified_by']} | {item['source']} |"
        )
    if not rows:
        lines.append("| _No verified results_ | | | | | | | |")
    lines.append("")
    return "\n".join(lines)


def render_demo_page() -> str:
    return """---
layout: page
---

# Synthetic teaching demo

<CamoDemo />

The browser demo uses deterministic synthetic scenes and exploratory heuristics. It is not a model inference service, a standard camouflage score, or part of the Awesome catalog.
"""


def write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render() -> str:
    """Return the generated curated README for legacy deterministic checks."""

    resources, datasets, _results, config = load_data()
    return render_curated(config, resources, datasets, catalog_link="../web/catalog.md")


def main() -> None:
    resources, datasets, results, config = load_data()
    write(
        AWESOME_OUT,
        render_curated(config, resources, datasets, catalog_link="../web/catalog.md"),
    )
    write(
        WEB / "awesome.md",
        render_curated(config, resources, datasets, catalog_link="./catalog.md"),
    )
    write(WEB / "catalog.md", render_catalog(resources, config))
    write(WEB / "updates.md", render_updates(config, resources))
    write(WEB / "papers.md", render_papers_page(resources))
    write(WEB / "models.md", render_models_page(resources))
    write(WEB / "datasets.md", render_datasets_page(datasets))
    write(WEB / "leaderboard.md", render_results(results))
    write(WEB / "demo.md", render_demo_page())
    print(
        f"Generated Awesome/catalog surfaces: {len(resources)} resources, "
        f"{sum(item.get('curated') is True for item in resources)} curated, {len(datasets)} datasets"
    )


if __name__ == "__main__":
    main()
