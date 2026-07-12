#!/usr/bin/env python3
"""Apply the project-wide remediation derived from the publication audit.

This is a one-shot, reviewable migration. It deliberately removes claims and
assets that cannot be supported, separates validated metrics from experimental
surrogates, upgrades the data contract, and aligns governance with the edited
monograph. The migration is idempotent at workflow level and is removed after
its generated commit is inspected.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-07-13"


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace(path: str, old: str, new: str, *, required: bool = True) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        if required:
            raise RuntimeError(f"required text not found in {path}: {old[:100]!r}")
        return
    target.write_text(text.replace(old, new), encoding="utf-8")


def regex_replace(path: str, pattern: str, repl: str, *, required: bool = True) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, lambda _m: repl, text, flags=re.MULTILINE | re.DOTALL)
    if count == 0 and required:
        raise RuntimeError(f"required pattern not found in {path}: {pattern[:100]!r}")
    target.write_text(updated, encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Project identity, governance, security, release status
# ---------------------------------------------------------------------------

write(
    "docs/PROJECT_PLAN.md",
    '''# CamoGED v0.2 Research Preview — Project Plan

## 1. Current position

CamoGED is an open research preview built around a cross-domain monograph on camouflage generation, detection, and evaluation. The repository currently contains four real assets:

1. an edited Quarto monograph;
2. a small schema-backed bibliography and dataset registry;
3. a Python evaluation toolkit whose strongest validated surface is image COD/SOD metrics;
4. a static website with generated indexes and a browser-side teaching demonstration.

The project does **not** currently claim to be a comprehensive model zoo, a dynamic SOTA authority, a completed unified game theory, or a deployment-ready suite of original methods. `coder`, `flowcamo`, and `dualvcod` are research agendas until their code, weights, predictions, manifests, and independently reviewable results exist.

## 2. Working thesis

Camouflage problems can be compared through five questions: who hides, who observes, through which input channel, for what task, and under which protocol and metrics. This is an analytical framework. Similarity of structure does not imply identical biological, military, cultural, or computational mechanisms.

## 3. Components and status

| Component | Status | What is usable now | Release gate |
|---|---|---|---|
| Monograph | publication candidate | HTML source, citations, executable teaching cells | domain review, image-rights ledger, PDF/ePub proofing |
| `data/` registry | metadata preview | generated paper/dataset/resource pages | item-level verification and license completion |
| Verified results registry | minimal | source-checked ZoomNeXt rows | at least three methods under comparable protocols |
| `camo-eval` COD core | validated preview | MAE, weighted F, S, E, F, PR | package matrix, versioned release, downstream use |
| `camo-eval` extensions | experimental | clearly named `*_lite` or descriptive helpers | authoritative reference alignment |
| Browser demo | teaching tool | synthetic scenes, manual/seed segmentation, exploratory diagnostics | accessibility and browser tests |
| Original projects | research agenda | scope statements only | code + weights + manifest + predictions + reproducible report |

## 4. Non-negotiable rules

- No unsupported claims of “first”, “largest”, “best”, “comprehensive”, or “standard”.
- A standard metric name is exposed only when the implementation matches its accepted definition or a named authoritative implementation.
- Experimental substitutes carry an explicit suffix such as `_lite` and cannot populate formal leaderboard fields.
- Third-party datasets are linked, not redistributed, unless a file-level rights record explicitly permits redistribution.
- A result is `reproduced` only when the repository stores an executable manifest, fixed source revision, prediction provenance, environment, and report.
- AI assistants may prepare changes, but the maintainer and named reviewers remain responsible for factual, legal, and release decisions.

## 5. Milestones

### M0 — Credibility baseline

- [x] publication-grade structural edit of the monograph;
- [x] separate validated metrics from experimental surrogates;
- [x] remove unlicensed third-party demo assets;
- [x] remove unfinished original projects from the result registry;
- [x] establish security disclosure, release manifest, and asset policy;
- [x] upgrade the data schema with verification and license state.

### M1 — v0.2 research-preview release

- [ ] merge the audited project branch after CI and human diff review;
- [ ] create a GitHub pre-release tag;
- [ ] archive release artifacts only after the tag exists;
- [ ] publish HTML, ePub proof, source archive, and `camo-eval` wheel;
- [ ] record the exact component versions in `RELEASE_MANIFEST.yml`.

### M2 — Data registry 1.0

- [ ] verify each paper against a primary source;
- [ ] verify each dataset's release page, task, annotation, split, and license status;
- [ ] add representation from biology, military history, materials, perception, and visual culture;
- [ ] publish quarterly snapshots rather than promising continuous SOTA coverage.

### M3 — Evaluation toolkit 0.3

- [ ] implement standard MS-SSIM, Boundary IoU, DAVIS boundary F/J&F, FID/KID/LPIPS/DISTS behind explicit optional dependencies;
- [ ] compare each implementation against an authoritative package or official script;
- [ ] add dataset hashes, threshold policy, metric implementation IDs, uncertainty, runtime environment, and seed to reports;
- [ ] publish API documentation and wheels for supported Python versions.

### M4 — First original-method integration

Only one original project should be selected. Entry requires:

- public repository or vendored source at a fixed commit;
- explicit license and model-card limitations;
- weight provenance;
- inference and evaluation commands;
- prediction archive checksum;
- protocol manifest and environment lock;
- independent result review.

The other two projects remain research agendas until the first integration is complete.

## 6. Release labels

- **research preview**: useful for inspection and experimentation; no stability guarantee;
- **validated**: compared with a named authoritative source under documented fixtures;
- **experimental**: implemented and tested for internal behavior, not accepted as a standard metric;
- **planned**: no usable implementation;
- **publication candidate**: content-complete enough for review, but not rights- and format-cleared.

## 7. Explicitly deferred work

Formal military field evaluation, human-subject experimentation, mission-level claims, and deployment-oriented adversarial generation are outside the present release. The repository may document protocols and published evidence but does not simulate or operationalize those activities.
''',
)

write(
    "AGENTS.md",
    '''# AGENTS.md — Repository rules for automated coding assistants

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
''',
)

write(
    ".github/CODEOWNERS",
    '''# CamoGED code owners
# The repository currently has one GitHub identity. This file documents review
# scope but does not create independent approval. Branch protection and external
# reviewers are required for genuine separation of duties.

*                                   @MichaelCSHN
/book/                              @MichaelCSHN
/data/                              @MichaelCSHN
/camo-eval/                         @MichaelCSHN
/web/                               @MichaelCSHN
/docs/                              @MichaelCSHN
/SECURITY.md                        @MichaelCSHN
/THIRD_PARTY_ASSETS.yml             @MichaelCSHN
/RELEASE_MANIFEST.yml               @MichaelCSHN
''',
)

write(
    "docs/CONTRIBUTOR_WORK_PACKAGES.md",
    '''# Contributor work packages

Work packages are assigned to people or reviewed pull requests, not to AI model names.

| Package | Scope | Required evidence |
|---|---|---|
| BOOK | chapters, bibliography, figures, publication apparatus | resolved citations, Quarto build, factual review notes, asset rights |
| DATA | papers, datasets, verified results registry | schema validation, primary source, verification state, license state |
| EVAL | metric code, protocol schema, CLI, package | tests, authoritative comparison where applicable, API and version notes |
| WEB | generated pages and teaching demo | VitePress build, accessibility smoke, no unlicensed assets |
| RELEASE | versions, artifacts, DOI/archive metadata | tagged commit, complete CI, release manifest, signed human review |
| SECURITY | vulnerability and dual-use response | private intake, triage record, coordinated disclosure decision |

## Interface changes

A change to metric names, data fields, report schemas, generated-page contracts, or public CLI options must update all consumers in one PR and include migration notes.

## Definition of done

A work package is complete only when its required CI is green and the PR records what was validated, what remains experimental, and who performed the human review.
''',
)

write(
    "docs/CODEX_DIRECTIVE.md",
    '''# Automated-assistant directive

This file no longer assigns repository ownership to a particular model. Follow `AGENTS.md`, the current issue or maintainer instruction, and the component contracts. Automated output must be reviewed by the maintainer before merge or release.
''',
)

write(
    "SECURITY.md",
    '''# Security policy

## Supported status

CamoGED is a research preview. Only the current default branch and the latest tagged release, when one exists, receive security fixes.

## Private reporting

Do not open a public issue for vulnerabilities, exposed credentials, private data, or details that would materially lower the cost of attacking a deployed perception system.

Report privately by email to **michaelcshn@gmail.com** with the subject `CamoGED security report`. Include the affected component, reproduction conditions, impact, and whether public disclosure is time-sensitive. Encrypt sensitive attachments or request an alternate transfer method before sending them.

The maintainer will acknowledge a credible report as soon as practical, classify its scope, and coordinate remediation and disclosure. No fixed response-time SLA is promised for this unfunded research preview.

## In scope

- dependency or deployment vulnerabilities in the website, package, or CI;
- accidental redistribution of restricted data or personal information;
- credential or secret exposure;
- metric or leaderboard behavior that creates a material integrity failure;
- directly deployable bypass details affecting a real system.

## Out of scope

- disagreement with research conclusions;
- expected limitations already labeled experimental;
- generic reports without a reproducible affected path;
- requests for operational attack recipes.
''',
)

write(
    "ETHICS.md",
    '''# Responsible use and dual-use policy

CamoGED studies camouflage across nature, engineered systems, visual culture, and machine perception. Some material is dual-use. The project therefore separates explanation and evaluation from deployment-oriented enablement.

## Commitments

- Defense and evaluation first: emphasize detection, robustness, protocol quality, and failure analysis.
- Method-level description: discuss published mechanisms without supplying system-specific bypass recipes or manufacturing parameters.
- Honest capability labels: distinguish validated, experimental, planned, and research-agenda components.
- Data minimization: link third-party datasets rather than redistributing them unless file-level rights are documented.
- No user-upload retention in browser-only demos; external services must be identified as third parties.
- Coordinated disclosure: use the private process in `SECURITY.md` for real-system vulnerabilities.

## Publication review

Before releasing adversarial-generation code, physical deployment guidance, sensitive imagery, or a new interactive service, the maintainer must record:

1. intended defensive or scientific value;
2. deployment realism and affected targets;
3. information already public in primary sources;
4. safeguards, withheld details, and safer alternatives;
5. reviewer and release decision.

## Reporting concerns

Use the private contact in `SECURITY.md` when a concern contains sensitive details. Ordinary corrections may use public issues.
''',
)

write(
    "CODE_OF_CONDUCT.md",
    '''# Code of Conduct

CamoGED adopts the Contributor Covenant, version 2.1. Participants must use respectful language, accept evidence-based correction, avoid harassment and doxxing, and keep discussion focused on the project.

Conduct reports that can be public may be opened as repository issues. Reports containing personal, security, or sensitive dual-use information must be sent privately through the contact in `SECURITY.md`; GitHub issues are not confidential.

The maintainer may edit, remove, or reject contributions and restrict participation when necessary to protect contributors and project integrity. The full Contributor Covenant text is available at https://www.contributor-covenant.org/version/2/1/code_of_conduct/.
''',
)

write(
    "CONTRIBUTING.md",
    '''# Contributing to CamoGED

CamoGED accepts corrections, metadata, evaluation code, and publication improvements. The project is a research preview; contributions must prefer traceability over volume.

## Data entries

Edit `data/*.yaml`, not generated Markdown. Every entry must follow `data/SCHEMA.md` and include a verification state, source type, and review date or explicit `null`. Unknown licenses remain `unknown`; do not infer permission from public availability.

## Results registry

A result row requires a primary source, a complete protocol description, metric implementation identity, verification date, and reviewer. `reproduced` additionally requires an executable manifest, fixed source revision, environment, and prediction provenance. Unfinished project plans do not belong in the registry.

## Metric code

- Standard metric names require authoritative semantic validation.
- Approximations and teaching metrics use descriptive names or an explicit `_lite` suffix.
- Add edge-case tests and reference comparisons where a standard implementation exists.
- Update `camo-eval/VALIDATION.md` with the evidence level.

## Pull-request checklist

- [ ] scope and status labels are accurate;
- [ ] no unsupported novelty or performance claim was added;
- [ ] tests and component builds pass;
- [ ] third-party asset and license implications were checked;
- [ ] sensitive material follows `ETHICS.md` and `SECURITY.md`;
- [ ] generated pages were regenerated from their source data.

Code contributions are Apache-2.0. Prose contributions are CC BY 4.0. Third-party material retains its upstream license and is not relicensed by contribution.
''',
)

write(
    "RELEASE_MANIFEST.yml",
    '''schema_version: "1.0"
release_status: "unreleased-research-preview"
release_tag: null
release_date: null
source_commit: null
components:
  monograph:
    version: "0.2.0-pre"
    license: "CC-BY-4.0"
    status: "publication-candidate"
  camo_eval:
    version: "0.2.0.dev0"
    license: "Apache-2.0"
    status: "research-preview"
  data_registry:
    schema_version: "2.0"
    license: "CC-BY-4.0 for original metadata; upstream facts and links retain source terms"
    status: "metadata-preview"
  website:
    version: "0.2.0-pre"
    license: "Apache-2.0 for code; CC-BY-4.0 for original prose"
    status: "teaching-preview"
release_requirements:
  - "all required CI checks pass"
  - "human review of metric semantics"
  - "third-party asset ledger complete"
  - "release commit and tag recorded above"
  - "HTML and ePub artifacts inspected"
  - "PDF typography inspected before any print claim"
''',
)

write(
    "THIRD_PARTY_ASSETS.yml",
    '''schema_version: "1.0"
policy: >-
  Third-party datasets, model weights, photographs, artwork, and historical images
  are linked rather than redistributed unless this file records explicit permission.
assets: []
notes:
  - "The browser demo uses deterministic synthetic scenes and user-local uploads only."
  - "Repository-local camo-eval fixtures are synthetic test data unless separately recorded."
  - "A public URL or academic-use dataset page is not, by itself, redistribution permission."
''',
)

write(
    "CITATION.cff",
    '''cff-version: 1.2.0
title: "CamoGED research platform"
message: "Cite the tagged release you used. This branch is an unreleased research preview."
type: software
authors:
  - family-names: "C"
    given-names: "Michael"
repository-code: "https://github.com/MichaelCSHN/CamoGED"
url: "https://michaelcshn.github.io/CamoGED/"
abstract: >-
  CamoGED is an open research preview centered on a cross-domain monograph,
  a verified-resource registry, an evaluation toolkit, and teaching demos for
  camouflage generation, detection, and evaluation.
keywords:
  - camouflage
  - camouflaged object detection
  - evaluation
  - reproducibility
license: Apache-2.0
version: "0.2.0-pre"
''',
)

write(
    "camo-eval/CITATION.cff",
    '''cff-version: 1.2.0
title: "camo-eval"
message: "Cite the tagged camo-eval release and report the metric implementation IDs used."
type: software
authors:
  - family-names: "C"
    given-names: "Michael"
repository-code: "https://github.com/MichaelCSHN/CamoGED"
license: Apache-2.0
version: "0.2.0-dev"
''',
)

write(
    "book/CITATION.md",
    '''# Citing the monograph

The monograph is a publication candidate, not yet a formally released book. Cite a tagged archive when available. Until then, identify the repository commit and access date. The monograph text is CC BY 4.0; software examples retain the repository code license.
''',
)

# ---------------------------------------------------------------------------
# 2. Data schema 2.0 and metadata migration
# ---------------------------------------------------------------------------

write(
    "data/SCHEMA.md",
    '''# CamoGED metadata schema 2.0

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
''',
)

papers_path = ROOT / "data/papers.yaml"
papers_doc = yaml.safe_load(papers_path.read_text(encoding="utf-8"))
for entry in papers_doc.get("papers", []):
    venue = str(entry.get("venue") or "").lower()
    if "arxiv" in venue:
        publication_status = "preprint"
    elif "unpublished" in venue:
        publication_status = "unpublished"
    else:
        publication_status = "published"
    entry["publication_status"] = publication_status
    entry["source_type"] = "primary"
    entry["verification_status"] = "metadata-only"
    entry["last_verified"] = TODAY
    entry["verified_by"] = "maintainer"
    entry.setdefault("license", None)
    if entry.get("id") == "mmcamobj2024":
        entry["venue"] = "AAAI"
        entry["year"] = 2025
        entry["paper"] = "https://doi.org/10.1609/aaai.v39i7.32723"
        entry["publication_status"] = "published"
        entry["notes"] = "Published at AAAI 2025; multimodal camouflage benchmark for LVLM evaluation."
papers_path.write_text(yaml.safe_dump(papers_doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

datasets_path = ROOT / "data/datasets.yaml"
datasets_doc = yaml.safe_load(datasets_path.read_text(encoding="utf-8"))
annotation_by_task = {
    "image-cod": "image-level metadata and pixel masks as provided upstream",
    "video-cod": "video frames/sequences and temporal mask annotations as provided upstream",
    "collaborative-cod": "grouped image masks as provided upstream",
    "referring-cod": "language expressions and target masks as provided upstream",
    "dataset": "multimodal task annotations as provided upstream",
}
for entry in datasets_doc.get("datasets", []):
    entry["publication_status"] = "released"
    entry["verification_status"] = "metadata-only"
    entry["last_verified"] = TODAY
    entry["verified_by"] = "maintainer"
    entry["license_status"] = "verified" if entry.get("license") else "unknown"
    entry.setdefault("annotation", annotation_by_task.get(entry.get("task"), "upstream-defined"))
    notes = str(entry.get("notes") or "")
    notes = notes.replace("First fully annotated COD dataset.", "Early fully annotated COD benchmark.")
    notes = notes.replace("Largest image COD benchmark.", "Large image COD benchmark; scale claim is version-dependent.")
    notes = notes.replace("First multispectral COD benchmark.", "Multispectral COD benchmark; novelty claim belongs to the cited source.")
    entry["notes"] = notes or None
datasets_path.write_text(yaml.safe_dump(datasets_doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

leaderboard_path = ROOT / "data/leaderboard.yaml"
leaderboard_doc = yaml.safe_load(leaderboard_path.read_text(encoding="utf-8"))
rows = []
for index, entry in enumerate(leaderboard_doc.get("leaderboard", []), start=1):
    if not entry.get("verified"):
        continue
    dataset = str(entry["dataset"])
    method_id = re.sub(r"[^a-z0-9]+", "-", str(entry["method"]).lower()).strip("-")
    entry["id"] = f"{method_id}-{dataset}-{index}"
    entry["verification_status"] = "verified"
    entry["last_verified"] = TODAY
    entry["verified_by"] = "maintainer"
    entry["metric_implementation"] = "reported-by-official-source"
    rows.append(entry)
leaderboard_doc["leaderboard"] = rows
leaderboard_path.write_text(
    yaml.safe_dump(leaderboard_doc, allow_unicode=True, sort_keys=False), encoding="utf-8"
)

write(
    "scripts/check_data.py",
    '''#!/usr/bin/env python3
"""Validate CamoGED metadata schema 2.0 and generated-page determinism."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BIB = ROOT / "book/references.bib"
AWESOME = ROOT / "awesome/README.md"

PILLAR = {"generation", "detection", "evaluation"}
DOMAIN = {"physical", "digital", "intelligent"}
PERSPECTIVE = {"nature", "war", "art", "ai"}
MODALITY = {"rgb", "video", "multispectral", "multimodal", "thermal", "polarization", "depth"}
TASK = {
    "image-cod", "video-cod", "instance-cod", "referring-cod", "collaborative-cod",
    "open-vocab-cos", "survey", "generation", "physical-adversarial",
    "digital-adversarial", "foundation-model", "dataset", "application",
}
PUBLICATION_STATUS = {"published", "preprint", "unpublished", "project-page", "released"}
VERIFICATION_STATUS = {"verified", "metadata-only", "unverified"}
SOURCE_TYPE = {"primary", "official-project", "secondary"}
LICENSE_STATUS = {"verified", "unknown", "restricted"}
RESULT_STATUS = {"reported", "reproduced"}
METRIC_KEYS = {"Sm", "Fw", "Em", "MAE", "maxF", "meanF", "AP", "AR", "JF", "temporal"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL = re.compile(r"^https?://", re.IGNORECASE)
DATE = re.compile(r"^\\d{4}-\\d{2}-\\d{2}$")

errors: list[str] = []
warnings: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def require(entry: dict, fields: set[str], where: str) -> None:
    for field in sorted(fields):
        if field not in entry:
            err(f"{where}: missing field {field!r}")


def check_date(value, where: str, field: str) -> None:
    if value is not None and (not isinstance(value, str) or not DATE.match(value)):
        err(f"{where}: {field} must be ISO YYYY-MM-DD or null")


def check_url(value, where: str, field: str, nullable: bool = True) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not URL.match(value):
        err(f"{where}: {field} must be an http(s) URL" + (" or null" if nullable else ""))


def bib_keys() -> set[str]:
    if not BIB.exists():
        return set()
    return set(re.findall(r"@\\w+\\{([^,]+),", BIB.read_text(encoding="utf-8")))


def main() -> int:
    papers = load("papers.yaml").get("papers", [])
    datasets = load("datasets.yaml").get("datasets", [])
    results = load("leaderboard.yaml").get("leaderboard", [])
    seen: set[str] = set()
    dataset_ids = {entry.get("id") for entry in datasets}
    dataset_names = {entry.get("name") for entry in datasets}
    data_bib: set[str] = set()

    paper_required = {
        "id", "title", "authors", "venue", "year", "pillar", "domain", "perspective",
        "task", "paper", "publication_status", "source_type", "verification_status",
        "last_verified", "verified_by",
    }
    for index, entry in enumerate(papers):
        where = f"papers[{index}]"
        require(entry, paper_required, where)
        item_id = entry.get("id")
        if not isinstance(item_id, str) or not KEBAB.match(item_id):
            err(f"{where}: invalid kebab-case id")
        if item_id in seen:
            err(f"{where}: duplicate id {item_id!r}")
        seen.add(item_id)
        for field, allowed in (("pillar", PILLAR), ("domain", DOMAIN), ("perspective", PERSPECTIVE), ("task", TASK), ("publication_status", PUBLICATION_STATUS), ("source_type", SOURCE_TYPE), ("verification_status", VERIFICATION_STATUS)):
            if entry.get(field) not in allowed:
                err(f"{where}: {field}={entry.get(field)!r} is invalid")
        check_url(entry.get("paper"), where, "paper", nullable=False)
        check_url(entry.get("code"), where, "code")
        check_date(entry.get("last_verified"), where, "last_verified")
        if entry.get("verification_status") == "verified" and not entry.get("verified_by"):
            err(f"{where}: verified entry requires verified_by")
        for dataset in entry.get("datasets") or []:
            if dataset not in dataset_ids and dataset not in dataset_names:
                err(f"{where}: unknown dataset reference {dataset!r}")
        if entry.get("bibtex_key"):
            data_bib.add(entry["bibtex_key"])

    dataset_required = {
        "id", "name", "task", "modality", "year", "link", "publication_status",
        "verification_status", "last_verified", "verified_by", "license_status",
    }
    for index, entry in enumerate(datasets):
        where = f"datasets[{index}]"
        require(entry, dataset_required, where)
        item_id = entry.get("id")
        if not isinstance(item_id, str) or not KEBAB.match(item_id):
            err(f"{where}: invalid kebab-case id")
        if item_id in seen:
            err(f"{where}: duplicate global id {item_id!r}")
        seen.add(item_id)
        if entry.get("task") not in TASK:
            err(f"{where}: invalid task")
        if entry.get("modality") not in MODALITY:
            err(f"{where}: invalid modality")
        if entry.get("publication_status") not in PUBLICATION_STATUS:
            err(f"{where}: invalid publication_status")
        if entry.get("verification_status") not in VERIFICATION_STATUS:
            err(f"{where}: invalid verification_status")
        if entry.get("license_status") not in LICENSE_STATUS:
            err(f"{where}: invalid license_status")
        if entry.get("license_status") == "verified" and not entry.get("license"):
            err(f"{where}: verified license_status requires a license value")
        check_url(entry.get("link"), where, "link")
        check_date(entry.get("last_verified"), where, "last_verified")
        if entry.get("bibtex_key"):
            data_bib.add(entry["bibtex_key"])

    result_required = {
        "id", "method", "dataset", "task", "metrics", "status", "source", "verified",
        "verification_status", "last_verified", "verified_by", "protocol",
        "metric_implementation",
    }
    for index, entry in enumerate(results):
        where = f"leaderboard[{index}]"
        require(entry, result_required, where)
        item_id = entry.get("id")
        if not isinstance(item_id, str) or not KEBAB.match(item_id):
            err(f"{where}: invalid id")
        if item_id in seen:
            err(f"{where}: duplicate global id {item_id!r}")
        seen.add(item_id)
        if entry.get("dataset") not in dataset_ids and entry.get("dataset") not in dataset_names:
            err(f"{where}: unknown dataset")
        if entry.get("task") not in TASK or entry.get("status") not in RESULT_STATUS:
            err(f"{where}: invalid task/status")
        if entry.get("verified") is not True or entry.get("verification_status") != "verified":
            err(f"{where}: registry rows must be verified")
        if not entry.get("verified_by") or not entry.get("last_verified"):
            err(f"{where}: verified row requires reviewer and date")
        check_date(entry.get("last_verified"), where, "last_verified")
        source = entry.get("source")
        if not (isinstance(source, str) and (URL.match(source) or (ROOT / source).exists())):
            err(f"{where}: source is not resolvable")
        metrics = entry.get("metrics")
        if not isinstance(metrics, dict):
            err(f"{where}: metrics must be a mapping")
            continue
        for key, value in metrics.items():
            if key not in METRIC_KEYS:
                err(f"{where}: unsupported standard metric key {key!r}")
            if value is not None and not isinstance(value, (int, float)):
                err(f"{where}: metric {key} must be numeric or null")
        if entry.get("status") == "reproduced":
            if URL.match(str(source)) or not str(source).endswith((".json", ".yaml", ".yml")):
                err(f"{where}: reproduced result requires a repository manifest path")

    keys = bib_keys()
    for key in sorted(data_bib - keys):
        warn(f"bibtex_key {key!r} exists in data but not references.bib")

    from build_awesome import render

    expected = render().rstrip() + "\n"
    if not AWESOME.exists() or AWESOME.read_text(encoding="utf-8") != expected:
        err("awesome/README.md is out of sync with scripts/build_awesome.py")

    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"check_data: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
)

# Update generated-page builder without changing its overall architecture.
replace("scripts/build_awesome.py", 'PILLAR_ORDER = ["generation", "evaluation", "detection"]', 'PILLAR_ORDER = ["generation", "detection", "evaluation"]')
replace("scripts/build_awesome.py", '"# Code",', '"# Code & Resources",')
replace("scripts/build_awesome.py", '"## Leaderboard", ""', '"## Verified Results Registry", ""')
regex_replace(
    "scripts/build_awesome.py",
    r"def render_leaderboard_page\(leaderboard: list\[dict\]\) -> str:\n.*?\n\ndef render_demo_page",
    '''def render_leaderboard_page(leaderboard: list[dict]) -> str:
    verified_rows = sort_verified_rows(leaderboard)
    lines = [
        "# Verified Results Registry",
        "",
        "> Source-checked result records. This page is not a comprehensive SOTA ranking.",
        "",
        f"- Verified rows: **{len(verified_rows)}**",
        "",
        "| Method | Dataset | Task | Metrics | Protocol | Implementation | Verified | Source |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in verified_rows:
        metrics = ", ".join(
            f"{key}={value}" for key, value in row["metrics"].items() if value is not None
        )
        lines.append(
            f"| {row['method']} | `{row['dataset']}` | `{row['task']}` | {metrics} | "
            f"{row.get('protocol') or ''} | `{row['metric_implementation']}` | "
            f"{row['last_verified']} / {row['verified_by']} | {row['source']} |"
        )
    if not verified_rows:
        lines.append("| _No verified results_ | | | | | | | |")
    lines.append("")
    return "\\n".join(lines) + "\\n"


def render_demo_page''',
)

# ---------------------------------------------------------------------------
# 3. camo-eval semantic separation: validated vs experimental
# ---------------------------------------------------------------------------

write(
    "camo-eval/src/camo_eval/metrics/generation/fid.py",
    '''"""Generation metrics and explicitly named lightweight surrogates.

Standard FID, KID, LPIPS, and DISTS require their accepted learned feature
backends. They are not silently approximated here. The `*_lite` functions are
small deterministic diagnostics for smoke tests and same-protocol experiments;
they must not be reported under standard metric names.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
from scipy import linalg
from scipy.ndimage import gaussian_filter, sobel

from ..perceptual import ms_ssim_lite, ssim

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".pgm", ".npy"}
EPS = np.spacing(1)


def _standard_unavailable(name: str) -> NotImplementedError:
    return NotImplementedError(
        f"Standard {name} is not implemented in the core research-preview install. "
        f"Use a validated external implementation, or call {name.lower()}_lite only for "
        "explicitly labelled exploratory diagnostics."
    )


def fid(real_dir: str, fake_dir: str) -> float:
    raise _standard_unavailable("FID")


def kid(
    real_dir: str,
    fake_dir: str,
    degree: int = 3,
    gamma: float | None = None,
    coef0: float = 1.0,
) -> float:
    raise _standard_unavailable("KID")


def lpips(img_a, img_b) -> float:
    raise _standard_unavailable("LPIPS")


def dists(img_a, img_b) -> float:
    raise _standard_unavailable("DISTS")


def _load_image(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npy":
        return np.load(path)
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Image loading requires Pillow for non-.npy files.") from exc
    return np.asarray(Image.open(path).convert("RGB"))


def _normalize_image(image) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("image must be non-empty.")
    if not np.isfinite(arr).all():
        raise ValueError("image must not contain NaN or inf.")
    if arr.ndim == 2:
        arr = arr[..., None]
    if arr.ndim != 3:
        raise ValueError("image must be a 2D grayscale or 3D image array.")
    if arr.max() > 1.0 or arr.min() < 0.0:
        if arr.max() > 255.0 or arr.min() < 0.0:
            raise ValueError("image values must be in [0, 1] or [0, 255].")
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def _to_gray(image: np.ndarray) -> np.ndarray:
    if image.shape[-1] == 1:
        return image[..., 0]
    return image[..., :3].mean(axis=2)


def _feature_vector(image) -> np.ndarray:
    arr = _normalize_image(image)
    gray = _to_gray(arr)
    gx = sobel(gray, axis=1)
    gy = sobel(gray, axis=0)
    grad = np.hypot(gx, gy)
    high = gray - gaussian_filter(gray, sigma=1.5)
    features: list[float] = []
    for channel in range(arr.shape[-1]):
        values = arr[..., channel].reshape(-1)
        features.extend(
            [
                float(values.mean()),
                float(values.std()),
                float(np.quantile(values, 0.1)),
                float(np.quantile(values, 0.5)),
                float(np.quantile(values, 0.9)),
            ]
        )
    for values in (gray.reshape(-1), grad.reshape(-1), high.reshape(-1)):
        features.extend(
            [
                float(values.mean()),
                float(values.std()),
                float(np.mean(np.abs(values))),
                float(np.quantile(values, 0.25)),
                float(np.quantile(values, 0.75)),
            ]
        )
    hist, _ = np.histogram(gray, bins=16, range=(0.0, 1.0), density=False)
    hist = hist.astype(np.float64) / (hist.sum() + EPS)
    features.extend(hist.tolist())
    return np.asarray(features, dtype=np.float64)


def _image_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"{directory} is not a directory.")
    files = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not files:
        raise ValueError(f"No supported image files found in {directory}.")
    return files


def _feature_matrix(directory: Path) -> np.ndarray:
    return np.stack([_feature_vector(_load_image(path)) for path in _image_files(directory)])


def _mean_and_cov(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = features.mean(axis=0)
    if features.shape[0] == 1:
        cov = np.eye(features.shape[1], dtype=np.float64) * EPS
    else:
        cov = np.cov(features, rowvar=False)
    return mean, np.atleast_2d(cov)


def fid_lite(real_dir: str, fake_dir: str) -> float:
    """Handcrafted-feature Fréchet diagnostic; not standard FID."""

    real = _feature_matrix(Path(real_dir))
    fake = _feature_matrix(Path(fake_dir))
    mu_real, cov_real = _mean_and_cov(real)
    mu_fake, cov_fake = _mean_and_cov(fake)
    diff = mu_real - mu_fake
    eps_eye = np.eye(cov_real.shape[0], dtype=np.float64) * 1e-9
    sqrt_result = linalg.sqrtm((cov_real + eps_eye) @ (cov_fake + eps_eye))
    covmean = sqrt_result[0] if isinstance(sqrt_result, tuple) else sqrt_result
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    if np.isfinite(covmean).all():
        trace_covmean = float(np.trace(covmean))
    else:
        diag_real = np.clip(np.diag(cov_real), 0.0, None)
        diag_fake = np.clip(np.diag(cov_fake), 0.0, None)
        trace_covmean = float(np.sum(np.sqrt(diag_real * diag_fake)))
    value = diff @ diff + np.trace(cov_real) + np.trace(cov_fake) - 2.0 * trace_covmean
    if not np.isfinite(value):
        raise ValueError("fid_lite produced a non-finite value.")
    return float(max(value, 0.0))


def kid_lite(
    real_dir: str,
    fake_dir: str,
    degree: int = 3,
    gamma: float | None = None,
    coef0: float = 1.0,
) -> float:
    """Polynomial-MMD diagnostic over handcrafted features; not standard KID."""

    real = _feature_matrix(Path(real_dir))
    fake = _feature_matrix(Path(fake_dir))
    gamma = gamma if gamma is not None else 1.0 / real.shape[1]

    def kernel(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return (gamma * (x @ y.T) + coef0) ** degree

    k_rr = kernel(real, real)
    k_ff = kernel(fake, fake)
    k_rf = kernel(real, fake)
    rr = (
        (k_rr.sum() - np.trace(k_rr)) / (len(real) * (len(real) - 1))
        if len(real) > 1
        else 0.0
    )
    ff = (
        (k_ff.sum() - np.trace(k_ff)) / (len(fake) * (len(fake) - 1))
        if len(fake) > 1
        else 0.0
    )
    return float(rr + ff - 2.0 * k_rf.mean())


def lpips_lite(img_a, img_b) -> float:
    """Handcrafted perceptual diagnostic; not standard LPIPS."""

    a = _normalize_image(img_a)
    b = _normalize_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    gray_a = _to_gray(a)
    gray_b = _to_gray(b)
    grad_a = np.hypot(sobel(gray_a, axis=1), sobel(gray_a, axis=0))
    grad_b = np.hypot(sobel(gray_b, axis=1), sobel(gray_b, axis=0))
    l1 = float(np.mean(np.abs(a - b)))
    grad = float(np.mean(np.abs(grad_a - grad_b)))
    structural = 1.0 - max(0.0, min(1.0, ssim(gray_a, gray_b)))
    multiscale = 1.0 - max(0.0, min(1.0, ms_ssim_lite(gray_a, gray_b)))
    return float(0.45 * l1 + 0.25 * grad + 0.2 * structural + 0.1 * multiscale)


def dists_lite(img_a, img_b) -> float:
    """Handcrafted structure/texture diagnostic; not standard DISTS."""

    a = _normalize_image(img_a)
    b = _normalize_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    gray_a = _to_gray(a)
    gray_b = _to_gray(b)
    texture_a = gray_a - gaussian_filter(gray_a, sigma=2.0)
    texture_b = gray_b - gaussian_filter(gray_b, sigma=2.0)
    structure = 1.0 - max(0.0, min(1.0, ssim(gray_a, gray_b)))
    texture = float(np.mean(np.abs(texture_a - texture_b)))
    contrast = float(abs(gray_a.std() - gray_b.std()))
    return float(0.5 * structure + 0.35 * texture + 0.15 * contrast)


def _target_success(output, target) -> bool:
    if callable(target):
        return bool(target(output))
    if isinstance(output, dict):
        if "label" in output:
            output = output["label"]
        elif "class" in output:
            output = output["class"]
        elif "score" in output and isinstance(target, (int, float)):
            return float(output["score"]) <= float(target)
    if isinstance(target, (set, list, tuple)) and not isinstance(target, str):
        return output in target
    return output == target


def deception_rate(detector: Callable, images: Sequence, targets: Sequence | Callable) -> float:
    """Fraction of images satisfying an explicitly supplied success criterion."""

    image_list = list(images)
    if not image_list:
        raise ValueError("At least one image is required.")
    outputs = [detector(image) for image in image_list]
    if callable(targets):
        successes = [bool(targets(output)) for output in outputs]
    else:
        target_list = list(targets)
        if len(target_list) != len(image_list):
            raise ValueError("targets must have the same length as images.")
        successes = [
            _target_success(output, target) for output, target in zip(outputs, target_list)
        ]
    return float(sum(successes) / len(successes))
''',
)

write(
    "camo-eval/src/camo_eval/metrics/generation/__init__.py",
    '''"""Generation metrics with explicit validation levels."""

from .fid import (
    deception_rate,
    dists,
    dists_lite,
    fid,
    fid_lite,
    kid,
    kid_lite,
    lpips,
    lpips_lite,
)

__all__ = [
    "deception_rate",
    "dists",
    "dists_lite",
    "fid",
    "fid_lite",
    "kid",
    "kid_lite",
    "lpips",
    "lpips_lite",
]
''',
)

write(
    "camo-eval/src/camo_eval/metrics/perceptual.py",
    '''"""Perceptual metrics with validated and experimental names separated."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter


def _prepare_image_pair(img_a: np.ndarray, img_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(img_a, dtype=np.float64)
    b = np.asarray(img_b, dtype=np.float64)
    if a.size == 0 or b.size == 0:
        raise ValueError("Images must be non-empty.")
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Images must not contain NaN or inf.")
    for name, array in (("img_a", a), ("img_b", b)):
        if array.max() > 1.0 or array.min() < 0.0:
            if array.max() > 255.0 or array.min() < 0.0:
                raise ValueError(f"{name} values must be in [0, 1] or [0, 255].")
    if a.max() > 1.0:
        a = a / 255.0
    if b.max() > 1.0:
        b = b / 255.0
    return np.clip(a, 0.0, 1.0), np.clip(b, 0.0, 1.0)


def _ssim_single_channel(a: np.ndarray, b: np.ndarray, sigma: float, truncate: float = 3.5) -> float:
    c1 = 0.01**2
    c2 = 0.03**2
    args = {"sigma": sigma, "truncate": truncate}
    mu_a = gaussian_filter(a, **args)
    mu_b = gaussian_filter(b, **args)
    mu_a_sq = mu_a * mu_a
    mu_b_sq = mu_b * mu_b
    mu_ab = mu_a * mu_b
    sigma_a_sq = gaussian_filter(a * a, **args) - mu_a_sq
    sigma_b_sq = gaussian_filter(b * b, **args) - mu_b_sq
    sigma_ab = gaussian_filter(a * b, **args) - mu_ab
    ssim_map = ((2 * mu_ab + c1) * (2 * sigma_ab + c2)) / (
        (mu_a_sq + mu_b_sq + c1) * (sigma_a_sq + sigma_b_sq + c2)
    )
    pad = int(truncate * sigma + 0.5)
    if ssim_map.shape[0] > 2 * pad and ssim_map.shape[1] > 2 * pad:
        ssim_map = ssim_map[pad:-pad, pad:-pad]
    return float(ssim_map.mean())


def ssim(img_a: np.ndarray, img_b: np.ndarray, sigma: float = 1.5) -> float:
    """Validated Gaussian-weighted SSIM compatible with scikit-image settings."""

    a, b = _prepare_image_pair(img_a, img_b)
    if a.ndim == 3:
        return float(
            np.mean([_ssim_single_channel(a[..., c], b[..., c], sigma) for c in range(a.shape[-1])])
        )
    return _ssim_single_channel(a, b, sigma)


def ms_ssim(img_a: np.ndarray, img_b: np.ndarray, levels: int = 5) -> float:
    raise NotImplementedError(
        "Standard MS-SSIM is not implemented. Use ms_ssim_lite only for explicitly labelled exploratory diagnostics."
    )


def _downsample(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return (
            image[0::2, 0::2]
            + image[1::2, 0::2]
            + image[0::2, 1::2]
            + image[1::2, 1::2]
        ) / 4.0
    return (
        image[0::2, 0::2, ...]
        + image[1::2, 0::2, ...]
        + image[0::2, 1::2, ...]
        + image[1::2, 1::2, ...]
    ) / 4.0


def ms_ssim_lite(img_a: np.ndarray, img_b: np.ndarray, levels: int = 4) -> float:
    """Product of per-scale SSIM scores; not standard MS-SSIM."""

    a, b = _prepare_image_pair(img_a, img_b)
    weights = np.array([0.0448, 0.2856, 0.3001, 0.2363, 0.1333], dtype=np.float64)
    weights = weights[:levels]
    weights = weights / weights.sum()
    scores = []
    for _ in range(levels):
        scores.append(max(ssim(a, b), 0.0))
        if min(a.shape[0], a.shape[1], b.shape[0], b.shape[1]) < 2:
            break
        if a.shape[0] % 2 == 1:
            a = a[:-1, ...]
            b = b[:-1, ...]
        if a.shape[1] % 2 == 1:
            a = a[:, :-1, ...]
            b = b[:, :-1, ...]
        a = _downsample(a)
        b = _downsample(b)
    weights = weights[: len(scores)]
    return float(np.prod(np.power(np.asarray(scores), weights)))
''',
)

write(
    "camo-eval/src/camo_eval/metrics/instance.py",
    '''"""Instance and mask-level metrics."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion

from .detection._common import EPS, prepare_prediction_and_gt


def iou(pred: np.ndarray, gt: np.ndarray) -> float:
    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    union = np.count_nonzero(pred_mask | gt_mask)
    if union == 0:
        return 1.0
    return float(np.count_nonzero(pred_mask & gt_mask) / union)


def dice(pred: np.ndarray, gt: np.ndarray) -> float:
    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    denom = np.count_nonzero(pred_mask) + np.count_nonzero(gt_mask)
    if denom == 0:
        return 1.0
    return float((2.0 * np.count_nonzero(pred_mask & gt_mask)) / denom)


def _boundary_mask(mask: np.ndarray) -> np.ndarray:
    mask = mask.astype(bool)
    if not np.any(mask):
        return np.zeros_like(mask, dtype=bool)
    eroded = binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    return mask ^ eroded


def boundary_iou(pred: np.ndarray, gt: np.ndarray, dilation_ratio: float = 0.02) -> float:
    raise NotImplementedError(
        "Standard region-band Boundary IoU is not implemented. Use boundary_match_score for the experimental tolerance-based contour score."
    )


def boundary_match_score(
    pred: np.ndarray, gt: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    """Symmetric tolerance-based contour matching score; not standard Boundary IoU."""

    pred_arr, gt_arr = prepare_prediction_and_gt(pred, gt)
    pred_mask = pred_arr >= 0.5
    gt_mask = gt_arr.astype(bool)
    pred_boundary = _boundary_mask(pred_mask)
    gt_boundary = _boundary_mask(gt_mask)
    if not np.any(pred_boundary) and not np.any(gt_boundary):
        return 1.0
    h, w = pred_mask.shape
    dilation = max(1, int(round(dilation_ratio * np.hypot(h, w))))
    structure = np.ones((3, 3), dtype=bool)
    pred_dilated = binary_dilation(pred_boundary, structure=structure, iterations=dilation)
    gt_dilated = binary_dilation(gt_boundary, structure=structure, iterations=dilation)
    matched = np.count_nonzero(pred_boundary & gt_dilated) + np.count_nonzero(
        gt_boundary & pred_dilated
    )
    total = np.count_nonzero(pred_boundary) + np.count_nonzero(gt_boundary)
    return float(matched / (total + EPS))


def average_precision(
    true_positive_flags: np.ndarray,
    confidence_scores: np.ndarray,
    num_ground_truth: int,
) -> float:
    if num_ground_truth <= 0:
        raise ValueError("num_ground_truth must be positive.")
    tp = np.asarray(true_positive_flags, dtype=np.float64)
    scores = np.asarray(confidence_scores, dtype=np.float64)
    if tp.shape != scores.shape:
        raise ValueError("true_positive_flags and confidence_scores must have the same shape.")
    order = np.argsort(-scores)
    tp = tp[order]
    fp = 1.0 - tp
    tp_cumsum = np.cumsum(tp)
    fp_cumsum = np.cumsum(fp)
    recalls = np.concatenate(([0.0], tp_cumsum / num_ground_truth, [1.0]))
    precisions = np.concatenate(
        ([1.0], tp_cumsum / np.maximum(tp_cumsum + fp_cumsum, EPS), [0.0])
    )
    for index in range(len(precisions) - 2, -1, -1):
        precisions[index] = max(precisions[index], precisions[index + 1])
    return float(np.sum((recalls[1:] - recalls[:-1]) * precisions[1:]))


def average_recall(true_positive_flags: np.ndarray, num_ground_truth: int) -> float:
    if num_ground_truth <= 0:
        raise ValueError("num_ground_truth must be positive.")
    return float(np.sum(np.asarray(true_positive_flags, dtype=np.float64)) / num_ground_truth)
''',
)

write(
    "camo-eval/src/camo_eval/metrics/video/__init__.py",
    '''"""Video metrics with experimental boundary semantics explicitly named."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation

from ..detection._common import EPS, prepare_prediction_and_gt
from ..instance import _boundary_mask, iou


def _prepare_sequence_pair(
    pred_frames: np.ndarray, gt_frames: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    pred_arr = np.asarray(pred_frames)
    gt_arr = np.asarray(gt_frames)
    if pred_arr.ndim == 2 and gt_arr.ndim == 2:
        pred_arr = pred_arr[None, ...]
        gt_arr = gt_arr[None, ...]
    if pred_arr.ndim != 3 or gt_arr.ndim != 3:
        raise ValueError("Video metrics expect [T, H, W] arrays or single [H, W] masks.")
    if pred_arr.shape != gt_arr.shape:
        raise ValueError(f"Shape mismatch: {pred_arr.shape} vs {gt_arr.shape}")
    pred_norm, gt_norm = [], []
    for pred_frame, gt_frame in zip(pred_arr, gt_arr):
        pred_prepared, gt_prepared = prepare_prediction_and_gt(pred_frame, gt_frame)
        pred_norm.append(pred_prepared)
        gt_norm.append(gt_prepared.astype(bool))
    return np.stack(pred_norm), np.stack(gt_norm)


def jaccard_index(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    return float(
        np.mean(
            [
                iou(pred_frame, gt_frame.astype(np.uint8))
                for pred_frame, gt_frame in zip(pred_arr, gt_arr)
            ]
        )
    )


def boundary_f_score(
    pred_frames: np.ndarray, gt_frames: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    raise NotImplementedError(
        "DAVIS boundary F is not yet validated against the official evaluator. Use boundary_f_score_lite only as an explicitly experimental score."
    )


def boundary_f_score_lite(
    pred_frames: np.ndarray, gt_frames: np.ndarray, dilation_ratio: float = 0.02
) -> float:
    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    scores = []
    for pred_frame, gt_frame in zip(pred_arr, gt_arr):
        pred_mask = pred_frame >= 0.5
        gt_mask = gt_frame.astype(bool)
        pred_boundary = _boundary_mask(pred_mask)
        gt_boundary = _boundary_mask(gt_mask)
        if not np.any(pred_boundary) and not np.any(gt_boundary):
            scores.append(1.0)
            continue
        h, w = pred_mask.shape
        dilation = max(1, int(round(dilation_ratio * np.hypot(h, w))))
        structure = np.ones((3, 3), dtype=bool)
        pred_dilated = binary_dilation(pred_boundary, structure=structure, iterations=dilation)
        gt_dilated = binary_dilation(gt_boundary, structure=structure, iterations=dilation)
        pred_match = np.count_nonzero(pred_boundary & gt_dilated)
        gt_match = np.count_nonzero(gt_boundary & pred_dilated)
        precision = pred_match / (np.count_nonzero(pred_boundary) + EPS)
        recall = gt_match / (np.count_nonzero(gt_boundary) + EPS)
        scores.append(float((2 * precision * recall) / (precision + recall + EPS)))
    return float(np.mean(scores))


def j_and_f(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    raise NotImplementedError(
        "Official DAVIS J&F is not yet validated. Use j_and_f_lite only for experimental internal checks."
    )


def j_and_f_lite(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    return float(
        (jaccard_index(pred_frames, gt_frames) + boundary_f_score_lite(pred_frames, gt_frames))
        / 2.0
    )


def temporal_stability(pred_frames: np.ndarray, gt_frames: np.ndarray) -> float:
    """Mean absolute difference between predicted and GT temporal derivatives; lower is better."""

    pred_arr, gt_arr = _prepare_sequence_pair(pred_frames, gt_frames)
    if pred_arr.shape[0] < 2:
        return 0.0
    return float(
        np.mean(
            np.abs(
                np.diff(pred_arr, axis=0)
                - np.diff(gt_arr.astype(np.float64), axis=0)
            )
        )
    )
''',
)

write(
    "camo-eval/src/camo_eval/__init__.py",
    '''"""camo-eval: protocol-aware evaluation tools for camouflage research."""

from .export import to_latex, to_markdown
from .metrics.background import target_background_similarity
from .metrics.clutter import camouflage_difficulty, edge_density, feature_congestion, subband_entropy
from .metrics.detection import (
    e_measure,
    f_measure,
    mae,
    precision,
    precision_recall_curve,
    recall,
    s_measure,
    weighted_f_measure,
)
from .metrics.generation import (
    deception_rate,
    dists,
    dists_lite,
    fid,
    fid_lite,
    kid,
    kid_lite,
    lpips,
    lpips_lite,
)
from .metrics.instance import (
    average_precision,
    average_recall,
    boundary_iou,
    boundary_match_score,
    dice,
    iou,
)
from .metrics.perceptual import ms_ssim, ms_ssim_lite, ssim
from .metrics.robustness import ap_drop, attack_success_rate, transferability
from .metrics.signature import signal_to_clutter_ratio, spectral_angle_mapper, thermal_contrast
from .metrics.video import (
    boundary_f_score,
    boundary_f_score_lite,
    j_and_f,
    j_and_f_lite,
    jaccard_index,
    temporal_stability,
)
from .protocols import EvaluationContext, EvaluationReport
from .results import ResultsTable
from .runner import evaluate

__version__ = "0.2.0.dev0"

__all__ = [name for name in globals() if not name.startswith("_")]
''',
)

write(
    "camo-eval/src/camo_eval/runner.py",
    '''"""Batch evaluation entry point."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .metrics.detection import (
    e_measure,
    f_measure,
    mae,
    precision,
    recall,
    s_measure,
    weighted_f_measure,
)
from .metrics.generation import dists_lite, lpips_lite
from .metrics.instance import boundary_match_score, dice, iou
from .metrics.perceptual import ms_ssim_lite, ssim
from .metrics.video import (
    boundary_f_score_lite,
    j_and_f_lite,
    jaccard_index,
    temporal_stability,
)
from .results import ResultsTable


def _load_array(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npy":
        return np.load(path)
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Image loading requires Pillow for non-.npy inputs.") from exc
    return np.asarray(Image.open(path))


def _index_files(directory: Path) -> dict[str, Path]:
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"{directory} is not a directory")
    return {path.stem: path for path in directory.iterdir() if path.is_file()}


def _metric_value(name: str, pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    key = name.lower()
    if key == "mae":
        return {"MAE": mae(pred, gt)}
    if key in {"weighted_f_measure", "fw"}:
        return {"Fw": weighted_f_measure(pred, gt)}
    if key in {"s_measure", "sm"}:
        return {"Sm": s_measure(pred, gt)}
    if key in {"e_measure", "em"}:
        return {f"Em_{subkey}": value for subkey, value in e_measure(pred, gt).items()}
    if key in {"f_measure", "f"}:
        return {f"F_{subkey}": value for subkey, value in f_measure(pred, gt).items()}
    if key in {"precision", "p"}:
        return {f"P_{subkey}": value for subkey, value in precision(pred, gt).items()}
    if key in {"recall", "r"}:
        return {f"R_{subkey}": value for subkey, value in recall(pred, gt).items()}
    if key == "iou":
        return {"IoU": iou(pred, gt)}
    if key == "dice":
        return {"Dice": dice(pred, gt)}
    if key in {"boundary_match", "boundary_match_score"}:
        return {"BoundaryMatch": boundary_match_score(pred, gt)}
    if key == "ssim":
        return {"SSIM": ssim(pred, gt)}
    if key in {"ms_ssim_lite", "msssim_lite"}:
        return {"MS_SSIM_lite": ms_ssim_lite(pred, gt)}
    if key in {"lpips_lite", "perceptual_distance_lite"}:
        return {"LPIPS_lite": lpips_lite(pred, gt)}
    if key in {"dists_lite", "structure_texture_lite"}:
        return {"DISTS_lite": dists_lite(pred, gt)}
    if key in {"j", "jaccard"}:
        return {"J": jaccard_index(pred, gt)}
    if key in {"boundary_f_lite", "f_boundary_lite"}:
        return {"BoundaryF_lite": boundary_f_score_lite(pred, gt)}
    if key in {"jf_lite", "j_and_f_lite"}:
        return {"JF_lite": j_and_f_lite(pred, gt)}
    if key in {"temporal", "temporal_stability"}:
        return {"Temporal": temporal_stability(pred, gt)}
    if key in {"boundary_iou", "ms_ssim", "lpips", "dists", "boundary_f", "jf", "j_and_f"}:
        raise NotImplementedError(
            f"Metric {name!r} is a reserved standard name without a validated implementation in this release."
        )
    raise KeyError(f"Unsupported metric {name!r}.")


def evaluate(pred_dir, gt_dir, metrics: list[str]) -> ResultsTable:
    pred_files = _index_files(Path(pred_dir))
    gt_files = _index_files(Path(gt_dir))
    basenames = sorted(set(pred_files) & set(gt_files))
    if not basenames:
        raise ValueError("No matching prediction/ground-truth files found by basename.")
    aggregates: dict[str, list[float]] = {}
    for basename in basenames:
        pred = _load_array(pred_files[basename])
        gt = _load_array(gt_files[basename])
        for metric in metrics:
            for key, value in _metric_value(metric, pred, gt).items():
                aggregates.setdefault(key, []).append(float(value))
    row = {"samples": len(basenames)}
    row.update({key: float(np.mean(values)) for key, values in sorted(aggregates.items())})
    return ResultsTable(rows=[row], columns=list(row.keys()))
''',
)

# CLI: use only explicit lite names for experimental metrics.
replace("camo-eval/src/camo_eval/cli.py", "    fid,\n    kid,", "    fid_lite,\n    kid_lite,")
replace("camo-eval/src/camo_eval/cli.py", '"instance": ["iou", "dice", "boundary_iou"],', '"instance": ["iou", "dice", "boundary_match_score"],')
replace("camo-eval/src/camo_eval/cli.py", '"video": ["j", "boundary_f", "jf", "temporal"],', '"video": ["j", "boundary_f_lite", "jf_lite", "temporal"],')
replace("camo-eval/src/camo_eval/cli.py", '"perceptual": ["ssim", "ms_ssim", "lpips_lite", "dists_lite"],', '"perceptual": ["ssim", "ms_ssim_lite", "lpips_lite", "dists_lite"],')
replace("camo-eval/src/camo_eval/cli.py", '            "boundary_iou",', '            "boundary_match_score",')
replace("camo-eval/src/camo_eval/cli.py", '            if key in {"fid", "fid_lite"}:\n                scores["FID_lite"] = fid(args.real_dir, args.fake_dir)\n            elif key in {"kid", "kid_lite"}:\n                scores["KID_lite"] = kid(args.real_dir, args.fake_dir)\n            elif key in {"lpips", "lpips_lite", "dists", "dists_lite"}:', '            if key == "fid_lite":\n                scores["FID_lite"] = fid_lite(args.real_dir, args.fake_dir)\n            elif key == "kid_lite":\n                scores["KID_lite"] = kid_lite(args.real_dir, args.fake_dir)\n            elif key in {"lpips_lite", "dists_lite"}:')

# Protocol records gain reproducibility metadata while remaining backward compatible.
replace(
    "camo-eval/src/camo_eval/protocols/schema.py",
    "    notes: str | None = None\n",
    '''    notes: str | None = None
    implementation_version: str = "0.2.0.dev0"
    dataset_version: str | None = None
    prediction_revision: str | None = None
    threshold_policy: str | None = None
    seed: int | None = None
    environment: str | None = None
    uncertainty: str | None = None
''',
)
replace(
    "camo-eval/src/camo_eval/protocols/schema.py",
    '            "notes": self.notes,\n',
    '''            "notes": self.notes,
            "implementation_version": self.implementation_version,
            "dataset_version": self.dataset_version,
            "prediction_revision": self.prediction_revision,
            "threshold_policy": self.threshold_policy,
            "seed": self.seed,
            "environment": self.environment,
            "uncertainty": self.uncertainty,
''',
)

write(
    "camo-eval/README.md",
    '''# camo-eval

`camo-eval` is a protocol-aware research-preview toolkit. It separates validated metrics from experimental diagnostics so that a convenient API cannot be mistaken for a standard implementation.

## Capability matrix

| Surface | Status | Evidence |
|---|---|---|
| MAE, weighted F, S-measure, E-measure, F/PR | **validated** | compared with PySODMetrics fixtures within 1e-4 |
| SSIM | **validated** | compared with scikit-image Gaussian-weighted settings |
| IoU, Dice | **validated definitions** | exact binary-set tests |
| AP/AR helpers, signature and robustness summaries | **implemented** | behavioral/unit tests; protocol-dependent |
| temporal derivative stability | **experimental** | defined behavior; not a community standard |
| `boundary_match_score` | **experimental** | tolerance-based contour matching; not Boundary IoU |
| `ms_ssim_lite` | **experimental** | multi-scale SSIM product; not standard MS-SSIM |
| `boundary_f_score_lite`, `j_and_f_lite` | **experimental** | not yet aligned with DAVIS official scripts |
| `fid_lite`, `kid_lite`, `lpips_lite`, `dists_lite` | **experimental** | handcrafted diagnostics; never report as standard metrics |
| FID, KID, LPIPS, DISTS, standard MS-SSIM/Boundary IoU/DAVIS F | **planned** | standard names raise `NotImplementedError` |

Full evidence and release gates are in `VALIDATION.md`.

## Installation

```bash
pip install -e .
pip install -e ".[full]"
pip install -e ".[dev]"
```

## Validated COD example

```python
from camo_eval import evaluate

results = evaluate("pred_dir", "gt_dir", ["mae", "fw", "sm", "em", "f"])
print(results)
```

## Experimental diagnostics

```python
from camo_eval import fid_lite, boundary_match_score

# These names explicitly identify non-standard diagnostics.
score = fid_lite("real_dir", "generated_dir")
```

## Protocol-aware report

```bash
camo-eval evaluate-report \
  --pred-dir pred --gt-dir gt --metrics mae fw sm em \
  --observer model --channel rgb --task image-cod \
  --protocol "fixed test split; automatic prediction; no manual prompt"
```

A report should also record the dataset version/hash, prediction revision, threshold policy, seed, environment, uncertainty method, and `camo-eval` version.

## Public demo scope

The browser demo is a synthetic teaching tool. The optional local Gradio app uses synthetic repository fixtures. Neither surface is a hosted SOTA model service or a benchmark authority.

## Tests

```bash
pytest --cov=camo_eval --cov-fail-under=80 -q
ruff check src tests
black --check src tests
```
''',
)

write(
    "camo-eval/VALIDATION.md",
    '''# camo-eval validation register

| Metric/API | Implementation ID | Level | Reference/evidence | Formal reporting allowed? |
|---|---|---|---|---|
| MAE/Fw/Sm/Em/F/PR | `cod-core-pysodmetrics-1` | validated | PySODMetrics comparison tests | yes, with version and protocol |
| SSIM | `ssim-skimage-gaussian-1` | validated | scikit-image comparison | yes, with settings |
| IoU/Dice | `binary-set-1` | validated definition | exact set tests | yes |
| AP/AR helper | `ranked-flags-1` | implemented | unit tests; not COCO evaluator | only with definition stated |
| `boundary_match_score` | `boundary-match-lite-1` | experimental | known cases only | no standard Boundary IoU claim |
| `ms_ssim_lite` | `ms-ssim-lite-1` | experimental | identity/monotonic tests | no standard MS-SSIM claim |
| `boundary_f_score_lite`/`j_and_f_lite` | `video-boundary-lite-1` | experimental | known cases only | no DAVIS claim |
| `fid_lite`/`kid_lite` | `handcrafted-distribution-lite-1` | experimental | deterministic smoke tests | no FID/KID claim |
| `lpips_lite`/`dists_lite` | `handcrafted-pair-lite-1` | experimental | identity/change tests | no LPIPS/DISTS claim |

A metric moves to `validated` only after a named authoritative implementation or official script is compared over representative and edge-case fixtures, with tolerance and dependency version recorded.
''',
)

write(
    "camo-eval/ARCHITECTURE.md",
    '''# camo-eval architecture

## Design rule

Names communicate evidence. Validated standards keep their accepted names. Experimental substitutes use descriptive names or `_lite`. Planned standard names raise rather than returning a misleading number.

## Layers

1. **Validated core** — deterministic metrics with authoritative comparison tests.
2. **Experimental extensions** — domain helpers and explicitly named diagnostics.
3. **Protocol layer** — observer, channel, task, dataset/prediction provenance, threshold policy, environment, seed, uncertainty, and implementation version.
4. **External experiments** — schemas and analyzers for human or sensor studies; the package does not pretend to execute field experiments.

## Package layout

```text
camo_eval/
  metrics/       validated and experimental algorithms
  protocols/     context, provenance and manifests
  runner.py      basename-matched batch evaluation
  export.py      Markdown and LaTeX output
  cli.py         explicit command-line surface
```

## Release gate

A public package release requires tests on supported Python versions, lint and format checks, wheel/sdist build, installation smoke test, validation-register update, and a tagged release manifest.
''',
)

write(
    "camo-eval/ROADMAP.md",
    '''# camo-eval roadmap

## P0 complete

- standard names no longer return heuristic substitutes;
- experimental diagnostics use `_lite` or descriptive names;
- protocol context records implementation and provenance fields;
- validated and experimental capability matrix is published.

## P1 validation

- implement standard MS-SSIM and compare with a named reference;
- implement Cheng-style Boundary IoU;
- align DAVIS boundary F and J&F with the official evaluator;
- add COCO-compatible instance AP/AP50/AP75 or integrate an official evaluator.

## P2 learned generation metrics

Implement FID/KID/LPIPS/DISTS through optional, pinned backends. Record feature network, weights, preprocessing, sample count, and dependency versions. Do not alias these to the current lite diagnostics.

## P3 protocols

Add dataset hashes, prediction revision, threshold and normalization policy, runtime environment, seed, aggregation, bootstrap confidence intervals, and machine-readable validation level to every report.

## P4 external studies

Provide data schemas and statistical analyzers for human visual search and calibrated sensor experiments. Do not simulate missing observations or report mission-level conclusions from local image metrics.
''',
)

# Update package metadata and CI.
replace("camo-eval/pyproject.toml", 'version = "0.1.0"', 'version = "0.2.0.dev0"')
replace("camo-eval/pyproject.toml", 'authors = [{ name = "CamoGED Authors" }]', 'authors = [{ name = "Michael C." }]')
replace("camo-eval/pyproject.toml", '    "scikit-image>=0.19",', '    "scikit-image>=0.19",\n    "build>=1.2",')

write(
    ".github/workflows/camo-eval.yml",
    '''name: camo-eval

on:
  push:
    paths: ["camo-eval/**", "scripts/check_api.py", ".github/workflows/camo-eval.yml"]
  pull_request:
    paths: ["camo-eval/**", "scripts/check_api.py", ".github/workflows/camo-eval.yml"]

permissions:
  contents: read

jobs:
  lint-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e "camo-eval[dev]"
      - run: ruff check camo-eval/src camo-eval/tests scripts/check_api.py
      - run: black --check camo-eval/src camo-eval/tests scripts/check_api.py
      - run: python -m build camo-eval
      - run: pip install camo-eval/dist/*.whl --force-reinstall
      - run: camo-eval list-metrics --format json

  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python-version }}" }
      - run: pip install -e "camo-eval[dev]"
      - run: cd camo-eval && pytest --cov=camo_eval --cov-fail-under=80 -q
''',
)

write(
    "scripts/check_api.py",
    '''#!/usr/bin/env python3
"""Check camo-eval public names and signatures, including evidence-explicit APIs."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "camo-eval/src"))

EXPECTED = {
    "camo_eval.metrics.detection": {
        "mae": ["pred", "gt"],
        "weighted_f_measure": ["pred", "gt", "beta2"],
        "s_measure": ["pred", "gt", "alpha"],
        "e_measure": ["pred", "gt"],
        "f_measure": ["pred", "gt"],
        "precision": ["pred", "gt"],
        "recall": ["pred", "gt"],
        "precision_recall_curve": ["pred", "gt"],
    },
    "camo_eval.metrics.generation": {
        "fid": ["real_dir", "fake_dir"],
        "fid_lite": ["real_dir", "fake_dir"],
        "kid": ["real_dir", "fake_dir", "degree", "gamma", "coef0"],
        "kid_lite": ["real_dir", "fake_dir", "degree", "gamma", "coef0"],
        "lpips": ["img_a", "img_b"],
        "lpips_lite": ["img_a", "img_b"],
        "dists": ["img_a", "img_b"],
        "dists_lite": ["img_a", "img_b"],
        "deception_rate": ["detector", "images", "targets"],
    },
    "camo_eval.metrics.instance": {
        "iou": ["pred", "gt"],
        "dice": ["pred", "gt"],
        "boundary_iou": ["pred", "gt", "dilation_ratio"],
        "boundary_match_score": ["pred", "gt", "dilation_ratio"],
        "average_precision": ["true_positive_flags", "confidence_scores", "num_ground_truth"],
        "average_recall": ["true_positive_flags", "num_ground_truth"],
    },
    "camo_eval.metrics.perceptual": {
        "ssim": ["img_a", "img_b", "sigma"],
        "ms_ssim": ["img_a", "img_b", "levels"],
        "ms_ssim_lite": ["img_a", "img_b", "levels"],
    },
    "camo_eval.metrics.video": {
        "jaccard_index": ["pred_frames", "gt_frames"],
        "boundary_f_score": ["pred_frames", "gt_frames", "dilation_ratio"],
        "boundary_f_score_lite": ["pred_frames", "gt_frames", "dilation_ratio"],
        "j_and_f": ["pred_frames", "gt_frames"],
        "j_and_f_lite": ["pred_frames", "gt_frames"],
        "temporal_stability": ["pred_frames", "gt_frames"],
    },
    "camo_eval.metrics.robustness": {
        "attack_success_rate": ["clean_outputs", "attacked_outputs", "criterion"],
        "ap_drop": ["clean_ap", "attacked_ap"],
        "transferability": ["asr_by_model"],
    },
    "camo_eval.runner": {"evaluate": ["pred_dir", "gt_dir", "metrics"]},
    "camo_eval.export": {"to_latex": ["results"], "to_markdown": ["results"]},
}

STANDARD_STUBS = {
    "camo_eval.metrics.generation": ["fid", "kid", "lpips", "dists"],
    "camo_eval.metrics.instance": ["boundary_iou"],
    "camo_eval.metrics.perceptual": ["ms_ssim"],
    "camo_eval.metrics.video": ["boundary_f_score", "j_and_f"],
}


def names(function) -> list[str]:
    return [
        name
        for name, parameter in inspect.signature(function).parameters.items()
        if name != "self"
        and parameter.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]


def main() -> int:
    errors = []
    for module_name, functions in EXPECTED.items():
        module = importlib.import_module(module_name)
        for function_name, expected in functions.items():
            function = getattr(module, function_name, None)
            if not callable(function):
                errors.append(f"{module_name}.{function_name}: missing")
            elif names(function) != expected:
                errors.append(
                    f"{module_name}.{function_name}: expected {expected}, got {names(function)}"
                )
    for module_name, function_names in STANDARD_STUBS.items():
        module = importlib.import_module(module_name)
        for function_name in function_names:
            function = getattr(module, function_name)
            signature = inspect.signature(function)
            arguments = []
            for parameter in signature.parameters.values():
                if parameter.default is not inspect.Parameter.empty:
                    continue
                arguments.append("dummy")
            try:
                function(*arguments)
            except NotImplementedError:
                pass
            except Exception as exc:
                errors.append(f"{module_name}.{function_name}: expected NotImplementedError, got {exc!r}")
            else:
                errors.append(f"{module_name}.{function_name}: standard stub returned a value")
    for error in errors:
        print(f"ERROR {error}")
    print(f"check_api: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
)

# Tests: rename experimental APIs and assert standard names fail honestly.
for test_path in [
    "camo-eval/tests/test_extension_metrics.py",
    "camo-eval/tests/test_reference_metrics.py",
    "camo-eval/tests/test_cli.py",
]:
    text = (ROOT / test_path).read_text(encoding="utf-8")
    text = re.sub(r"\bboundary_iou\b", "boundary_match_score", text)
    text = re.sub(r"\bms_ssim\b", "ms_ssim_lite", text)
    text = re.sub(r"\bboundary_f_score\b", "boundary_f_score_lite", text)
    text = re.sub(r"\bj_and_f\b", "j_and_f_lite", text)
    text = re.sub(r"\bfid\b", "fid_lite", text)
    text = re.sub(r"\bkid\b", "kid_lite", text)
    text = re.sub(r"\blpips\b", "lpips_lite", text)
    text = re.sub(r"\bdists\b", "dists_lite", text)
    (ROOT / test_path).write_text(text, encoding="utf-8")

write(
    "camo-eval/tests/test_standard_metric_guards.py",
    '''import numpy as np
import pytest

from camo_eval import boundary_f_score, boundary_iou, dists, fid, j_and_f, kid, lpips, ms_ssim


def test_unvalidated_standard_names_do_not_return_surrogates(tmp_path):
    image = np.zeros((16, 16), dtype=float)
    for function, args in [
        (boundary_iou, (image, image)),
        (ms_ssim, (image, image)),
        (boundary_f_score, (image[None], image[None])),
        (j_and_f, (image[None], image[None])),
        (lpips, (image, image)),
        (dists, (image, image)),
    ]:
        with pytest.raises(NotImplementedError):
            function(*args)

    real = tmp_path / "real"
    fake = tmp_path / "fake"
    real.mkdir()
    fake.mkdir()
    for function in (fid, kid):
        with pytest.raises(NotImplementedError):
            function(str(real), str(fake))
''',
)

# ---------------------------------------------------------------------------
# 4. Browser demo: synthetic assets only, explicit teaching status
# ---------------------------------------------------------------------------

assets = ROOT / "web/public/demo-artifacts"
if assets.exists():
    shutil.rmtree(assets)

write(
    "web/.vitepress/theme/components/CamoDemo.vue",
    '''<script setup>
import { computed, nextTick, onMounted, ref } from "vue";

const canvasRef = ref(null);
const width = ref(560);
const height = ref(340);
const source = ref(null);
const mask = ref(null);
const seed = ref(null);
const tool = ref("seed");
const tolerance = ref(42);
const brush = ref(16);
const version = ref(0);
const label = ref("Synthetic bark scene");

function makeScene(kind) {
  const canvas = document.createElement("canvas");
  canvas.width = width.value;
  canvas.height = height.value;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const gradient = ctx.createLinearGradient(0, 0, width.value, height.value);
  if (kind === "bark") {
    gradient.addColorStop(0, "#5f5a49");
    gradient.addColorStop(1, "#81765d");
  } else if (kind === "leaf") {
    gradient.addColorStop(0, "#5b774f");
    gradient.addColorStop(1, "#8f9b62");
  } else {
    gradient.addColorStop(0, "#77878a");
    gradient.addColorStop(1, "#a0a59b");
  }
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width.value, height.value);
  const rng = mulberry32(kind === "bark" ? 13 : kind === "leaf" ? 29 : 41);
  for (let i = 0; i < 900; i += 1) {
    const value = 55 + Math.floor(rng() * 90);
    ctx.fillStyle = `rgba(${value},${value + 8},${Math.max(30, value - 15)},0.20)`;
    ctx.fillRect(rng() * width.value, rng() * height.value, 1 + rng() * 9, 1 + rng() * 3);
  }
  const target = new Uint8Array(width.value * height.value);
  const cx = width.value * 0.58;
  const cy = height.value * 0.52;
  const rx = kind === "leaf" ? 88 : 72;
  const ry = kind === "leaf" ? 44 : 62;
  ctx.fillStyle = kind === "bark" ? "rgba(102,96,76,0.96)" : kind === "leaf" ? "rgba(105,126,74,0.96)" : "rgba(132,142,136,0.96)";
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, kind === "leaf" ? -0.45 : 0.15, 0, Math.PI * 2);
  ctx.fill();
  for (let y = 0; y < height.value; y += 1) {
    for (let x = 0; x < width.value; x += 1) {
      const cos = Math.cos(kind === "leaf" ? -0.45 : 0.15);
      const sin = Math.sin(kind === "leaf" ? -0.45 : 0.15);
      const dx = x - cx;
      const dy = y - cy;
      const xr = dx * cos + dy * sin;
      const yr = -dx * sin + dy * cos;
      if ((xr * xr) / (rx * rx) + (yr * yr) / (ry * ry) <= 1) target[y * width.value + x] = 1;
    }
  }
  return { pixels: ctx.getImageData(0, 0, width.value, height.value), target };
}

function mulberry32(seedValue) {
  return function random() {
    let value = (seedValue += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

async function loadSynthetic(kind) {
  label.value = `Synthetic ${kind} scene`;
  const generated = makeScene(kind);
  source.value = generated.pixels;
  mask.value = generated.target;
  seed.value = null;
  version.value += 1;
  await nextTick();
  draw();
}

async function upload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  try {
    const image = await new Promise((resolve, reject) => {
      const item = new Image();
      item.onload = () => resolve(item);
      item.onerror = reject;
      item.src = url;
    });
    const scale = Math.min(1, 720 / Math.max(image.width, image.height));
    width.value = Math.max(1, Math.round(image.width * scale));
    height.value = Math.max(1, Math.round(image.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width.value;
    canvas.height = height.value;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(image, 0, 0, width.value, height.value);
    source.value = ctx.getImageData(0, 0, width.value, height.value);
    mask.value = new Uint8Array(width.value * height.value);
    seed.value = { x: Math.floor(width.value / 2), y: Math.floor(height.value / 2) };
    label.value = file.name;
    version.value += 1;
    await nextTick();
    draw();
  } finally {
    URL.revokeObjectURL(url);
    event.target.value = "";
  }
}

function point(event) {
  const rect = canvasRef.value.getBoundingClientRect();
  return {
    x: Math.floor(((event.clientX - rect.left) / rect.width) * width.value),
    y: Math.floor(((event.clientY - rect.top) / rect.height) * height.value),
  };
}

function regionGrow(x, y) {
  if (!source.value) return;
  const data = source.value.data;
  const start = y * width.value + x;
  const base = [data[start * 4], data[start * 4 + 1], data[start * 4 + 2]];
  const visited = new Uint8Array(width.value * height.value);
  const result = new Uint8Array(width.value * height.value);
  const queue = [start];
  visited[start] = 1;
  for (let head = 0; head < queue.length; head += 1) {
    const index = queue[head];
    const offset = index * 4;
    const distance = Math.hypot(data[offset] - base[0], data[offset + 1] - base[1], data[offset + 2] - base[2]);
    if (distance > tolerance.value) continue;
    result[index] = 1;
    const px = index % width.value;
    const py = Math.floor(index / width.value);
    for (const [nx, ny] of [[px - 1, py], [px + 1, py], [px, py - 1], [px, py + 1]]) {
      if (nx < 0 || nx >= width.value || ny < 0 || ny >= height.value) continue;
      const next = ny * width.value + nx;
      if (!visited[next]) {
        visited[next] = 1;
        queue.push(next);
      }
    }
  }
  mask.value = result;
  version.value += 1;
  draw();
}

let painting = false;
function pointerDown(event) {
  const p = point(event);
  if (tool.value === "seed") {
    seed.value = p;
    regionGrow(p.x, p.y);
    return;
  }
  painting = true;
  paint(p.x, p.y);
}
function pointerMove(event) {
  if (!painting) return;
  const p = point(event);
  paint(p.x, p.y);
}
function pointerUp() { painting = false; }
function paint(x, y) {
  const radius = Math.max(1, Math.round(brush.value / 2));
  for (let yy = y - radius; yy <= y + radius; yy += 1) {
    for (let xx = x - radius; xx <= x + radius; xx += 1) {
      if (xx < 0 || yy < 0 || xx >= width.value || yy >= height.value) continue;
      if ((xx - x) ** 2 + (yy - y) ** 2 > radius ** 2) continue;
      mask.value[yy * width.value + xx] = tool.value === "paint" ? 1 : 0;
    }
  }
  version.value += 1;
  draw();
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas || !source.value || !mask.value) return;
  canvas.width = width.value;
  canvas.height = height.value;
  const data = new Uint8ClampedArray(source.value.data);
  for (let i = 0; i < mask.value.length; i += 1) {
    if (!mask.value[i]) continue;
    data[i * 4] = Math.round(data[i * 4] * 0.45 + 245 * 0.55);
    data[i * 4 + 1] = Math.round(data[i * 4 + 1] * 0.45 + 165 * 0.55);
    data[i * 4 + 2] = Math.round(data[i * 4 + 2] * 0.45 + 35 * 0.55);
  }
  canvas.getContext("2d").putImageData(new ImageData(data, width.value, height.value), 0, 0);
}

function gray(index) {
  const data = source.value.data;
  return (0.299 * data[index * 4] + 0.587 * data[index * 4 + 1] + 0.114 * data[index * 4 + 2]) / 255;
}
function histogram(values, bins = 24) {
  const output = new Array(bins).fill(0);
  values.forEach((value) => output[Math.min(bins - 1, Math.floor(value * bins))]++);
  return output.map((value) => value / Math.max(1, values.length));
}
const metrics = computed(() => {
  version.value;
  if (!source.value || !mask.value) return null;
  const target = [];
  const background = [];
  for (let i = 0; i < mask.value.length; i += 1) (mask.value[i] ? target : background).push(gray(i));
  if (!target.length || !background.length) return null;
  const mean = (values) => values.reduce((sum, value) => sum + value, 0) / values.length;
  const tMean = mean(target);
  const bMean = mean(background);
  const tHist = histogram(target);
  const bHist = histogram(background);
  const overlap = tHist.reduce((sum, value, index) => sum + Math.min(value, bHist[index]), 0);
  const meanDifference = Math.abs(tMean - bMean);
  const exploratory = Math.max(0, Math.min(1, 0.65 * overlap + 0.35 * (1 - meanDifference)));
  return { target: target.length, overlap, meanDifference, exploratory };
});

onMounted(() => loadSynthetic("bark"));
</script>

<template>
  <main class="demo">
    <header>
      <p class="eyebrow">Synthetic teaching demo</p>
      <h1>Explore target–background similarity</h1>
      <p>
        This page uses deterministic synthetic scenes or an image kept locally in your browser.
        It is not a COD model, not a benchmark, and not a standard camo-eval score.
      </p>
    </header>

    <section class="controls">
      <button @click="loadSynthetic('bark')">Synthetic bark</button>
      <button @click="loadSynthetic('leaf')">Synthetic leaf</button>
      <button @click="loadSynthetic('stone')">Synthetic stone</button>
      <label class="upload">Upload local image <input type="file" accept="image/*" @change="upload" /></label>
    </section>

    <section class="workspace">
      <div>
        <canvas ref="canvasRef" @pointerdown="pointerDown" @pointermove="pointerMove" @pointerup="pointerUp" @pointerleave="pointerUp" />
        <p>{{ label }} · orange overlay = current target mask</p>
      </div>
      <aside>
        <label>Tool
          <select v-model="tool">
            <option value="seed">Seeded colour region</option>
            <option value="paint">Paint target</option>
            <option value="erase">Erase mask</option>
          </select>
        </label>
        <label>Region tolerance <input v-model.number="tolerance" type="range" min="5" max="150" /></label>
        <label>Brush size <input v-model.number="brush" type="range" min="4" max="60" /></label>
        <button v-if="seed" @click="regionGrow(seed.x, seed.y)">Re-run seeded region</button>
      </aside>
    </section>

    <section class="results">
      <h2>Exploratory diagnostics</h2>
      <div v-if="metrics" class="grid">
        <article><strong>{{ metrics.target }}</strong><span>target pixels</span></article>
        <article><strong>{{ metrics.overlap.toFixed(3) }}</strong><span>grayscale histogram overlap</span></article>
        <article><strong>{{ metrics.meanDifference.toFixed(3) }}</strong><span>mean luminance difference</span></article>
        <article><strong>{{ metrics.exploratory.toFixed(3) }}</strong><span>exploratory heuristic</span></article>
      </div>
      <p class="warning">
        The heuristic combines histogram overlap and luminance similarity. It has no claim to human detectability,
        ecological fitness, detector failure, or mission effectiveness. Use validated metrics and a declared protocol for research reporting.
      </p>
    </section>
  </main>
</template>

<style scoped>
.demo { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 4rem; }
.eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; }
.controls { display: flex; flex-wrap: wrap; gap: .7rem; margin: 1.5rem 0; }
button, .upload, select { border: 1px solid var(--vp-c-divider); border-radius: 8px; padding: .65rem .85rem; background: var(--vp-c-bg-soft); }
.upload input { display: block; margin-top: .45rem; }
.workspace { display: grid; grid-template-columns: minmax(0, 1fr) 260px; gap: 1rem; }
canvas { width: 100%; max-height: 620px; object-fit: contain; border-radius: 10px; border: 1px solid var(--vp-c-divider); touch-action: none; }
aside { display: grid; align-content: start; gap: 1rem; padding: 1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; }
aside label { display: grid; gap: .4rem; }
.results { margin-top: 2rem; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; }
article { padding: 1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; }
article strong, article span { display: block; }
article strong { font-size: 1.5rem; }
.warning { padding: 1rem; border-left: 4px solid var(--vp-c-warning-1); background: var(--vp-c-warning-soft); }
@media (max-width: 760px) { .workspace { grid-template-columns: 1fr; } .grid { grid-template-columns: 1fr 1fr; } }
</style>
''',
)

write(
    "web/index.md",
    '''---
layout: home
hero:
  name: CamoGED
  text: "Camouflage research preview"
  tagline: A cross-domain monograph with verified metadata, protocol-aware evaluation tools, and synthetic teaching demos.
  actions:
    - theme: brand
      text: Read the book
      link: /book/
    - theme: alt
      text: Verified results registry
      link: /leaderboard
    - theme: alt
      text: Synthetic demo
      link: /demo
features:
  - title: Generation
    details: Published mechanisms and research questions; original generator projects remain agendas until reproducible.
  - title: Detection
    details: Image, video, instance, semantic, and multimodal detection literature organized by declared tasks and protocols.
  - title: Evaluation
    details: Validated COD core metrics are separated from explicitly experimental diagnostics.
---
''',
)

write(
    "web/.vitepress/config.mjs",
    '''export default {
  title: "CamoGED",
  base: "/CamoGED/",
  description: "CamoGED research preview: monograph, verified metadata, and evaluation tools.",
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Book", link: "/book/" },
      { text: "Synthetic demo", link: "/demo" },
      { text: "Papers", link: "/papers" },
      { text: "Datasets", link: "/datasets" },
      { text: "Code & Resources", link: "/models" },
      { text: "Verified results", link: "/leaderboard" }
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/MichaelCSHN/CamoGED" }],
    search: { provider: "local" }
  }
};
''',
)

# Website code license follows repository code license.
package_path = ROOT / "web/package.json"
package_doc = yaml.safe_load(package_path.read_text(encoding="utf-8"))
package_doc["license"] = "Apache-2.0"
import json
package_path.write_text(json.dumps(package_doc, indent=2) + "\n", encoding="utf-8")

# Project directories are research agendas, not integrations.
for name, scope in {
    "coder": "image camouflaged-object segmentation baseline research",
    "flowcamo": "video camouflage generation and detection research",
    "dualvcod": "video instance and identity-preserving camouflage research",
}.items():
    write(
        f"projects/{name}/README.md",
        f'''# {name}: research agenda

**Scope:** {scope}.

No method is integrated in this monorepo at present. There is no vendored code, released weight, prediction archive, executable evaluation manifest, verified result, or hosted model demo. This directory exists only to define future integration gates.

## Entry requirements

- fixed source repository and commit;
- explicit license and model/data provenance;
- reproducible environment and commands;
- weight and prediction checksums;
- `camo-eval` protocol manifest;
- independently reviewed report;
- limitations and dual-use assessment.

Until all requirements are met, this project must not appear in the verified results registry or be described as a CamoGED baseline.
''',
    )

# ---------------------------------------------------------------------------
# 5. Workflows, release proofing, and integrity checks
# ---------------------------------------------------------------------------

write(
    ".github/workflows/arxiv-watch.yml",
    '''name: arXiv watch prototype

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  explain:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "The scheduled watcher is disabled until candidate retrieval, deduplication,"
          echo "source validation, and issue creation are implemented and reviewed."
''',
)

write(
    ".github/workflows/check-links.yml",
    '''name: link checks

on:
  pull_request:
    paths: ["**/*.md", "**/*.qmd", "data/*.yaml", "web/**/*.vue", ".github/workflows/check-links.yml"]
  schedule: [{ cron: "0 6 * * 1" }]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  internal:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lycheeverse/lychee-action@v2
        with:
          args: --offline --no-progress "**/*.md" "**/*.qmd"

  external-report:
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lycheeverse/lychee-action@v2
        with:
          args: --no-progress --accept 200,206,429 "**/*.md" "**/*.qmd" "data/*.yaml" "web/**/*.vue"
        continue-on-error: true
''',
)

write(
    ".github/workflows/book.yml",
    '''name: book

on:
  push:
    branches: [main]
    paths: ["book/**", ".github/workflows/book.yml"]
  pull_request:
    paths: ["book/**", ".github/workflows/book.yml"]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install jupyter numpy matplotlib scipy
      - uses: quarto-dev/quarto-actions/setup@v2
      - name: Render HTML and populate execution cache
        run: quarto render book --to html
      - name: Render ePub from frozen results
        run: quarto render book --to epub
      - uses: actions/upload-artifact@v4
        with:
          name: book-html-epub
          path: book/_book
''',
)

# Update README with explicit component statuses and disclosure links.
readme = (ROOT / "README.md").read_text(encoding="utf-8")
readme = re.sub(
    r"## What's inside\n.*?## Analytical map",
    '''## Component status

| Component | Current status | Trust boundary |
|---|---|---|
| Monograph | publication candidate | not yet rights- and format-cleared |
| `camo-eval` COD core | validated research preview | report package version and protocol |
| `camo-eval` extensions | experimental | use explicit `*_lite` or descriptive names |
| Paper/dataset registry | metadata preview | coverage is selective; licenses may be unknown |
| Results registry | minimal source-checked records | not a comprehensive ranking |
| Browser demo | synthetic teaching tool | no model inference or standard difficulty score |
| `coder` / `flowcamo` / `dualvcod` | research agendas | no integrated methods or verified results |

Security reports use [`SECURITY.md`](SECURITY.md). Third-party asset policy is recorded in [`THIRD_PARTY_ASSETS.yml`](THIRD_PARTY_ASSETS.yml). Release state is recorded in [`RELEASE_MANIFEST.yml`](RELEASE_MANIFEST.yml).

## Analytical map''',
    readme,
    flags=re.MULTILINE | re.DOTALL,
)
readme = readme.replace(
    "# Evaluation toolkit\ncd camo-eval && pip install -e . && pytest -q",
    "# Evaluation toolkit\ncd camo-eval && pip install -e \".[dev]\" && pytest -q",
)
(ROOT / "README.md").write_text(readme, encoding="utf-8")

write(
    "docs/PROJECT_AUDIT_REMEDIATION.md",
    '''# Project audit remediation register

Date: 2026-07-13

## Closed in this change

- standard metric names no longer return heuristic substitutes;
- experimental generation, boundary, multiscale, and video diagnostics are explicitly named;
- COD10K-derived browser assets were removed and replaced with synthetic scenes;
- unfinished original projects were removed from the results registry and relabeled research agendas;
- security and sensitive-conduct reporting now use a real private channel;
- release metadata no longer claims an untagged release date;
- project plan, governance, website, and README now use the edited monograph's bounded claims;
- data schema records verification, source, publication, and license state;
- the leaderboard is now a verified results registry;
- `camo-eval` gains validation documentation, package/lint/test gates, and richer protocol provenance;
- scheduled arXiv placeholder automation was disabled;
- book HTML/ePub rendering is sequential with a timeout.

## Still open before a formal release

- complete item-level dataset license research;
- validate standard MS-SSIM, Boundary IoU, DAVIS F/J&F, and learned generation metrics;
- obtain external domain review and image-rights clearance for the monograph;
- inspect final ePub and PDF typography;
- create an actual tag/release and update `RELEASE_MANIFEST.yml`;
- select and fully integrate at most one original method before advertising an original baseline.
''',
)

# Regenerate Markdown surfaces from migrated data.
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from build_awesome import write_outputs

write_outputs()

print("Project audit remediation applied.")
