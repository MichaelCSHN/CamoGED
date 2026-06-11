# AGENTS.md — Instructions for AI coding agents (Codex) in this repo

> **Division of labor (updated 2026-06, supersedes the original split).** This repo is
> now developed by two agents under the maintainer's identity:
> - **Claude (project lead)** — owns and develops the evaluation toolkit `camo-eval/`,
>   its demo surfaces (`web/hf-space/`, `camo-eval/notebooks/`), and the API gate
>   `scripts/check_api.py`. Also acts as overall coordinator and auditor.
> - **Codex (you)** — author the **monograph** (`book/`: chapters, `references.bib`,
>   figures, proofreading) **and** own the **Awesome list + data pipeline**
>   (`awesome/`, `data/`, `scripts/build_awesome.py`, `scripts/check_data.py`) and the
>   data-driven website pages.
>
> Your current, concrete assignment lives in
> [`docs/CODEX_DIRECTIVE.md`](docs/CODEX_DIRECTIVE.md) — read it first.
>
> This file is the authoritative behavioral boundary. Because you commit as the
> maintainer, GitHub access control cannot separate your work from Claude's or the
> maintainer's — so these rules + the CI gates + the maintainer's diff review are
> what keep the boundary. Follow them strictly.

---

## 1. Your scope

**You MAY create/modify files in:**
- `book/` — the monograph: chapters `*.qmd`, `references.bib`, `figures/`. **You are now the
  author**: expand chapters to publication level, manage citations, generate figures, proofread.
- `awesome/` — the Awesome list (generated output)
- `data/` — the YAML single source of truth
- `scripts/build_awesome.py`, `scripts/check_data.py` — the awesome/data generators & validators
- `web/` — the data-driven website pages (papers/datasets/leaderboard/models), **except**
  `web/hf-space/` (Claude's camo-eval demo)
- `.github/workflows/` — only CI related to the above (book render, link-check, check_data)
- tests under `data/` and the awesome pipeline

**You MUST NOT modify (owned by Claude, the project lead):**
- `camo-eval/` — the evaluation toolkit (Python package), its tests, and `camo-eval/notebooks/`
- `scripts/check_api.py` — the camo-eval API gate
- `web/hf-space/` — the camo-eval Hugging Face Space demo
- root `README.md`, `LICENSE`, `LICENSE-CONTENT`, `CITATION.cff` — unless the maintainer explicitly asks
- `AGENTS.md`, `docs/CONTRIBUTOR_WORK_PACKAGES.md`, `docs/CODEX_DIRECTIVE.md` — coordination docs maintained by the lead

If a task appears to require editing anything under `camo-eval/`, `scripts/check_api.py`,
`web/hf-space/`, or `camo-eval/notebooks/`, **STOP**. Do not edit it. Append a short entry to
`NOTES_FOR_MAINTAINER.md` describing exactly what change you need and why (e.g. a camo-eval bug,
or a new metric you want surfaced in the leaderboard), and continue with the parts you own.

---

## 2. Frozen interface contracts (do NOT change without explicit maintainer approval)

These are the coupling points between your work (book + data + awesome) and Claude's
`camo-eval`. Treat them as APIs.

1. **Data schema** — follow [`data/SCHEMA.md`](data/SCHEMA.md) **exactly**. Do not rename,
   add, or remove fields or controlled-vocabulary values. Aligning the existing YAML to the
   schema (task B1, see §8 of SCHEMA.md) is allowed and expected.
2. **`camo-eval` public API** — the names/signatures in §6 below are the contract you **consume**
   when reporting metric values (leaderboard, website, Chapter 15 / Appendix B). **Claude owns
   and evolves the implementation; you do not implement or change camo-eval.** Keep the book's
   metric definitions (Ch.15 + Appendix B) consistent with this API; if the API needs to change,
   coordinate via `NOTES_FOR_MAINTAINER.md`.
3. **`bibtex_key` namespace** — `data/*.yaml` `bibtex_key` values must match the keys in
   `book/references.bib`. **You now own both sides** (book + data), so add the key to
   `references.bib` and align `data/*.yaml` in the same change. Keep the namespace coherent.

---

## 3. Hard rules

- **NO FABRICATION.** Never invent or estimate any of: leaderboard numbers, metric values,
  dataset sizes/splits, citations, URLs, or DOIs. Unknown → `null`. In `data/leaderboard.yaml`,
  any non-null metric requires `verified: true` **and** a resolvable `source`. If you cannot
  verify a number against its source, leave it `null` and note it. This rule is absolute — it
  applies equally to facts, dates, and citations in the **monograph**.
- **Determinism.** Same input → same output: `scripts/build_awesome.py` must regenerate
  `awesome/README.md` byte-for-byte.
- **Don't add dependencies casually.** Justify each new dependency in the commit message.

---

## 4. Definition of done (self-check before reporting a task complete)

Run and pass the gates **for the area you touched**; do not claim completion otherwise.

For **data / awesome** changes:

```bash
python scripts/check_data.py           # data schema + no-fabrication + consistency
python scripts/build_awesome.py        # regenerate; then `git diff --exit-code awesome/README.md`
# link-check workflow green (all URLs resolve)
```

For **book** changes:

```bash
quarto render                          # the book builds without errors
# citations resolve; figures generate; no broken cross-references
```

And confirm: **you did not modify anything Claude owns** —
`git diff --name-only | grep -E '^(camo-eval/|scripts/check_api\.py|web/hf-space/)'` must be empty.

---

## 5. Where to read before starting

- [`docs/CODEX_DIRECTIVE.md`](docs/CODEX_DIRECTIVE.md) — **your current assignment** (start here).
- [`docs/CONTRIBUTOR_WORK_PACKAGES.md`](docs/CONTRIBUTOR_WORK_PACKAGES.md) — work packages,
  task breakdown, milestones, and audit requirements.
- [`data/SCHEMA.md`](data/SCHEMA.md) — the data contract.
- §6 below — the camo-eval API you **consume** when reporting metric values (Claude implements it).

---

## 6. `camo-eval` public API (authoritative — consume these names; Claude implements)

```python
# camo_eval/metrics/detection.py
mae(pred, gt) -> float
weighted_f_measure(pred, gt, beta2: float = 1.0) -> float          # Margolin 2014
s_measure(pred, gt, alpha: float = 0.5) -> float                   # Fan 2017 (ICCV)
e_measure(pred, gt) -> dict     # {"adaptive":…, "mean":…, "max":…} # Fan 2018 (IJCAI)
f_measure(pred, gt) -> dict     # {"max":…, "mean":…, "adaptive":…}

# camo_eval/metrics/generation.py   (optional extra: camo-eval[generation])
fid(real_dir, fake_dir) -> float
lpips(img_a, img_b) -> float
deception_rate(detector, images, targets) -> float    # detector is a pluggable callable

# camo_eval/metrics/robustness.py
attack_success_rate(clean_outputs, attacked_outputs, criterion) -> float
ap_drop(clean_ap: float, attacked_ap: float) -> float
transferability(asr_by_model: dict) -> dict

# camo_eval/runner.py
evaluate(pred_dir, gt_dir, metrics: list[str]) -> "ResultsTable"

# camo_eval/export.py
to_latex(results: "ResultsTable") -> str
to_markdown(results: "ResultsTable") -> str
```

**Input/return contract:** `pred`, `gt` are same-size `numpy.ndarray` (HxW); `pred` accepts
`[0,1]` float or `uint8 [0,255]` (normalize internally); `gt` is binary (>0 = foreground).
Define and test behavior for empty/all-foreground/single-pixel/NaN inputs. `evaluate` matches
files by basename across the two dirs. Metric dict keys must match those in `data/SCHEMA.md` §4
and Chapter 15.

`scripts/check_api.py` must compare the actual public signatures to this list and fail on any
mismatch — this is how the contract stays frozen.

---

## 7. Commit hygiene

- One logical task per commit/PR; reference the work-package task id (e.g. `WP-A/A1`).
- Conventional-commit style messages (`feat(camo-eval): …`, `data: …`, `chore(ci): …`).
- Never commit large binaries, datasets, or model weights (data is **linked, not redistributed**).
