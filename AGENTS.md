# AGENTS.md — Instructions for AI coding agents (Codex) in this repo

> You are a coding agent working on **CamoGED** on the maintainer's local machine,
> committing under the maintainer's identity. You implement and maintain **code,
> data, and the Awesome list**. You do **not** write the monograph.
>
> This file is the authoritative behavioral boundary. Because you commit as the
> maintainer, GitHub access control cannot separate your work from the
> maintainer's — so these rules + the CI gates + the maintainer's diff review are
> what keep the boundary. Follow them strictly.

---

## 1. Your scope

**You MAY create/modify files in:**
- `camo-eval/` — the evaluation toolkit (Python package)
- `awesome/` — the Awesome list (generated output)
- `data/` — the YAML single source of truth
- `scripts/` — generators and validators
- `web/` — the website (later phase)
- `.github/workflows/` — only CI related to the above
- tests under any of the above

**You MUST NOT modify:**
- `book/` — the monograph: chapters `*.qmd`, `references.bib`, `figures/`. Authored separately.
- `docs/`, root `README.md`, `LICENSE`, `LICENSE-CONTENT`, `CITATION.cff` — unless the maintainer explicitly asks.

If a task appears to require editing `book/`, **STOP**. Do not edit it. Instead append a
short entry to `NOTES_FOR_MAINTAINER.md` (create it if absent) describing exactly what
change is needed and why, and continue with the parts you are allowed to do.

---

## 2. Frozen interface contracts (do NOT change without explicit maintainer approval)

These are the only coupling points between your code and the monograph. Treat them as APIs.

1. **Data schema** — follow [`data/SCHEMA.md`](data/SCHEMA.md) **exactly**. Do not rename,
   add, or remove fields or controlled-vocabulary values. Aligning the existing YAML to the
   schema (task B1, see §8 of SCHEMA.md) is allowed and expected.
2. **`camo-eval` public API** — the names and signatures in §6 below are fixed by the book
   (Chapter 15 + Appendix B). Implement to these exact names. Do not rename public functions.
3. **`bibtex_key` namespace** — `data/*.yaml` `bibtex_key` values should match the keys in
   `book/references.bib`. You do **not** edit `references.bib`. If you need a key that is not
   there, record it in `NOTES_FOR_MAINTAINER.md`; the maintainer adds it.

To propose any change to the three contracts: write it in `NOTES_FOR_MAINTAINER.md` and stop;
do not implement the change yourself.

---

## 3. Hard rules

- **NO FABRICATION.** Never invent or estimate any of: leaderboard numbers, metric values,
  dataset sizes/splits, citations, URLs, or DOIs. Unknown → `null`. In `data/leaderboard.yaml`,
  any non-null metric requires `verified: true` **and** a resolvable `source`. If you cannot
  verify a number against its source, leave it `null` and note it. This rule is absolute.
- **Determinism.** Same input → same output. Seed any randomness (e.g. FID feature sampling).
- **Keep the core light.** Core detection metrics (`mae`, `s_measure`, `e_measure`,
  `weighted_f_measure`) must work **without** torch. Put FID/LPIPS behind an optional extra
  (`pip install camo-eval[generation]`).
- **Numerical correctness is paramount.** Validate metrics against a reference implementation
  (e.g. `PySODMetrics`, `pip install pysodmetrics`) to tolerance `1e-4` and freeze the
  comparison in `tests/`.
- **Don't add dependencies casually.** Justify each new dependency in the PR/commit message.

---

## 4. Definition of done (self-check before reporting a task complete)

Run and pass all of these; do not claim completion otherwise:

```bash
pytest -q                              # all green; coverage >= 85% for camo-eval
python scripts/check_data.py           # data schema + no-fabrication + consistency
python scripts/check_api.py            # camo-eval signatures match Appendix B (see §6)
ruff check . && black --check .        # style
python scripts/build_awesome.py        # regenerate; then `git diff --exit-code awesome/README.md`
```

And confirm: **you did not modify anything under `book/`** (`git diff --name-only | grep '^book/'`
must be empty).

---

## 5. Where to read before starting

- [`docs/CONTRIBUTOR_WORK_PACKAGES.md`](docs/CONTRIBUTOR_WORK_PACKAGES.md) — your work packages,
  task breakdown, milestones, and audit requirements. (Where it says "collaborator", that is you,
  Codex; where it describes PR review by "both owners", read it as: CI gates + the maintainer's
  review, since you commit as the maintainer.)
- [`data/SCHEMA.md`](data/SCHEMA.md) — the data contract.
- §6 below — the camo-eval API you must implement.

---

## 6. `camo-eval` public API (authoritative — implement to these names)

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
