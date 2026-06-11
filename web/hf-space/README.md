# camo-eval Hugging Face Space

This directory contains a lightweight Gradio app intended for deployment as a
Hugging Face Space.

## Scope

The first version is intentionally small:

- upload prediction and ground-truth masks
- ship repository-local example images and a tiny bundled demo dataset
- compute core detection, instance, and perceptual metrics
- run a protocol-aware batch evaluation over the bundled demo dataset
- attach observer/channel/task/protocol metadata
- export a protocol-aware JSON or Markdown report

## Local Run

From the repository root:

```bash
pip install -e "./camo-eval[full]"
pip install -r web/hf-space/requirements.txt
python web/hf-space/app.py
```

The local app binds to `http://127.0.0.1:7860` by default.

The app includes:

- two built-in single-pair examples
- one bundled batch demo dataset from `camo-eval/demo_data/rgb_masks`
- a batch path that mirrors `camo-eval evaluate-protocol --manifest ...`

## Notes

- This app is designed as the third step in the public demo route, after the
  stable Python API / CLI and the Colab notebook.
- Heavier evaluations such as large-batch generation metrics or human-study
  analytics should stay outside the Space and run in notebooks or dedicated
  pipelines.
