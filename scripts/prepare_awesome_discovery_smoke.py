#!/usr/bin/env python3
"""Bound PR discovery smoke time while preserving full scheduled scans."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/discover_awesome.py"
text = path.read_text(encoding="utf-8")

replacements = {
    "def request_text(url: str, *, attempts: int = 3) -> str:":
        "def request_text(url: str, *, attempts: int = 2) -> str:",
    "with urllib.request.urlopen(request, timeout=45) as response:":
        "with urllib.request.urlopen(request, timeout=20) as response:",
    '''    parser.add_argument(\n        "--require-source",\n        action="append",\n        default=[],\n        choices=("arxiv", "crossref"),\n        help="Fail unless at least one query from this source succeeds; repeatable.",\n    )\n''':
        '''    parser.add_argument(\n        "--require-source",\n        action="append",\n        default=[],\n        choices=("arxiv", "crossref"),\n        help="Fail unless at least one query from this source succeeds; repeatable.",\n    )\n    parser.add_argument(\n        "--query-id",\n        action="append",\n        default=[],\n        help="Run only the named configured query; repeatable. Default: all queries.",\n    )\n''',
    '''    discovered: list[dict] = []\n    query_errors: list[dict[str, str]] = []\n    successful_queries: list[str] = []\n    successful_sources: set[str] = set()\n    for query in config.get("queries", []):\n''':
        '''    configured_queries = config.get("queries", [])\n    if args.query_id:\n        requested = set(args.query_id)\n        queries = [query for query in configured_queries if query.get("id") in requested]\n        missing = sorted(requested - {str(query.get("id")) for query in queries})\n        if missing:\n            raise ValueError(f"unknown discovery query id(s): {missing}")\n    else:\n        queries = configured_queries\n\n    discovered: list[dict] = []\n    query_errors: list[dict[str, str]] = []\n    successful_queries: list[str] = []\n    successful_sources: set[str] = set()\n    for query in queries:\n''',
    '"query_count": len(config.get("queries", [])),': '"query_count": len(queries),',
}
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"discovery smoke patch marker not found: {old[:80]!r}")
path.write_text(text, encoding="utf-8")
print("Awesome discovery smoke limits prepared.")
