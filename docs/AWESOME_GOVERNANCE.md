# Awesome Camouflage governance

## 1. Two products, one accepted metadata source

CamoGED maintains two different surfaces:

1. **Awesome Camouflage** is a concise, human-curated reading map. It contains only records with `curated: true` and a useful editorial description.
2. **CamoGED Research Catalog** is the complete accepted metadata registry. It includes `metadata-only` records and is intended for filtering, discovery, and future review.

Automated discovery feeds neither surface directly. A record enters the accepted catalog only through a human-reviewed pull request. Promotion from the catalog to the curated Awesome list is a separate editorial decision.

## 2. Inclusion criteria

A catalog record must satisfy all of the following:

- directly concerns camouflage, concealed/camouflaged vision, camouflage assessment, camouflage generation, biological camouflage, military camouflage, or the art/design/history of camouflage;
- has a traceable primary or official source;
- has a canonical title and a stable identifier or source URL;
- is not a duplicate preprint/final-publication record;
- includes a concise description of why it matters;
- declares publication and verification state;
- uses the multi-axis fields defined below.

The curated Awesome layer additionally requires:

- durable relevance rather than merely recent publication;
- a clear place in the reading map;
- no unresolved identity, source, or scope ambiguity;
- adequate representation balance across tasks and knowledge domains;
- a human editorial decision recorded in git history.

## 3. Multi-axis classification

Every accepted record carries:

- `resource_type`: paper, survey, book, standard, tool, or historical source;
- `pillars[]`: generation, detection, evaluation;
- `tasks[]`: one or more precise research tasks;
- `modalities[]`: RGB, video, depth, thermal, spectral, polarization, multimodal, or vision-language;
- `supervision[]`: fully, weakly, semi, self, unsupervised, zero-shot, prompt-based, training-free, optimization-based, or not applicable;
- `method_families[]`: architectural or methodological families;
- `contexts[]`: computer vision, biological, wildlife, military, art/design, cultural history, and related application contexts.

The legacy singular fields remain temporarily for compatibility with the rest of CamoGED. They are not the authoritative Awesome classification.

## 4. Evidence levels

- `verified`: identity and substantive metadata were checked against an authoritative source;
- `metadata-only`: title, authorship/publication identity, and URL were checked, but substantive claims were not independently validated;
- `unverified`: candidate or legacy record not suitable for public promotion.

A discovery workflow may propose only `metadata-only` records. It cannot create `verified` records.

## 5. Candidate lifecycle

```text
discovered
→ deduplicated
→ enriched
→ triage issue
→ accepted / rejected / deferred
→ metadata-only catalog record
→ optional substantive verification
→ optional curated promotion
```

Rejection or deferral reasons should use one of:

- out of scope;
- duplicate or preprint/final-version collision;
- unverifiable source;
- insufficient technical or historical contribution;
- unsafe operational detail unsuitable for this repository;
- unclear license or redistribution implications;
- superseded project page;
- pending domain-expert review.

## 6. Dynamic update mechanism

### Weekly automated discovery

`.github/workflows/awesome-discovery.yml` runs the configured arXiv and Crossref queries. It:

- retrieves recent candidate metadata;
- normalizes titles and identifiers;
- removes accepted duplicates;
- writes JSON and Markdown artifacts;
- creates a GitHub triage issue.

It has no contents-write permission. A failed individual query is recorded in the scan report while other queries continue. Pull requests run a small live-network smoke scan and require at least one successful arXiv query and one successful Crossref query; scheduled scans may publish a clearly marked partial report during a temporary upstream outage.

### Human-gated acceptance

A maintainer reviews the triage issue, then manually triggers `.github/workflows/awesome-curation.yml` with explicit candidate IDs. The workflow:

- extracts the machine-readable candidate block from the issue;
- appends selected records as `metadata-only` and `curated: false`;
- regenerates all Awesome/catalog pages;
- runs schema, duplication, coverage, freshness, and link checks;
- creates a Draft PR for human review.

No workflow merges the PR automatically.

## 7. Freshness and audit cadence

- arXiv/Crossref candidate discovery: weekly;
- external curated-list comparison: monthly during triage;
- preprint-to-publication reconciliation: monthly;
- broken-link report: weekly;
- coverage-matrix review: quarterly;
- curated Awesome editorial review: at least every six months.

The public pages show the coverage cutoff and last human-review date. The latest automated scan is represented by the newest open or closed issue labeled `awesome:triage`.

## 8. Acceptance gates

`scripts/check_awesome.py` blocks changes when:

- accepted or curated record counts fall below the maintained baseline;
- a major task, modality, or context becomes empty;
- recent-year coverage is insufficient;
- normalized titles, DOI, or arXiv identifiers collide;
- a curated section has no entries;
- dynamic discovery or governance surfaces are missing;
- records omit multi-axis fields or editorial descriptions.

These gates test structural coverage, not scholarly completeness. Quarterly human review remains necessary.

## 9. Relationship to the book, demo, and results registry

- The book may cite the catalog but is not auto-edited by discovery workflows.
- Demo assets and evaluation fixtures are not Awesome resources unless separately cataloged and licensed.
- The results registry remains protocol- and metric-specific; a paper's inclusion in Awesome does not validate its reported scores.
- Cross-component issues found during Awesome maintenance are recorded in `docs/AWESOME_CROSS_COMPONENT_BACKLOG.md` and handled in a later unified revision.
