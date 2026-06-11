# camo-eval

Unified evaluation toolkit for camouflage research, part of [CamoGED](../README.md).

Three metric families:

| Family | Metrics | Status |
|--------|---------|--------|
| **Detection** | MAE, S-measure, weighted F-measure, E-measure | MAE ✅ · others scaffolded |
| **Generation** | FID, LPIPS, deception rate | scaffolded |
| **Robustness** | attack success rate, AP drop, transferability | scaffolded |

## Install

```bash
pip install -e .          # core (numpy only)
pip install -e ".[full]"  # + scipy, pillow, matplotlib
pip install -e ".[dev]"   # + pytest, ruff
```

## Use

```python
import numpy as np
from camo_eval import mae

pred = np.random.rand(352, 352)   # predicted map, [0,1] or uint8 [0,255]
gt   = np.zeros((352, 352))       # ground-truth mask
print(mae(pred, gt))
```

## Test

```bash
pytest -q
```

## Contributing metrics

Each metric has a consistent signature `metric(pred, gt) -> float` (detection) and raises
`NotImplementedError` until implemented. Pick one, implement it, add tests. See
[../CONTRIBUTING.md](../CONTRIBUTING.md).
