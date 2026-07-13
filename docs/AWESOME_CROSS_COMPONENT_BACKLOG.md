# Awesome cross-component follow-ups — closure record

**Status: CLOSED — 2026-07-13**

This record documents the items discovered during the Awesome specialist audit and the concrete implementation that closed each item. Future literature changes are handled through the normal fact-check and release process rather than reopening the original backlog implicitly.

## Book

| Item | Resolution | Evidence |
|---|---|---|
| Explain curated Awesome vs complete Catalog | Appendix A now defines three layers: curated map, accepted metadata Catalog, and book citations | `book/chapters/appendix-resources.qmd` |
| Expand Chapter 10 task map | Rebuilt as task/supervision/modality axes, including bbox RCOD, tracking, incomplete supervision, zero-shot/open-vocabulary, VLM and robustness | `book/chapters/10-intelligent-overview-datasets.qmd` |
| Review 2025–2026 foundation-model literature | Added source-checked CamSAM2, MMCSBench and SDDF discussion, while keeping dynamic candidates outside the book | `book/chapters/14-foundation-models.qmd` |
| Prevent Catalog-to-bibliography auto-copy | Appendix and search methodology explicitly require editorial adoption and primary-source review | `docs/BOOK_SEARCH_METHODOLOGY.md` |
| Periodically reassess “first/largest/latest” | Added F15 and release-time dynamic-catalog review requirement | `docs/BOOK_FACTCHECK_REGISTER.md` |
| Remove unsupported cross-domain foundation-model claim | Recast as a testable hypothesis with zero/few/full-supervision comparison requirements | F18 and Chapter 14.7 |
| Remove residual dynamic overclaims | Replaced unsupported “fact standard”, priority, dataset-superiority, fixed adapter-ratio and universal-stability wording with protocol-bounded statements | Chapters 10 and 14; `scripts/check_cross_component.py` |

## Demo

| Item | Resolution | Evidence |
|---|---|---|
| Keep Demo synthetic and local | Page states local browser handling and no model-inference claim | `web/demo.md`, `CamoDemo.vue` |
| Link Catalog and metric validation | Added direct links and research-reporting boundary | `web/demo.md` |
| Define real-model integration gate | Added code/weight provenance, version, license, input/output, privacy and safety requirements | `web/demo.md` |

## Website

| Item | Resolution | Evidence |
|---|---|---|
| Multi-axis Catalog filtering | Generated JSON + client-side accessible filters with static fallback | `web/public/catalog.json`, `CatalogExplorer.vue` |
| Public latest automated scan status | Read-only client widget fetches the latest public `awesome:triage` issue with session cache and failure fallback | `AwesomeScanStatus.vue`, `/updates` |
| Explain Awesome/Catalog split at project root | Root component-status table and policy note updated | `README.md` |

## Enforcement

`scripts/check_cross_component.py` and the Contracts workflow block regressions in the book taxonomy, references, dynamic-claim wording, Demo boundary, interactive Catalog data, scan widget, README distinction and closure status.

Final acceptance is evaluated on the permanent branch contents only: no one-shot workflows, rendered-book caches, validation logs or other migration artifacts belong in the pull request. The required release-facing checks are Contracts, internal links, VitePress/Web, and Book HTML/ePub rendering.