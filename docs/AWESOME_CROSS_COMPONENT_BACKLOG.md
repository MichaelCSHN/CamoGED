# Awesome remediation: deferred cross-component follow-ups

This file records findings discovered during the Awesome specialist remediation that affect other CamoGED components. They are deliberately **not** implemented in this branch unless required for Awesome navigation or build integrity.

## Book

1. `book/chapters/appendix-resources.qmd` still describes the schema-2 single-task fields and should later explain the curated Awesome / complete Catalog split and the multi-axis extension.
2. Chapter 10's task map should later be checked against the new catalog facets: bbox RCOD, tracking, incomplete supervision, zero-shot/open-vocabulary, VLM, and robustness now have explicit catalog categories.
3. Chapter 14 should later be checked for 2025–2026 foundation-model references including CamSAM2, MMCSBench, SDDF, and related work. New catalog inclusion does not justify automatic book citation.
4. `book/references.bib` does not yet contain all new metadata-only catalog records. Only resources actually cited in the book should be added, after bibliographic verification.
5. The book's publication fact-check register should later add a periodic check for claims such as “first”, “largest”, and “latest” that may be affected by the dynamic catalog.

## Demo

1. The browser demo remains a synthetic teaching tool. No newly discovered model or dataset should be connected automatically.
2. The demo's explanatory text should later link to the new Catalog and metric-validation register, but this is not necessary for Awesome acceptance.
3. Any future model demo must use a catalog record with code/weight provenance and must not treat Awesome inclusion as reproduction evidence.

## Website outside Awesome

1. The old `/papers` page becomes a short pointer to `/catalog`; broader information architecture should be reviewed after the specialist branch is merged.
2. Search/filter UI for the multi-axis catalog is currently static Markdown. A later web work package may add client-side filters without changing the accepted metadata model.
3. A public “latest automated scan date” widget would require a safe dynamic data surface. The current implementation links to GitHub triage issues instead of granting the scheduled scanner contents-write permission.

## Project governance

1. Quarterly coverage review requires named domain reviewers for biological camouflage, military history/materials, art/design, and computer vision.
2. External Awesome lists are candidate sources only. Their entries and update timestamps must not be imported as verified facts.
3. After PR #9 and this specialist PR are merged, root release notes should describe the new Awesome/Catalog distinction.
