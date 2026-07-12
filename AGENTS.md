# AGENTS.md — Repository rules for automated coding assistants

Automated assistants are tools, not maintainers, authors of record, security contacts, or release approvers. The repository owner remains accountable for all merges and public claims.

## 1. Before editing

Read the relevant contracts:

- `docs/PROJECT_PLAN.md`
- `docs/BOOK_STYLE_GUIDE.md` for book work
- `data/SCHEMA.md` for metadata work
- `camo-eval/README.md` and `camo-eval/VALIDATION.md` for metric work
- `ETHICS.md` and `SECURITY.md` for dual-use or vulnerability-related work

## 2. Scope discipline

Work only in the files required by the assigned issue or prompt. Do not infer ownership from the model or tool name used to prepare a change. Cross-component changes are allowed only when an interface actually changes and all consumers, tests, and documentation are updated together.

## 3. Integrity rules

- Never invent citations, results, dataset facts, licenses, URLs, DOIs, versions, or release dates.
- Unknown metadata remains `null` and carries an explicit verification state.
- Do not use a standard metric name for an approximation or heuristic.
- Do not commit datasets, model weights, user uploads, credentials, rendered build directories, or caches.
- Do not mark a result `reproduced` without an executable manifest and provenance.
- Do not describe research agendas as implemented projects.

## 4. Required checks

### Book

```bash
quarto render book --to html
quarto render book --to epub
```

### Data and generated pages

```bash
python scripts/check_data.py
python scripts/build_awesome.py
git diff --exit-code -- awesome/README.md web/papers.md web/datasets.md web/leaderboard.md web/models.md
```

### `camo-eval`

```bash
pip install -e "camo-eval[dev]"
ruff check camo-eval/src camo-eval/tests scripts/check_api.py
black --check camo-eval/src camo-eval/tests scripts/check_api.py
cd camo-eval && pytest --cov=camo_eval --cov-fail-under=80 -q
python -m build
```

### Website

```bash
cd web && npm ci && npm run docs:build
```

## 5. Review boundary

Assistants may propose or implement changes. A human maintainer must review:

- factual and historical claims;
- metric semantics and validation evidence;
- third-party asset rights;
- security disclosures;
- release metadata and versioning;
- any material with meaningful dual-use risk.
