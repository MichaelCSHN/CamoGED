# camo-eval Demo Data

This directory contains a tiny repository-local demo dataset for notebooks,
CLI smoke tests, and the Hugging Face Space.

## Structure

- `rgb_masks/pred`: prediction masks
- `rgb_masks/gt`: ground-truth masks
- `rgb_masks/manifest.json`: protocol metadata for the demo bundle
- `cod_sota_masks/pred`: larger synthetic prediction masks for COD/SOD metric demos
- `cod_sota_masks/gt`: larger synthetic ground-truth masks for COD/SOD metric demos
- `cod_sota_masks/images`: scene images used by target-background similarity metrics
- `cod_sota_masks/manifest.json`: protocol metadata for visualization demos

## Quick Use

Generate a runnable protocol manifest template:

```bash
camo-eval protocol-template --observer model --channel rgb --task image-cod --protocol "repository demo bundle" --pred-dir pred --gt-dir gt --metrics mae fw sm em f precision recall iou dice boundary_iou ssim ms_ssim
```

Run the bundled demo bundle through the protocol-aware CLI:

```bash
camo-eval evaluate-protocol --manifest camo-eval/demo_data/rgb_masks/manifest.json
```

Create visual outputs for one sample:

```bash
camo-eval visualize --pred camo-eval/demo_data/cod_sota_masks/pred/sample1.png --gt camo-eval/demo_data/cod_sota_masks/gt/sample1.png --output-dir camo-eval/demo_outputs/sample1
```

The masks are synthetic and deliberately small enough to ship with the repo.
They are meant for validating tooling and demos, not for benchmarking research
models.
