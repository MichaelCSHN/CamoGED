# NOTES FOR MAINTAINER

> **Purpose.** This is the one-way channel from the coding agent (Codex) to the
> maintainer. Whenever the agent hits something it **must not do itself** — per
> `AGENTS.md` — it appends an entry here instead of acting, and keeps working on
> the parts it *is* allowed to do.
>
> The agent writes entries. **Only the maintainer edits `status` and
> `maintainer note`, and performs the actual change** (in `book/`,
> `references.bib`, `data/SCHEMA.md`, or Appendix B).

---

## When to add an entry (agent)

Add an entry when a task would otherwise require you to:

- **`bibtex-key`** — cite a paper whose key is not in `book/references.bib`
  (you may use the key in `data/*.yaml`, but you cannot add it to `references.bib`).
- **`book-edit`** — change anything under `book/` (chapters, figures, references).
- **`interface-change`** — change a frozen contract: a `data/SCHEMA.md` field or
  controlled-vocabulary value, or a `camo-eval` public API name/signature
  (Appendix B / `AGENTS.md` §6).
- **`verification`** — a number/fact you could not verify against its source
  (you left it `null` per the no-fabrication rule) and a human should check.
- **`blocker` / `question`** — anything ambiguous or blocking that needs a decision.

Do **not** implement any of the above yourself. Append an entry, then continue.

---

## Entry format

Copy this block, fill it, append under **Entries** (newest at the bottom). Use a
running id: `N-001`, `N-002`, …

```
## N-XXX <short title>
- date: YYYY-MM-DD
- author: codex
- category: bibtex-key | book-edit | interface-change | verification | blocker | question
- status: open                 # maintainer sets: open | acknowledged | resolved
- where: <file / task that triggered this, e.g. data/papers.yaml, WP-A/A1>
- what: <what is needed, concretely>
- why: <why the agent must not do it itself>
- proposed: <a concrete proposal: exact bibtex entry / field / signature / value>
- maintainer note: <blank; maintainer fills on resolution>
```

---

## Examples (reference — not live items)

```
## EX-1 add bibtex key for "SegMaR"
- date: 2026-06-11
- author: codex
- category: bibtex-key
- where: data/papers.yaml (WP-B/B2)
- status: resolved (example)
- what: references.bib needs a key `jia2022segmar` so data/ and the book share one identity.
- why: references.bib is author-owned; agent does not edit book/.
- proposed: |
    @inproceedings{jia2022segmar,
      title     = {Segment, Magnify and Reiterate: Detecting Camouflaged Objects the Hard Way},
      author    = {Jia, Qi and Yao, Shuilian and Liu, Yu and Fan, Xin and Liu, Risheng and Luo, Zhongxuan},
      booktitle = {CVPR},
      year      = {2022}
    }
- maintainer note: verify authors/venue before adding.
```

```
## EX-2 chapter 11 should mention method X (do NOT edit book/)
- date: 2026-06-11
- author: codex
- category: book-edit
- where: while adding method X to data/papers.yaml
- status: resolved (example)
- what: Ch.11 §11.3 lists Transformer-era COD methods; method X (CVPR'25) fits and is now in data/.
- why: book/ is author-owned; agent must not edit chapters.
- proposed: consider adding one sentence + citation [@x2025] in §11.3.
- maintainer note: optional; author decides editorial fit.
```

```
## EX-3 new metric key needed (interface-change)
- date: 2026-06-11
- author: codex
- category: interface-change
- where: data/SCHEMA.md §4 metric keys; camo-eval video metrics
- status: resolved (example)
- what: video COD needs a "boundary-F" metric key not in METRIC_KEYS / Appendix B.
- why: METRIC_KEYS is a frozen vocabulary; changing it needs maintainer approval + book sync.
- proposed: add key `bF` to SCHEMA §4 and Appendix B; agent will implement `camo_eval` accordingly afterwards.
- maintainer note: decide name; update SCHEMA + Appendix B + check_api.py EXPECTED.
```

```
## EX-4 unverifiable leaderboard number (left null)
- date: 2026-06-11
- author: codex
- category: verification
- where: data/leaderboard.yaml (ZoomNeXt on NC4K)
- status: resolved (example)
- what: could not locate the NC4K Sm value in the cited paper; left metrics.Sm = null.
- why: no-fabrication rule — never estimate a number.
- proposed: maintainer locate the value (paper table / official repo) or keep null.
- maintainer note: confirm source page/table, then set verified:true.
```

---

## Entries

_No open notes yet._
