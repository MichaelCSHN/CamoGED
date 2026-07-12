# camo-eval Gradio preview

This directory contains an optional local/Hugging Face Space interface for mask evaluation. It is not a hosted COD model and does not claim benchmark authority.

## Scope

- upload prediction and ground-truth masks;
- run the validated COD/SOD core metrics and IoU/Dice/SSIM;
- optionally run diagnostics explicitly labelled `experimental` or `_lite`;
- display mask overlays and TP/FP/FN error maps;
- run a protocol-aware batch evaluation on synthetic repository fixtures;
- export JSON and Markdown reports with implementation and provenance metadata.

Standard FID, KID, LPIPS, DISTS, MS-SSIM, Boundary IoU, and DAVIS boundary F/J&F are not implemented in this preview. The Space does not silently substitute heuristic values under those names.

## Local run

```bash
pip install -e "./camo-eval[full]"
pip install -r web/hf-space/requirements.txt
python web/hf-space/app.py
```

The app binds to `0.0.0.0` by default for container deployment. Set `GRADIO_SERVER_NAME=127.0.0.1` for a loopback-only local run.

## Data and privacy

Bundled examples under `camo-eval/demo_data/` are synthetic fixtures. User uploads are processed by the running Gradio service; deployment operators must publish their own retention and privacy policy. The browser-only VitePress demo keeps user-selected files local to the browser.
