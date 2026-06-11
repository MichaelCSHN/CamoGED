# Contributing to CamoGED

Thanks for helping build the most comprehensive open resource on camouflage! 🦎

CamoGED has a **single source of truth** for resources: the YAML files in [`data/`](data/).
Both the [Awesome list](awesome/README.md) and the [website](web/) are generated from them, so
**add a resource once in `data/` and it shows up everywhere**.

## Ways to contribute

- **Add a paper / method** → use the *Add a paper* issue template, or edit `data/papers.yaml`.
- **Add a dataset** → use the *Add a dataset* issue template, or edit `data/datasets.yaml`.
- **Add a leaderboard entry** → edit `data/leaderboard.yaml` (see rules below).
- **Write / correct the book** → edit the relevant `book/chapters/*.qmd`.
- **Improve camo-eval** → add metrics under `camo-eval/src/camo_eval/metrics/` with tests.

## Resource entry format

Each `papers.yaml` entry:

```yaml
- title: "ZoomNeXt: A Unified Collaborative Pyramid Network for Camouflaged Object Detection"
  authors: "Pang et al."
  venue: "TPAMI"
  year: 2024
  task: "image-cod"        # image-cod | video-cod | instance | referring | collaborative | generation | adversarial | ...
  domain: "intelligent"    # physical | digital | intelligent
  pillar: "detection"      # generation | detection | evaluation
  code: "https://github.com/..."   # or null
  paper: "https://arxiv.org/abs/..."
  dataset: ["COD10K", "CAMO", "NC4K"]
```

## Leaderboard rules (credibility first)

- Every number must cite its **source** (`paper` or `repo`) and the **training protocol**.
- Mark whether a result is `reported` (from the original paper) or `reproduced` (by us).
- Do **not** invent or estimate numbers. Leave blank if unverified.

```yaml
- method: "ZoomNeXt"
  dataset: "COD10K"
  task: "image-cod"
  metrics: { Sm: null, Fw: null, Em: null, MAE: null }  # fill from source
  params_M: null
  source: "https://..."
  status: "reported"   # reported | reproduced
```

## Pull request checklist

- [ ] Edited `data/*.yaml` rather than the generated Markdown where applicable
- [ ] Links are valid (CI checks this)
- [ ] For code: added/updated tests; `pytest` passes
- [ ] Respect the dual-use policy in [`ETHICS.md`](ETHICS.md)

## Style

- Prose: clear, sourced, no hype. Prefer paraphrase over long quotes.
- Code: Python ≥3.9, type hints, `ruff`/`black` formatting.

By contributing you agree your contributions are licensed under Apache-2.0 (code)
or CC-BY-4.0 (content), matching the repository.
