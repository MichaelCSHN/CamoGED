#!/usr/bin/env python3
"""Discover Awesome candidates without modifying accepted metadata.

The scanner queries configured public APIs, normalizes identifiers, removes
records already present in ``data/papers.yaml``, and writes a JSON/Markdown
triage report.  Acceptance is a separate human-triggered workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
USER_AGENT = "CamoGED-Awesome-Discovery/0.1 (+https://github.com/MichaelCSHN/CamoGED)"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)
DOI_RE = re.compile(r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/\S+)", re.I)


def load_yaml(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def extract_external_id(url: str | None) -> tuple[str, str] | None:
    if not url:
        return None
    arxiv = ARXIV_RE.search(url)
    if arxiv:
        return ("arxiv", arxiv.group(1))
    doi = DOI_RE.search(url)
    if doi:
        return ("doi", doi.group(1).rstrip(".,)").lower())
    return None


def candidate_id(source: str, external_id: str | None, title: str) -> str:
    raw = f"{source}:{external_id or normalize_title(title)}"
    digest = hashlib.sha1(raw.encode("utf-8"), usedforsecurity=False).hexdigest()[:10]
    return f"{source}-{digest}"


def request_text(url: str, *, attempts: int = 3) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read().decode("utf-8")
        except Exception as exc:  # network boundary
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"failed to retrieve {url}: {last_error}")


def parse_arxiv(xml_text: str, query_id: str, tags: list[str]) -> list[dict]:
    root = ET.fromstring(xml_text)
    candidates: list[dict] = []
    for entry in root.findall("a:entry", ATOM):
        title = clean_text(entry.findtext("a:title", default="", namespaces=ATOM))
        abstract = clean_text(entry.findtext("a:summary", default="", namespaces=ATOM))
        url = clean_text(entry.findtext("a:id", default="", namespaces=ATOM))
        arxiv_match = ARXIV_RE.search(url)
        arxiv_id = arxiv_match.group(1) if arxiv_match else None
        published = clean_text(
            entry.findtext("a:published", default="", namespaces=ATOM)
        )
        updated = clean_text(entry.findtext("a:updated", default="", namespaces=ATOM))
        authors = [
            clean_text(author.findtext("a:name", default="", namespaces=ATOM))
            for author in entry.findall("a:author", ATOM)
        ]
        doi = None
        for child in entry:
            if child.tag.endswith("doi") and child.text:
                doi = clean_text(child.text)
                break
        year = int(published[:4]) if published[:4].isdigit() else None
        candidates.append(
            {
                "candidate_id": candidate_id("arxiv", arxiv_id, title),
                "source": "arxiv",
                "external_id": arxiv_id,
                "arxiv_id": arxiv_id,
                "doi": doi,
                "title": title,
                "authors": authors,
                "venue": "arXiv",
                "year": year,
                "paper": url,
                "abstract": abstract,
                "publication_status": "preprint",
                "discovered_by": [query_id],
                "suggested_tags": tags,
                "published": published,
                "updated": updated,
            }
        )
    return candidates


def parse_crossref(json_text: str, query_id: str, tags: list[str]) -> list[dict]:
    payload = json.loads(json_text)
    items = payload.get("message", {}).get("items", [])
    candidates: list[dict] = []
    for item in items:
        title_values = item.get("title") or []
        if not title_values:
            continue
        title = clean_text(title_values[0])
        doi = clean_text(item.get("DOI")) or None
        url = f"https://doi.org/{doi}" if doi else clean_text(item.get("URL"))
        authors = [
            clean_text(
                " ".join(filter(None, [author.get("given"), author.get("family")]))
            )
            for author in item.get("author") or []
        ]
        date_parts = (
            item.get("published-print", {}).get("date-parts")
            or item.get("published-online", {}).get("date-parts")
            or item.get("issued", {}).get("date-parts")
            or []
        )
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        venue_values = item.get("container-title") or []
        venue = (
            clean_text(venue_values[0])
            if venue_values
            else clean_text(item.get("publisher"))
        )
        candidates.append(
            {
                "candidate_id": candidate_id("crossref", doi, title),
                "source": "crossref",
                "external_id": doi,
                "arxiv_id": None,
                "doi": doi,
                "title": title,
                "authors": authors,
                "venue": venue or "Crossref record",
                "year": year,
                "paper": url,
                "abstract": clean_text(item.get("abstract")),
                "publication_status": "published",
                "discovered_by": [query_id],
                "suggested_tags": tags,
                "published": None,
                "updated": item.get("indexed", {}).get("date-time"),
            }
        )
    return candidates


def query_arxiv(config: dict, query: dict, max_results: int) -> list[dict]:
    endpoint = config["sources"]["arxiv"]["endpoint"]
    parameters = urllib.parse.urlencode(
        {
            "search_query": query["query"],
            "start": 0,
            "max_results": max_results,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        }
    )
    return parse_arxiv(
        request_text(f"{endpoint}?{parameters}"), query["id"], query.get("tags", [])
    )


def query_crossref(config: dict, query: dict, max_results: int) -> list[dict]:
    endpoint = config["sources"]["crossref"]["endpoint"]
    parameters = urllib.parse.urlencode(
        {
            "query.bibliographic": query["query"],
            "rows": max_results,
            "sort": "published",
            "order": "desc",
            "select": "DOI,title,author,container-title,publisher,published-print,published-online,issued,indexed,URL,type",
        }
    )
    return parse_crossref(
        request_text(f"{endpoint}?{parameters}"), query["id"], query.get("tags", [])
    )


def existing_keys(records: Iterable[dict]) -> tuple[set[str], set[tuple[str, str]]]:
    titles: set[str] = set()
    identifiers: set[tuple[str, str]] = set()
    for item in records:
        titles.add(normalize_title(str(item.get("title", ""))))
        for url in (item.get("canonical_url"), item.get("paper")):
            external = extract_external_id(url)
            if external:
                identifiers.add(external)
    return titles, identifiers


def merge_candidates(candidates: Iterable[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for item in candidates:
        key = normalize_title(item["title"])
        current = merged.get(key)
        if current is None:
            merged[key] = item
            continue
        current["discovered_by"] = sorted(
            set(current["discovered_by"] + item["discovered_by"])
        )
        current["suggested_tags"] = sorted(
            set(current["suggested_tags"] + item["suggested_tags"])
        )
        if not current.get("doi") and item.get("doi"):
            current["doi"] = item["doi"]
            current["paper"] = item["paper"]
            current["publication_status"] = "published"
            current["venue"] = item["venue"]
    return list(merged.values())


def filter_candidates(
    candidates: Iterable[dict], accepted: list[dict], *, min_year: int
) -> list[dict]:
    titles, identifiers = existing_keys(accepted)
    output: list[dict] = []
    for item in merge_candidates(candidates):
        if item.get("year") and int(item["year"]) < min_year:
            continue
        if normalize_title(item["title"]) in titles:
            continue
        external = ("doi", item["doi"].lower()) if item.get("doi") else None
        if external and external in identifiers:
            continue
        arxiv = ("arxiv", item["arxiv_id"]) if item.get("arxiv_id") else None
        if arxiv and arxiv in identifiers:
            continue
        output.append(item)
    return sorted(
        output,
        key=lambda value: (int(value.get("year") or 0), value.get("updated") or ""),
        reverse=True,
    )


def markdown_report(payload: dict) -> str:
    lines = [
        f"# Awesome candidate triage — {payload['scan_timestamp'][:10]}",
        "",
        f"- Query count: **{payload['query_count']}**",
        f"- New candidates after deduplication: **{len(payload['candidates'])}**",
        f"- Minimum publication year: **{payload['min_year']}**",
        "- Policy: automated discovery only; human review is required before acceptance.",
        "",
    ]
    for item in payload["candidates"]:
        lines.extend(
            [
                f"## {item['candidate_id']} — {item['title']}",
                "",
                f"- Source: `{item['source']}` / `{item.get('external_id') or 'none'}`",
                f"- Year / venue: {item.get('year') or 'unknown'} / {item.get('venue') or 'unknown'}",
                f"- Suggested tags: {', '.join(item.get('suggested_tags') or [])}",
                f"- Discovered by: {', '.join(item.get('discovered_by') or [])}",
                f"- Paper: {item.get('paper') or ''}",
                f"- Abstract: {item.get('abstract') or 'not supplied'}",
                "",
            ]
        )
    lines.extend(
        [
            "<!-- CAMOGED_CANDIDATES_JSON_BEGIN -->",
            "```json",
            json.dumps(payload["candidates"], ensure_ascii=False, indent=2),
            "```",
            "<!-- CAMOGED_CANDIDATES_JSON_END -->",
            "",
        ]
    )
    return "\n".join(lines)


def self_test() -> None:
    atom = """<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'>
    <entry><id>https://arxiv.org/abs/2601.12345</id><updated>2026-01-03T00:00:00Z</updated>
    <published>2026-01-02T00:00:00Z</published><title> Test Camouflage Paper </title>
    <summary> A candidate. </summary><author><name>A. Author</name></author></entry></feed>"""
    items = parse_arxiv(atom, "test", ["image-cod"])
    assert items[0]["arxiv_id"] == "2601.12345"
    assert normalize_title(items[0]["title"]) == "testcamouflagepaper"
    accepted = [{"title": "Other", "canonical_url": "https://arxiv.org/abs/2501.00001"}]
    assert len(filter_candidates(items, accepted, min_year=2025)) == 1
    print("discover_awesome self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", default="awesome_candidates.json")
    parser.add_argument("--output-markdown", default="awesome_candidates.md")
    parser.add_argument("--max-results", type=int, default=15)
    parser.add_argument("--min-year", type=int, default=datetime.now(UTC).year - 2)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    config = load_yaml("discovery_queries.yaml")
    accepted = load_yaml("papers.yaml").get("papers", [])
    discovered: list[dict] = []
    for query in config.get("queries", []):
        source = query.get("source")
        if source == "arxiv":
            discovered.extend(query_arxiv(config, query, args.max_results))
            time.sleep(float(config["sources"]["arxiv"].get("polite_delay_seconds", 3)))
        elif source == "crossref":
            discovered.extend(query_crossref(config, query, min(args.max_results, 20)))
        else:
            raise ValueError(f"unsupported discovery source: {source!r}")

    candidates = filter_candidates(discovered, accepted, min_year=args.min_year)
    payload = {
        "schema_version": "1.0",
        "scan_timestamp": datetime.now(UTC).isoformat(),
        "query_count": len(config.get("queries", [])),
        "min_year": args.min_year,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    Path(args.output_json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    Path(args.output_markdown).write_text(markdown_report(payload), encoding="utf-8")
    print(f"discover_awesome: {len(candidates)} new candidate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
