#!/usr/bin/env python3
"""Apply final specialist-review fixes before the last acceptance run."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]

# Render repository and website Awesome surfaces with context-correct links.
build_path = root / "scripts/build_awesome.py"
build = build_path.read_text(encoding="utf-8")
replacements = {
    "def render_curated(config: dict, resources: list[dict], datasets: list[dict]) -> str:":
        "def render_curated(\n    config: dict, resources: list[dict], datasets: list[dict], *, catalog_link: str\n) -> str:",
    '"> separately at [`web/catalog.md`](../web/catalog.md).",':
        'f"> separately at [Research Catalog]({catalog_link}).",',
    "return render_curated(config, resources, datasets)":
        'return render_curated(config, resources, datasets, catalog_link="../web/catalog.md")',
    "    curated = render_curated(config, resources, datasets)\n    write(AWESOME_OUT, curated)\n    write(WEB / \"awesome.md\", curated)":
        '    write(\n        AWESOME_OUT,\n        render_curated(config, resources, datasets, catalog_link="../web/catalog.md"),\n    )\n    write(\n        WEB / "awesome.md",\n        render_curated(config, resources, datasets, catalog_link="./catalog"),\n    )',
}
for old, new in replacements.items():
    if old in build:
        build = build.replace(old, new, 1)
    elif new not in build:
        raise SystemExit(f"build_awesome patch marker not found: {old[:80]!r}")
build_path.write_text(build, encoding="utf-8")

# Make discovery resilient to individual query failures while allowing PR smoke
# tests to require at least one successful query from each configured source.
discovery_path = root / "scripts/discover_awesome.py"
discovery = discovery_path.read_text(encoding="utf-8")
old_report = '''        f"- Query count: **{payload['query_count']}**",\n        f"- New candidates after deduplication: **{len(payload['candidates'])}**",\n        f"- Minimum publication year: **{payload['min_year']}**",\n        "- Policy: automated discovery only; human review is required before acceptance.",\n        "",\n    ]\n'''
new_report = '''        f"- Configured queries: **{payload['query_count']}**",\n        f"- Successful queries: **{payload['successful_query_count']}**",\n        f"- Successful sources: **{', '.join(payload['successful_sources']) or 'none'}**",\n        f"- Query errors: **{len(payload['query_errors'])}**",\n        f"- New candidates after deduplication: **{len(payload['candidates'])}**",\n        f"- Minimum publication year: **{payload['min_year']}**",\n        "- Policy: automated discovery only; human review is required before acceptance.",\n        "",\n    ]\n    if payload["query_errors"]:\n        lines.extend(["## Query errors", ""])\n        for error in payload["query_errors"]:\n            lines.append(\n                f"- `{error['query_id']}` / `{error['source']}`: {error['error']}"\n            )\n        lines.append("")\n'''
if old_report in discovery:
    discovery = discovery.replace(old_report, new_report, 1)
elif new_report not in discovery:
    raise SystemExit("discover report marker not found")

old_parser = '    parser.add_argument("--self-test", action="store_true")\n'
new_parser = '''    parser.add_argument(\n        "--require-source",\n        action="append",\n        default=[],\n        choices=("arxiv", "crossref"),\n        help="Fail unless at least one query from this source succeeds; repeatable.",\n    )\n    parser.add_argument("--self-test", action="store_true")\n'''
if old_parser in discovery:
    discovery = discovery.replace(old_parser, new_parser, 1)
elif new_parser not in discovery:
    raise SystemExit("discover parser marker not found")

old_loop = '''    discovered: list[dict] = []\n    for query in config.get("queries", []):\n        source = query.get("source")\n        if source == "arxiv":\n            discovered.extend(query_arxiv(config, query, args.max_results))\n            time.sleep(float(config["sources"]["arxiv"].get("polite_delay_seconds", 3)))\n        elif source == "crossref":\n            discovered.extend(query_crossref(config, query, min(args.max_results, 20)))\n        else:\n            raise ValueError(f"unsupported discovery source: {source!r}")\n\n    candidates = filter_candidates(discovered, accepted, min_year=args.min_year)\n    payload = {\n        "schema_version": "1.0",\n        "scan_timestamp": datetime.now(UTC).isoformat(),\n        "query_count": len(config.get("queries", [])),\n        "min_year": args.min_year,\n        "candidate_count": len(candidates),\n        "candidates": candidates,\n    }\n'''
new_loop = '''    discovered: list[dict] = []\n    query_errors: list[dict[str, str]] = []\n    successful_queries: list[str] = []\n    successful_sources: set[str] = set()\n    for query in config.get("queries", []):\n        source = str(query.get("source"))\n        try:\n            if source == "arxiv":\n                discovered.extend(query_arxiv(config, query, args.max_results))\n                time.sleep(\n                    float(config["sources"]["arxiv"].get("polite_delay_seconds", 3))\n                )\n            elif source == "crossref":\n                discovered.extend(\n                    query_crossref(config, query, min(args.max_results, 20))\n                )\n            else:\n                raise ValueError(f"unsupported discovery source: {source!r}")\n        except Exception as exc:  # public API boundary; retain partial scan\n            query_errors.append(\n                {\n                    "query_id": str(query.get("id")),\n                    "source": source,\n                    "error": clean_text(str(exc))[:500],\n                }\n            )\n            continue\n        successful_queries.append(str(query.get("id")))\n        successful_sources.add(source)\n\n    missing_required = sorted(set(args.require_source) - successful_sources)\n    if missing_required:\n        details = "; ".join(\n            f"{item['query_id']}: {item['error']}"\n            for item in query_errors\n            if item["source"] in missing_required\n        )\n        raise RuntimeError(\n            f"required discovery source(s) had no successful query: {missing_required}; {details}"\n        )\n    if not successful_queries:\n        raise RuntimeError("all configured discovery queries failed")\n\n    candidates = filter_candidates(discovered, accepted, min_year=args.min_year)\n    payload = {\n        "schema_version": "1.0",\n        "scan_timestamp": datetime.now(UTC).isoformat(),\n        "query_count": len(config.get("queries", [])),\n        "successful_query_count": len(successful_queries),\n        "successful_queries": successful_queries,\n        "successful_sources": sorted(successful_sources),\n        "query_errors": query_errors,\n        "min_year": args.min_year,\n        "candidate_count": len(candidates),\n        "candidates": candidates,\n    }\n'''
if old_loop in discovery:
    discovery = discovery.replace(old_loop, new_loop, 1)
elif new_loop not in discovery:
    raise SystemExit("discover main-loop marker not found")

discovery_path.write_text(discovery, encoding="utf-8")
print("Final Awesome review fixes prepared.")
