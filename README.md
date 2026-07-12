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

CamoGED brings camouflage **generation, detection, and evaluation** into one open research environment,
with natural-science, military, visual-culture, and machine-perception perspectives represented across
physical, digital, and learning-based settings. The project combines a living monograph, curated metadata,
reproducible evaluation tools, and research demos. Claims of novelty or comprehensive coverage are treated
as versioned literature-search conclusions rather than permanent promotional facts; see
[`docs/BOOK_SEARCH_METHODOLOGY.md`](docs/BOOK_SEARCH_METHODOLOGY.md).

## What's inside

| Component | Path | Description |
|-----------|------|-------------|
| 📚 **Monograph** | [`book/`](book/) | *Camouflage: Generation, Detection, and Evaluation*; HTML is CI-gated, while PDF/ePub require format-specific proofing |
| 🌟 **Awesome list** | [`awesome/`](awesome/README.md) | Curated cross-domain resources backed by machine-readable metadata |
| 🌐 **Website** | [`web/`](web/) | Aggregator for papers, datasets, leaderboard entries, and demos |
| 🔧 **camo-eval** | [`camo-eval/`](camo-eval/) | Evaluation toolkit for detection, generation, robustness, and protocol reporting |
| 🔬 **Research agendas** | [`projects/`](projects/) | Work-in-progress anchors: `coder`, `flowcamo`, and `dualvcod`; not presented as completed methods until verified |
| 🗂️ **Shared data** | [`data/`](data/) | Single source of truth for papers, datasets, and leaderboard metadata |

## Analytical map

```text
                  Hide–reveal interaction                  ← working framework
   ┌──────────────────────────┼──────────────────────────┐
 Nature                 Military systems           Visual culture
   └──────────────────────────┼──────────────────────────┘
             Physical ── Digital ── Learning-based       ← settings
   ┌──────────────────────────┼──────────────────────────┐
 Generation                 Detection                Evaluation
  (hider)                    (seeker)              (protocol/judge)
```

The map is an organizing framework, not a claim that all four domains share identical mechanisms or a
single solved game-theoretic model.

## Quick start

```bash
# Clone
git clone https://github.com/MichaelCSHN/CamoGED.git && cd CamoGED

# Evaluation toolkit
cd camo-eval && pip install -e . && pytest -q

# Book (requires Quarto)
cd book && quarto preview

# Website (requires Node 18+)
cd web && npm install && npm run docs:dev
```

## Roadmap

Build the slow-changing pieces first, the fast-iterating ones last:
**① repository foundation → ② monograph and evaluation contracts → ③ curated metadata → ④ website and demos.**

- **Foundation:** governance, licenses, CI, metadata schemas, and `camo-eval` core.
- **Monograph:** editorially controlled chapters, fact-check register, executable examples, and publication proofing.
- **Metadata:** verified papers, datasets, and protocol-aware leaderboard entries.
- **Demos:** stable evaluation demos first; heavier generation or model demos only after reproducibility and risk review.
- **Publication:** archive a reviewed release, then add DOI and publisher/companion-paper metadata.

Full plan: [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) · Book compilation plan: [`docs/BOOK_COMPILATION_PLAN.md`](docs/BOOK_COMPILATION_PLAN.md).

## Contributing

We welcome papers, datasets, methods, demos, and corrections. See [`CONTRIBUTING.md`](CONTRIBUTING.md)
and use the structured issue templates. Please also read our [Code of Conduct](CODE_OF_CONDUCT.md).

## Responsible use

CamoGED covers military camouflage and adversarial attacks. All such content is provided for **understanding,
defense, and robustness evaluation**. We do **not** publish directly weaponizable recipes. See [`ETHICS.md`](ETHICS.md).

## Citing

If CamoGED helps your work, please cite it via [`CITATION.cff`](CITATION.cff). A DOI will be added only after
a reviewed release is archived in a DOI-minting repository.

## Acknowledgements

CamoGED builds on and links to prior community work, including the Awesome lists by
[visionxiang](https://github.com/visionxiang/awesome-camouflaged-object-detection),
[ChunmingHe](https://github.com/ChunmingHe/awesome-concealed-object-segmentation),
[clelouch](https://github.com/clelouch/Awesome-Camouflaged-Object-Detection),
and the 2024 survey *A Survey of Camouflaged Object Detection and Beyond*.

## License

Code is licensed under [Apache-2.0](LICENSE). Prose content (book, Awesome list, docs) is licensed under
[CC-BY-4.0](LICENSE-CONTENT). Datasets are **linked, not redistributed**; respect each dataset's upstream license.
