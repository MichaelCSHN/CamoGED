# CamoGED metadata schema 2.1

`data/*.yaml` is the source for generated resource pages. It is not a substitute for the monograph bibliography, and it does not imply comprehensive coverage.

## Common verification fields

- `verification_status`: `verified` | `metadata-only` | `unverified`
- `last_verified`: ISO date or `null`
- `verified_by`: reviewer identifier or `null`
- `source_type`: `primary` | `official-project` | `secondary`

`metadata-only` means the title, authorship/publication identity, and URL were reviewed; it does not validate every claim, dataset property, or reported score.

## `papers.yaml`: compatibility layer

The following singular fields remain required because other CamoGED components still consume them:

`id`, `title`, `authors`, `venue`, `year`, `pillar`, `domain`, `perspective`, `task`, `paper`, `publication_status`, `source_type`, `verification_status`, `last_verified`, `verified_by`.

Optional compatibility fields: `code`, `datasets`, `bibtex_key`, `license`, `notes`.

`publication_status`: `published` | `preprint` | `unpublished` | `project-page` | `released`.

## Awesome / Research Catalog multi-axis extension

Every accepted resource record additionally requires:

- `resource_type`: `paper`, `survey`, `book`, `standard`, `tool`, `historical-source`, or another reviewed descriptive type;
- `pillars[]`: one or more of `generation`, `detection`, `evaluation`;
- `tasks[]`: precise task/topic tags; this is the authoritative Awesome classification;
- `modalities[]`: sensing or information modalities;
- `supervision[]`: supervision/study mode;
- `method_families[]`: methodological families;
- `contexts[]`: application or knowledge contexts;
- `description`: concise factual editorial description;
- `curated`: whether the record appears in the concise Awesome view;
- `curation_tier`: `core` | `recommended` | `catalog`;
- `date_added`: ISO date;
- `discovery_status`: `accepted` | `deferred` | `rejected`;
- `canonical_url`: canonical source URL.

Optional discovery provenance fields may record the candidate source, query, external identifier, and triage issue. Automated discovery may create only `metadata-only`, `curated: false` records through a human-triggered Draft PR.

The multi-axis tags are intentionally open but are guarded by `scripts/check_awesome.py`, which enforces required coverage of major tasks, modalities, and contexts. New tags should be descriptive, kebab-case, and documented in `docs/AWESOME_GOVERNANCE.md` when they define a new public section.

## `awesome.yaml`

Controls the concise curated view:

- coverage and human-review dates;
- core-reading IDs;
- section titles and multi-axis match rules;
- external lists used only as candidate sources;
- discovery workflow/status surfaces.

It does not contain the complete catalog and does not override record-level verification state.

## `discovery_queries.yaml`

Defines public API sources and candidate-retrieval queries. Discovery output is a triage artifact, not accepted metadata. Changes require a self-test and review of scope, false-positive risk, rate limits, and privacy/security implications.

## `datasets.yaml`

Required: `id`, `name`, `task`, `modality`, `year`, `link`, `publication_status`, `verification_status`, `last_verified`, `verified_by`, `license_status`.

Optional: `size`, `split`, `annotation`, `license`, `bibtex_key`, `notes`.

`license_status`: `verified` | `unknown` | `restricted`. `license: null` with `license_status: unknown` means the project must not redistribute files.

## `leaderboard.yaml`

This file is a **verified results registry**, not a claim of comprehensive ranking.

Required: `id`, `method`, `dataset`, `task`, `metrics`, `status`, `source`, `verified`, `verification_status`, `last_verified`, `verified_by`, `protocol`, `metric_implementation`.

- `status`: `reported` | `reproduced`;
- non-null metrics require `verified: true`, `verification_status: verified`, a primary/official source, and review metadata;
- `reproduced` requires an executable repository-relative manifest and prediction provenance;
- standard metric keys may be used only with validated implementations or when copied from a clearly identified source;
- experimental `*_lite` metrics never populate standard leaderboard keys.

## Compatibility controlled vocabularies

- pillar: `generation`, `detection`, `evaluation`
- domain: `physical`, `digital`, `intelligent`
- perspective: `nature`, `war`, `art`, `ai`
- modality: `rgb`, `video`, `multispectral`, `multimodal`, `thermal`, `polarization`, `depth`
- task: `image-cod`, `video-cod`, `instance-cod`, `referring-cod`, `collaborative-cod`, `open-vocab-cos`, `survey`, `generation`, `physical-adversarial`, `digital-adversarial`, `foundation-model`, `dataset`, `application`

Any schema change must update validation, generated surfaces, examples, and the release manifest where applicable.
