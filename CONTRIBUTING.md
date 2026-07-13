# Contributing to CamoGED

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
