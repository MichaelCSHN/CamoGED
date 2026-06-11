# camo-eval

Unified evaluation toolkit for camouflage research, part of
[CamoGED](../README.md).

`camo-eval` is intended to become a unified evaluation stack for camouflage
research across four layers:

1. Core algorithmic metrics
2. Protocolized benchmarking
3. Extension modules for richer signals and domains
4. External experiment protocols for human and mission-level evaluation

The current implementation is strongest in layer 1 and provides the stable API
surface that the rest of the stack can grow around. The architecture and
roadmap are described in [ARCHITECTURE.md](./ARCHITECTURE.md).

## Current Surface

Three public metric families are exposed today:

| Family | Metrics | Status |
|--------|---------|--------|
| **Detection** | MAE, S-measure, weighted F-measure, E-measure, F-measure | implemented and reference-tested |
| **Generation** | FID, LPIPS, deception rate | API present; optional implementation pending |
| **Robustness** | attack success rate, AP drop, transferability | lightweight helpers implemented |

Other public utilities:

- `evaluate(pred_dir, gt_dir, metrics)` for batch directory evaluation
- `ResultsTable` as the common result container
- `to_markdown(results)` and `to_latex(results)` for report export

## Scope Model

The intended long-term structure is:

- **Core library**: pure algorithmic metrics and batch runners that can be used
  as ordinary Python functions or CLI calls
- **Extension modules**: heavier or domain-specific evaluators such as
  instance/video/perceptual/signature metrics
- **External protocols**: standardized schemas and analyzers for human studies,
  mission-level acquisition experiments, and multi-observer studies

This split matters because not every "evaluation" in camouflage is reducible to
`metric(pred, gt) -> float`. Some are protocol-driven experiments whose role in
the toolkit is to standardize inputs, logging, aggregation, and reporting.

## Install

```bash
pip install -e .          # core
pip install -e ".[full]"  # + scipy, pillow, matplotlib
pip install -e ".[dev]"   # + pytest, pytest-cov, ruff
```

## Use

```python
import numpy as np
from camo_eval import evaluate, mae

pred = np.random.rand(352, 352)
gt = np.zeros((352, 352))
print(mae(pred, gt))

results = evaluate("pred_dir", "gt_dir", ["mae", "fw", "sm", "em", "f"])
print(results)
```

## Test

```bash
pytest -q
pytest --cov=camo_eval --cov-report=term-missing -q
```

## Next Steps

Near-term priorities are:

- extend layer-1 coverage to instance, video, perceptual, and generation metrics
- add a stable CLI on top of the current Python API
- ship a reproducible Colab notebook
- expose a lightweight Hugging Face Space for interactive demos
