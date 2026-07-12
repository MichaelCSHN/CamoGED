<div align="center">

# 🦎 CamoGED

### Platform pillars: **G**eneration · **E**valuation · **D**etection

*A cross-domain open platform for the science, art, and engineering of concealment —
spanning **Nature · War · Machines** and the **Physical · Digital · Intelligent** domains.*

[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC--BY--4.0-lightgrey.svg)](LICENSE-CONTENT)
[![Awesome](https://awesome.re/badge.svg)](awesome/README.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

> **Working thesis.** Camouflage can be studied as an observer-, channel-, and task-dependent
> interaction between a **hider** and a **seeker**, with evaluation defining what counts as success.
> Biology, military engineering, visual culture, and AI share parts of this analytical structure,
> while retaining different mechanisms, histories, constraints, and utility functions.

CamoGED is the first open resource to **simultaneously** cover camouflage **generation, evaluation, and detection**,
across the **natural-science, military, and humanities/art** perspectives, and the **physical, digital, and
intelligent** technical domains. Existing resources cover only detection and are static lists; CamoGED adds the
missing generation and evaluation pillars, the cross-domain narrative, and a *living* platform (leaderboard +
demos + a unified evaluation toolkit).

## What's inside

| Component | Path | Description |
|-----------|------|-------------|
| 📚 **Monograph** | [`book/`](book/) | *Camouflage: Generation, Detection, and Evaluation*; HTML is CI-gated, while PDF/ePub remain release outputs requiring format-specific proofing |
| 🌟 **Awesome list** | [`awesome/`](awesome/README.md) | Curated cross-domain resources (machine-readable) |
| 🌐 **Website** | [`web/`](web/) | Aggregator: papers, model zoo, leaderboard, demos, datasets |
| 🔧 **camo-eval** | [`camo-eval/`](camo-eval/) | Unified toolkit: detection accuracy · generation quality · adversarial robustness |
| 🔬 **Projects** | [`projects/`](projects/) | Original anchors: `coder`, `flowcamo`, `dualvcod` |
| 🗂️ **Shared data** | [`data/`](data/) | Single source of truth (`papers.yaml`, `datasets.yaml`, `leaderboard.yaml`) consumed by both the Awesome list and the website |

## The map

```
                  Co-evolutionary game (hide ⇄ seek)        ← unifying thesis
   ┌──────────────────────────┼──────────────────────────┐
 Nature                      War                        Art          ← three perspectives
   └──────────────────────────┼──────────────────────────┘
                Physical ── Digital ── Intelligent                   ← three domains
   ┌──────────────────────────┼──────────────────────────┐
 Generation                Evaluation                Detection      ← three pillars
  (the hider)              (the judge)                (the seeker)
      │                        │                          │
   flowcamo                 coder                     camo-eval
                            dualvcod
```

## Quick start

```bash
# Clone
git clone https://github.com/MichaelCSHN/CamoGED.git && cd CamoGED

# Evaluation toolkit (core COD, boundary, video, perceptual and signature metrics are implemented; heavy generation metrics remain optional)
cd camo-eval && pip install -e . && pytest -q

# Book (requires Quarto: https://quarto.org)
cd book && quarto preview

# Website (requires Node 18+)
cd web && npm install && npm run docs:dev
```

## Roadmap (stability-first order)

Build the slow-changing pieces first, the fast-iterating ones last:
**① repo scaffold → ② monograph → ③ Awesome list → ④ website.**

- **Phase 0 — Repo foundation:** scaffold, governance, licenses, CI, `data/` schema, `camo-eval` skeleton ✅
- **Phase 1 — Monograph:** Part I + Evaluation part + thesis chapter first; `camo-eval` metrics; online `v0.5`.
- **Phase 2 — Awesome list:** distilled from the book's bibliography into `data/*.yaml`; auto-updates via Actions.
- **Phase 3 — Website:** leaderboard + demos (image → video → instance), consuming `data/*.yaml`.
- **Phase 4 — Publication & community:** finalize book, submit to publisher + companion paper, Zenodo DOI.

Full plan: [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) · Book compilation plan: [`docs/BOOK_COMPILATION_PLAN.md`](docs/BOOK_COMPILATION_PLAN.md).

## Contributing

We welcome papers, datasets, methods, demos, and corrections. See [`CONTRIBUTING.md`](CONTRIBUTING.md)
and use the structured issue templates. Please also read our [Code of Conduct](CODE_OF_CONDUCT.md).

## Responsible use (dual-use notice)

CamoGED covers military camouflage and adversarial attacks. All such content is provided for **understanding,
defense, and robustness evaluation**. We do **not** publish directly weaponizable recipes. See [`ETHICS.md`](ETHICS.md).

## Citing

If CamoGED helps your work, please cite it via [`CITATION.cff`](CITATION.cff). A DOI will be added when a release is archived in a DOI-minting repository.

## Acknowledgements

CamoGED builds on and links to prior community work, including the Awesome lists by
[visionxiang](https://github.com/visionxiang/awesome-camouflaged-object-detection),
[ChunmingHe](https://github.com/ChunmingHe/awesome-concealed-object-segmentation),
[clelouch](https://github.com/clelouch/Awesome-Camouflaged-Object-Detection),
and the 2024 survey *A Survey of Camouflaged Object Detection and Beyond*.

## License

Code is licensed under [Apache-2.0](LICENSE). Prose content (book, Awesome list, docs) is licensed under
[CC-BY-4.0](LICENSE-CONTENT). Datasets are **linked, not redistributed**; respect each dataset's upstream license.
