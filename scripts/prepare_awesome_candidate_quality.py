#!/usr/bin/env python3
"""Add quality filters for noisy Crossref discovery records."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts/discover_awesome.py"
text = path.read_text(encoding="utf-8")

old_constants = '''DOI_RE = re.compile(r"(?:doi\\.org/|doi:\\s*)(10\\.\\d{4,9}/\\S+)", re.I)\n'''
new_constants = '''DOI_RE = re.compile(r"(?:doi\\.org/|doi:\\s*)(10\\.\\d{4,9}/\\S+)", re.I)\nCAMOUFLAGE_TERMS = {\n    "camouflage",\n    "camouflaged",\n    "concealed",\n    "concealment",\n    "crypsis",\n    "mimicry",\n    "countershading",\n    "disruptive coloration",\n    "detectability",\n    "visual ecology",\n    "adaptive coloration",\n}\nPLACEHOLDER_TITLES = {"titlepending", "untitled", "titleforthcoming"}\n'''
if old_constants in text:
    text = text.replace(old_constants, new_constants, 1)
elif new_constants not in text:
    raise SystemExit("discovery constants marker not found")

old_filter = '''    for item in merge_candidates(candidates):\n        if item.get("year") and int(item["year"]) < min_year:\n            continue\n        if normalize_title(item["title"]) in titles:\n            continue\n'''
new_filter = '''    current_year = datetime.now(UTC).year\n    for item in merge_candidates(candidates):\n        year = int(item.get("year") or 0)\n        normalized_title = normalize_title(item["title"])\n        if year and year < min_year:\n            continue\n        if year > current_year + 1:\n            continue\n        if any(normalized_title.startswith(value) for value in PLACEHOLDER_TITLES):\n            continue\n        if item.get("source") == "crossref":\n            haystack = f"{item.get('title', '')} {item.get('abstract', '')}".lower()\n            if not any(term in haystack for term in CAMOUFLAGE_TERMS):\n                continue\n        if normalized_title in titles:\n            continue\n'''
if old_filter in text:
    text = text.replace(old_filter, new_filter, 1)
elif new_filter not in text:
    raise SystemExit("candidate filter marker not found")

old_test = '''    accepted = [{"title": "Other", "canonical_url": "https://arxiv.org/abs/2501.00001"}]\n    assert len(filter_candidates(items, accepted, min_year=2025)) == 1\n    print("discover_awesome self-test: ok")\n'''
new_test = '''    accepted = [{"title": "Other", "canonical_url": "https://arxiv.org/abs/2501.00001"}]\n    assert len(filter_candidates(items, accepted, min_year=2025)) == 1\n    noisy = [\n        {\n            "title": "Title Pending 2223",\n            "year": 2036,\n            "source": "crossref",\n            "abstract": "",\n            "doi": "10.1/noise",\n            "arxiv_id": None,\n            "updated": "",\n            "discovered_by": ["biology"],\n            "suggested_tags": ["biological-camouflage"],\n        }\n    ]\n    assert filter_candidates(noisy, accepted, min_year=2025) == []\n    print("discover_awesome self-test: ok")\n'''
if old_test in text:
    text = text.replace(old_test, new_test, 1)
elif new_test not in text:
    raise SystemExit("candidate-quality self-test marker not found")

path.write_text(text, encoding="utf-8")
print("Awesome candidate quality filters prepared.")
