# CamoGED metadata schema 2.0

`data/*.yaml` is the source for generated resource pages. It is not a substitute for the monograph bibliography, and it does not imply comprehensive coverage.

## Common verification fields

- `verification_status`: `verified` | `metadata-only` | `unverified`
- `last_verified`: ISO date or `null`
- `verified_by`: reviewer identifier or `null`
- `source_type`: `primary` | `official-project` | `secondary`

`metadata-only` means the title, authorship/publication identity, and URL were reviewed; it does not validate every claim, dataset property, or reported score.

## `papers.yaml`

Required: `id`, `title`, `authors`, `venue`, `year`, `pillar`, `domain`, `perspective`, `task`, `paper`, `publication_status`, `source_type`, `verification_status`, `last_verified`, `verified_by`.

Optional: `code`, `datasets`, `bibtex_key`, `license`, `notes`.

`publication_status`: `published` | `preprint` | `unpublished` | `project-page`.

## `datasets.yaml`

Required: `id`, `name`, `task`, `modality`, `year`, `link`, `publication_status`, `verification_status`, `last_verified`, `verified_by`, `license_status`.

Optional: `size`, `split`, `annotation`, `license`, `bibtex_key`, `notes`.

`license_status`: `verified` | `unknown` | `restricted`. `license: null` with `license_status: unknown` means the project must not redistribute files.

## `leaderboard.yaml`

This file is a **verified results registry**, not a claim of comprehensive ranking.

Required: `id`, `method`, `dataset`, `task`, `metrics`, `status`, `source`, `verified`, `verification_status`, `last_verified`, `verified_by`, `protocol`, `metric_implementation`.

- `status`: `reported` | `reproduced`
- non-null metrics require `verified: true`, `verification_status: verified`, a primary/official source, and review metadata;
- `reproduced` requires an executable repository-relative manifest and prediction provenance;
- standard metric keys may be used only with validated implementations or when copied from a clearly identified source;
- experimental `*_lite` metrics never populate standard leaderboard keys.

## Controlled vocabularies

- pillar: `generation`, `detection`, `evaluation`
- domain: `physical`, `digital`, `intelligent`
- perspective: `nature`, `war`, `art`, `ai`
- modality: `rgb`, `video`, `multispectral`, `multimodal`, `thermal`, `polarization`, `depth`
- task: `image-cod`, `video-cod`, `instance-cod`, `referring-cod`, `collaborative-cod`, `open-vocab-cos`, `survey`, `generation`, `physical-adversarial`, `digital-adversarial`, `foundation-model`, `dataset`, `application`

Any schema change must update `scripts/check_data.py`, generated surfaces, examples, and the release manifest.
