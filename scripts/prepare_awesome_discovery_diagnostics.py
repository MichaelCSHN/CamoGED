#!/usr/bin/env python3
"""Ensure live-discovery failures still emit auditable artifacts."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/discover_awesome.py"
text = path.read_text(encoding="utf-8")
old = '''    missing_required = sorted(set(args.require_source) - successful_sources)\n    if missing_required:\n        details = "; ".join(\n            f"{item['query_id']}: {item['error']}"\n            for item in query_errors\n            if item["source"] in missing_required\n        )\n        raise RuntimeError(\n            f"required discovery source(s) had no successful query: {missing_required}; {details}"\n        )\n    if not successful_queries:\n        raise RuntimeError("all configured discovery queries failed")\n\n    candidates = filter_candidates(discovered, accepted, min_year=args.min_year)\n    payload = {\n'''
new = '''    fatal_errors: list[str] = []\n    missing_required = sorted(set(args.require_source) - successful_sources)\n    if missing_required:\n        details = "; ".join(\n            f"{item['query_id']}: {item['error']}"\n            for item in query_errors\n            if item["source"] in missing_required\n        )\n        fatal_errors.append(\n            f"required discovery source(s) had no successful query: {missing_required}; {details}"\n        )\n    if not successful_queries:\n        fatal_errors.append("all configured discovery queries failed")\n\n    candidates = filter_candidates(discovered, accepted, min_year=args.min_year)\n    payload = {\n'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("fatal discovery block marker not found")
old_payload = '''        "query_errors": query_errors,\n        "min_year": args.min_year,\n'''
new_payload = '''        "query_errors": query_errors,\n        "fatal_errors": fatal_errors,\n        "min_year": args.min_year,\n'''
if old_payload in text:
    text = text.replace(old_payload, new_payload, 1)
elif new_payload not in text:
    raise SystemExit("discovery payload marker not found")
old_tail = '''    Path(args.output_markdown).write_text(markdown_report(payload), encoding="utf-8")\n    print(f"discover_awesome: {len(candidates)} new candidate(s)")\n    return 0\n'''
new_tail = '''    Path(args.output_markdown).write_text(markdown_report(payload), encoding="utf-8")\n    for error in fatal_errors:\n        print(f"ERROR {error}")\n    print(\n        f"discover_awesome: {len(candidates)} new candidate(s); "\n        f"successful_queries={len(successful_queries)}; query_errors={len(query_errors)}"\n    )\n    return 1 if fatal_errors else 0\n'''
if old_tail in text:
    text = text.replace(old_tail, new_tail, 1)
elif new_tail not in text:
    raise SystemExit("discovery return marker not found")
path.write_text(text, encoding="utf-8")
print("Awesome discovery diagnostics prepared.")
