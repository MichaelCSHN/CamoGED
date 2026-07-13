# CamoGED v0.2 Research Preview — Project Plan

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
