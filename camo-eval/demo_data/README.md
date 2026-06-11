# camo-eval Demo Data

This directory contains a tiny repository-local demo dataset for notebooks,
CLI smoke tests, and the Hugging Face Space.

## Structure

- `rgb_masks/pred`: prediction masks
- `rgb_masks/gt`: ground-truth masks
- `rgb_masks/manifest.json`: protocol metadata for the demo bundle

## Quick Use

Generate a runnable protocol manifest template:

```bash
camo-eval protocol-template --observer model --channel rgb --task image-cod --protocol "repository demo bundle" --pred-dir pred --gt-dir gt --metrics mae fw sm em f iou dice boundary_iou ssim ms_ssim
```

Run the bundled demo bundle through the protocol-aware CLI:

```bash
camo-eval evaluate-protocol --manifest camo-eval/demo_data/rgb_masks/manifest.json
```

The masks are deliberately tiny and synthetic. They are meant for validating
tooling and demos, not for benchmarking research models.
