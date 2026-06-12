# Demo

This page covers camouflage metrics that can run without large datasets, model weights, or external services. Heavy learned backends remain out of scope for the browser demo; the repository exposes lightweight, deterministic surrogates where that is useful for smoke tests and protocol comparisons.

## Quick artifacts

| Bundle | Overlay | Error map | PR curve | Scores | Diagnostics |
| --- | --- | --- | --- | --- | --- |
| COD sample 1 | [overlay](./demo-artifacts/cod-sample1/mask_overlay.png) | [error](./demo-artifacts/cod-sample1/error_map.png) | [PR](./demo-artifacts/cod-sample1/pr_curve.png) | [scores](./demo-artifacts/cod-sample1/scores.json) | [diagnostics](./demo-artifacts/cod-sample1/diagnostics.json) |
| COD sample 2 | [overlay](./demo-artifacts/cod-sample2/mask_overlay.png) | [error](./demo-artifacts/cod-sample2/error_map.png) | [PR](./demo-artifacts/cod-sample2/pr_curve.png) | [scores](./demo-artifacts/cod-sample2/scores.json) | [diagnostics](./demo-artifacts/cod-sample2/diagnostics.json) |
| Demo-set generation surrogate | - | - | - | [generation distances](./demo-artifacts/cod-demo-generation.json) | - |

## Metric coverage

| Family | Metrics | Browser/HF | CLI/Colab | Default threshold or assumption |
| --- | --- | --- | --- | --- |
| Detection | MAE, weighted F, S-measure, E-measure, F-measure | yes | yes | mask threshold `0.5` for binary visualizations |
| PR diagnostics | precision, recall, PR curve | static artifacts; HF JSON | yes | adaptive and sweep thresholds from `camo-eval` |
| Region/boundary | IoU, Dice, BoundaryIoU | yes | yes | mask threshold `0.5`; boundary dilation ratio from API default |
| Perceptual mask similarity | SSIM, MS-SSIM | yes | yes | normalized grayscale/RGB inputs in `[0,1]` or `[0,255]` |
| Lightweight generation similarity | FID_lite, KID_lite, LPIPS_lite, DISTS_lite | static artifacts for bundled data; pairwise in HF | yes | deterministic handcrafted features; no Inception/LPIPS weights |
| Clutter and difficulty | edge density, subband entropy, feature congestion, camouflage difficulty | static artifacts; HF when a scene is supplied | yes | adaptive edge threshold `mean + std`; near-background ring default |
| Signature analysis | thermal contrast, signal-to-clutter ratio, spectral angle mapper | documented CLI/API path | yes | caller supplies target/background or signatures |
| Robustness | attack success rate, AP drop, transferability | API/CLI-adjacent only | yes | requires paired clean/attacked outputs supplied by caller |

## Run surfaces

- Web: this page hosts static outputs generated from `camo-eval/demo_data/cod_sota_masks`.
- HF Space: source is ready in [web/hf-space](https://github.com/MichaelCSHN/CamoGED/tree/main/web/hf-space); deploy it as a Gradio Space when an interactive hosted endpoint is needed.
- Colab: open the notebook at [camo_eval_colab_demo.ipynb](https://colab.research.google.com/github/MichaelCSHN/CamoGED/blob/main/camo-eval/notebooks/camo_eval_colab_demo.ipynb).
- GitHub/CLI: install with `pip install -e ./camo-eval[full]`, then run the commands below.

```bash
camo-eval list-metrics
camo-eval visualize --pred camo-eval/demo_data/cod_sota_masks/pred/sample1.png --gt camo-eval/demo_data/cod_sota_masks/gt/sample1.png --output-dir demo-output
camo-eval image-diagnostics --image camo-eval/demo_data/cod_sota_masks/images/sample1.png --mask camo-eval/demo_data/cod_sota_masks/gt/sample1.png
camo-eval generation-distance --real-dir camo-eval/demo_data/cod_sota_masks/gt --fake-dir camo-eval/demo_data/cod_sota_masks/pred
```

## Explicit non-goals

- The web demo does not download large pretrained models or benchmark datasets.
- `FID_lite`, `KID_lite`, `LPIPS_lite`, and `DISTS_lite` are lightweight reproducibility surrogates, not replacements for heavyweight learned backends in final papers.
- Full benchmark claims belong in verified leaderboard entries with resolvable sources, not in ad hoc demo artifacts.
