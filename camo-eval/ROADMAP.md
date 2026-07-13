# camo-eval roadmap

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
