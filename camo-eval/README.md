# camo-eval

`camo-eval` is a protocol-aware research-preview toolkit. It separates validated metrics from experimental diagnostics so that a convenient API cannot be mistaken for a standard implementation.

## Capability matrix

| Surface | Status | Evidence |
|---|---|---|
| MAE, weighted F, S-measure, E-measure, F/PR | **validated** | compared with PySODMetrics fixtures within 1e-4 |
| SSIM | **validated** | compared with scikit-image Gaussian-weighted settings |
| IoU, Dice | **validated definitions** | exact binary-set tests |
| AP/AR helpers, signature and robustness summaries | **implemented** | behavioral/unit tests; protocol-dependent |
| temporal derivative stability | **experimental** | defined behavior; not a community standard |
| `boundary_match_score` | **experimental** | tolerance-based contour matching; not Boundary IoU |
| `ms_ssim_lite` | **experimental** | multi-scale SSIM product; not standard MS-SSIM |
| `boundary_f_score_lite`, `j_and_f_lite` | **experimental** | not yet aligned with DAVIS official scripts |
| `fid_lite`, `kid_lite`, `lpips_lite`, `dists_lite` | **experimental** | handcrafted diagnostics; never report as standard metrics |
| FID, KID, LPIPS, DISTS, standard MS-SSIM/Boundary IoU/DAVIS F | **planned** | standard names raise `NotImplementedError` |

Full evidence and release gates are in `VALIDATION.md`.

## Installation

```bash
pip install -e .
pip install -e ".[full]"
pip install -e ".[dev]"
```

## Validated COD example

```python
from camo_eval import evaluate

results = evaluate("pred_dir", "gt_dir", ["mae", "fw", "sm", "em", "f"])
print(results)
```

## Experimental diagnostics

```python
from camo_eval import fid_lite, boundary_match_score

# These names explicitly identify non-standard diagnostics.
score = fid_lite("real_dir", "generated_dir")
```

## Protocol-aware report

```bash
camo-eval evaluate-report   --pred-dir pred --gt-dir gt --metrics mae fw sm em   --observer model --channel rgb --task image-cod   --protocol "fixed test split; automatic prediction; no manual prompt"
```

A report should also record the dataset version/hash, prediction revision, threshold policy, seed, environment, uncertainty method, and `camo-eval` version.

## Public demo scope

The browser demo is a synthetic teaching tool. The optional local Gradio app uses synthetic repository fixtures. Neither surface is a hosted SOTA model service or a benchmark authority.

## Tests

```bash
pytest --cov=camo_eval --cov-fail-under=80 -q
ruff check src tests
black --check src tests
```
