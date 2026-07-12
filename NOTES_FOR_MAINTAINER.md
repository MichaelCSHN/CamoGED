# Notes for the maintainer

## Open release blockers

- Complete primary-source and license verification for dataset metadata; `license_status: unknown` means CamoGED must not redistribute files.
- Validate standard MS-SSIM, Boundary IoU, DAVIS boundary F/J&F, FID, KID, LPIPS, and DISTS before enabling their standard API names. Current approximations are explicitly named `_lite` or `boundary_match_score`.
- Obtain external subject-matter review and complete the monograph image-rights ledger.
- Inspect generated ePub and PDF outputs; a successful build is not sufficient for publication approval.
- Update `RELEASE_MANIFEST.yml` only when a reviewed tag and archive actually exist.
- Select at most one original project for full integration; do not restore `coder`, `flowcamo`, or `dualvcod` to the results registry without code, weights, predictions, manifest, environment, and independent review.

## Current stable boundaries

- Image COD/SOD core metrics are validated against PySODMetrics.
- Experimental diagnostics are not permitted to populate standard leaderboard metric fields.
- Browser demonstrations use synthetic scenes or user-local uploads.
- Security-sensitive reports use `SECURITY.md`, not public issues.
