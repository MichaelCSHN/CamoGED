<div align="center">

# 🦎 CamoGED

### Camouflage: **G**eneration · **E**valuation · **D**etection

*A cross-domain open platform for the science, art, and engineering of concealment —
spanning **Nature · War · Machines** and the **Physical · Digital · Intelligent** domains.*

[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC--BY--4.0-lightgrey.svg)](LICENSE-CONTENT)
[![Awesome](https://awesome.re/badge.svg)](awesome/README.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

> **Thesis.** Camouflage is a *co-evolutionary arms race* between a **hider** and a **seeker**.
> The same structure recurs across biology (prey vs. predator), the military (measure vs. counter‑measure),
> art (image vs. perception), and AI (generator vs. discriminator / attacker vs. detector).
> CamoGED treats **generation** (hiding), **detection** (seeking), and **evaluation** (judging) as the three
> faces of this single game — and unifies them into one living research platform.

CamoGED is the first open resource to **simultaneously** cover camouflage **generation, detection, and evaluation**,
across the **natural-science, military, and humanities/art** perspectives, and the **physical, digital, and
intelligent** technical domains. Existing resources cover only detection and are static lists; CamoGED adds the
missing generation and evaluation pillars, the cross-domain narrative, and a *living* platform (leaderboard +
demos + a unified evaluation toolkit).

## What's inside

| Component | Path | Description |
|-----------|------|-------------|
| 📚 **Monograph** | [`book/`](book/) | The book *Camouflage: Generation, Detection & Evaluation* (Quarto → HTML/PDF/ePub) |
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
 Generation                Detection                 Evaluation      ← three pillars
  (the hider)              (the seeker)               (the judge)
      │                        │                          │
   flowcamo                 coder                     camo-eval
                            dualvcod
```

## Quick start

```bash
# Clone
git clone https://github.com/MichaelCSHN/CamoGED.git && cd CamoGED

# Evaluation toolkit (one working metric ships now: MAE; others scaffolded)
cd camo-eval && pip install -e . && pytest -q

# Book (requires Quarto: https://quarto.org)
cd book && quarto preview

# Website (requires Node 18+)
cd web && npm install && npm run docs:dev
```

## Roadmap (high level)

- **Phase 1 — Foundation:** org/repo scaffold ✅, Awesome v0.5, `camo-eval` detection metrics, website skeleton, Ch.1 + Evaluation outline.
- **Phase 2 — Expansion:** Part I + Evaluation chapter, `coder` demo + leaderboard, datasets page.
- **Phase 3 — Deepening:** Generation + Detection parts, `flowcamo`/`dualvcod` demos, automated Awesome updates, bilingual alignment.
- **Phase 4 — Publication:** finalize book, submit to publisher + companion survey paper, Zenodo DOI, community.

Full plan: [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).

## Contributing

We welcome papers, datasets, methods, demos, and corrections. See [`CONTRIBUTING.md`](CONTRIBUTING.md)
and use the structured issue templates. Please also read our [Code of Conduct](CODE_OF_CONDUCT.md).

## Responsible use (dual-use notice)

CamoGED covers military camouflage and adversarial attacks. All such content is provided for **understanding,
defense, and robustness evaluation**. We do **not** publish directly weaponizable recipes. See [`ETHICS.md`](ETHICS.md).

## Citing

If CamoGED helps your work, please cite it via [`CITATION.cff`](CITATION.cff) (a versioned DOI is minted on each release).

## Acknowledgements

CamoGED builds on and links to prior community work, including the Awesome lists by
[visionxiang](https://github.com/visionxiang/awesome-camouflaged-object-detection),
[ChunmingHe](https://github.com/ChunmingHe/awesome-concealed-object-segmentation),
[clelouch](https://github.com/clelouch/Awesome-Camouflaged-Object-Detection),
and the 2024 survey *A Survey of Camouflaged Object Detection and Beyond*.

## License

Code is licensed under [Apache-2.0](LICENSE). Prose content (book, Awesome list, docs) is licensed under
[CC-BY-4.0](LICENSE-CONTENT). Datasets are **linked, not redistributed**; respect each dataset's upstream license.
