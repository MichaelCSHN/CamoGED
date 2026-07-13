# Awesome remediation: cross-component follow-up status

This register tracks findings discovered during the Awesome specialist remediation that affect other CamoGED components.

## Completed in PR #12

### Book

1. **Completed:** `book/chapters/appendix-resources.qmd` now explains the curated Awesome / complete Catalog split and the multi-axis metadata extension.
2. **Completed:** Chapter 10 now records bbox RCOD, tracking, incomplete supervision, zero-shot/open-vocabulary, VLM, multimodal, and robustness as distinct protocol facets.
3. **Completed with evidence boundary:** Chapter 14 now contains a versioned 2025–2026 foundation-model literature window. Metadata-only Catalog inclusion does not become a formal citation automatically.
4. **Intentionally retained rule:** `book/references.bib` contains only resources actually cited after bibliographic verification; it is not synchronized wholesale from the Catalog.
5. **Completed:** `docs/BOOK_FACTCHECK_REGISTER.md` now requires periodic rechecking of “first”, “largest”, “latest”, and SOTA claims against current primary sources and the Catalog review cutoff.

### Demo

1. **Completed and retained:** the browser demo remains a deterministic synthetic teaching tool. No newly discovered model or dataset is connected automatically.
2. **Completed:** the Demo explanation links to the Research Catalog and the camo-eval validation register.
3. **Completed as a gate:** future model-backed demos require fixed code and weight provenance, an explicit license, an evaluation manifest, and an independently reviewable report. Awesome inclusion is not reproduction evidence.

### Website outside Awesome

1. **Completed:** the Resources navigation now distinguishes Awesome, Research Catalog, Update status, Datasets, Code & Resources, and Verified Results.
2. **Completed:** the Catalog has a client-side search and multi-axis filter for task, modality, and context. The accepted metadata model remains unchanged.
3. **Completed:** the Update status page has a read-only component that queries the public GitHub API for the latest `awesome:triage` issue. The discovery workflow retains no contents-write permission.

## Still open at project-governance level

1. Quarterly coverage review still requires named domain reviewers for biological camouflage, military history/materials, art/design, and computer vision.
2. External Awesome lists remain candidate sources only. Their entries and update timestamps must not be imported as verified facts.
3. After PRs #9, #10, and #12 are merged, root release notes should describe the final project structure and component versions.
