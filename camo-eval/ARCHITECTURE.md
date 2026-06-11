# camo-eval Architecture and Expansion Plan

This document describes the intended shape of `camo-eval` as a unified
evaluation stack for camouflage research. The key design decision is to accept a
three-part structure:

1. **Core library**
2. **Extension modules**
3. **External experiment protocols**

That split is necessary because the field mixes ordinary algorithmic metrics,
protocol-sensitive benchmarking, and evaluations that depend on humans,
specialized sensors, or mission-specific acquisition tasks.

## Layer 1: Core Algorithmic Metrics

### Introduction

Layer 1 is the mathematical core of the toolkit: metrics that can be computed
from structured inputs such as prediction maps, masks, scores, or paired image
sets. These belong in the core package because they are deterministic,
reproducible, and easy to expose through both Python and CLI interfaces.

### Concept

The purpose of this layer is to answer questions like:

- How close is a predicted mask to the ground truth?
- How well does a generated sample match the target distribution?
- How much does an attack degrade detector performance?

### Definition and Algorithms

Representative metrics:

- **MAE**: mean absolute pixel error, `mean(abs(pred - gt))`
- **F-measure**: harmonic balance of precision and recall across thresholds
- **Weighted F-measure**: Margolin-style F-measure that penalizes spatially
  important errors more heavily than ordinary pixelwise mismatch
- **S-measure**: object-aware plus region-aware structural similarity
- **E-measure**: enhanced alignment score over thresholded foreground maps
- **FID / KID / LPIPS / SSIM / MS-SSIM**: generation and perceptual metrics
- **ASR / AP drop / transferability**: attack and robustness summaries

### Suitable Scenarios

This layer is appropriate when inputs are already available in digital form and
the evaluation does not require extra protocol state beyond the data itself.

Examples:

- image COD benchmark tables
- detector-vs-detector comparisons
- batch comparison of adversarial attack outputs
- generation-quality ablations

### Current Status

Implemented now:

- detection: `MAE`, `F`, `weighted F`, `S`, `E`
- robustness helpers: `attack_success_rate`, `ap_drop`, `transferability`
- batch runner and table exporters

Planned next:

- instance metrics: `IoU`, `Dice`, `AP`, `AR`, `Boundary IoU`
- video metrics: `J`, `F`, `J&F`, temporal stability
- generation metrics: `FID`, `KID`, `LPIPS`, `SSIM`, `MS-SSIM`

## Layer 2: Protocolized Benchmarking

### Introduction

Layer 2 sits above single metrics. It standardizes *how* an experiment is run
and reported: dataset splits, observer definition, sensor channel, threat
model, detector family, evaluation thresholding, and aggregation rules.

### Concept

The main idea is that a metric without protocol context is often not comparable.
In camouflage research, a score becomes meaningful only when the report also
states:

- **observer**: human, model, detector family, sensor operator
- **channel**: RGB, thermal, multispectral, multimodal, radar, video
- **task**: image COD, VCOD, instance COD, physical attack, search experiment
- **protocol**: dataset split, preprocessing, thresholding, evaluation rules

### Definition and Algorithms

This layer is less about one formula and more about reproducible evaluation
pipelines:

- directory-level runners
- per-dataset evaluators
- multi-model score aggregation
- report schemas
- export to Markdown, LaTeX, JSON, CSV, and leaderboard records

### Suitable Scenarios

- reproducing a paper table
- comparing multiple methods under one declared protocol
- building a public leaderboard
- auditing whether two reported results are actually comparable

### Current Status

Implemented now:

- `evaluate(pred_dir, gt_dir, metrics)` with basename matching
- `ResultsTable`
- Markdown and LaTeX export

Planned next:

- explicit report schema carrying observer/channel/task/protocol
- dataset bundles and protocol presets
- CLI entrypoints such as `camo-eval run ...` and `camo-eval export ...`

## Layer 3: Extension Modules

### Introduction

Layer 3 covers metrics that are still algorithmic but require additional
dependencies, richer data structures, or domain-specific logic. These should not
burden the core install, but they should still live inside the same conceptual
toolkit.

### Concept

Examples include:

- instance-level camouflage evaluation
- video continuity and stability metrics
- generation/perceptual metrics with heavier model dependencies
- multispectral and thermal signature metrics
- detector-plug-in deception metrics

### Definition and Algorithms

Typical module families:

- `metrics.instance`
- `metrics.video`
- `metrics.perceptual`
- `metrics.signature`
- `metrics.generation`

These may depend on:

- `scipy`
- `pillow`
- `torch`
- pretrained backbones
- sensor-specific calibration rules

### Suitable Scenarios

- video COD and VCOS evaluation
- physical camouflage across RGB and thermal channels
- detector-aware deception scoring
- richer perceptual similarity studies

### Current Status

The package already has the public API surface for generation metrics, but the
implementations remain deferred. This is the natural place to expand next.

## Layer 4: External Experiment Protocols

### Introduction

Layer 4 covers evaluations that cannot honestly be reduced to a pure local
function call. These are still part of `camo-eval`, but here the package serves
as a standardization and analysis layer rather than pretending to simulate the
whole experiment.

### Concept

This includes:

- human visual search experiments
- eye-tracking studies
- military acquisition or target-recognition task protocols
- multi-observer and multi-sensor field evaluations

### Definition and Algorithms

Relevant outputs may include:

- reaction time
- hit rate / miss rate / false alarm rate
- `d'` from signal detection theory
- fixation and dwell statistics
- detection / orientation / recognition / identification task success
- TOD / TTP style acquisition summaries

The library role here is to provide:

- experiment log schemas
- result importers
- statistical analyzers
- report generators
- protocol templates

### Suitable Scenarios

- lab-based human-perception studies
- field trials with thermal or multispectral devices
- acquisition-task evaluation in military or surveillance settings

### Current Status

Not implemented yet. This layer should begin as:

- standardized input formats
- analyzers for logged experiments
- report generation

rather than trying to fake the acquisition experiment itself.

## Three-Part Package Structure

The practical repository layout should evolve toward:

```text
camo_eval/
  metrics/        # core and extension algorithmic metrics
  protocols/      # dataset/task/protocol declarations
  analysis/       # aggregation, reporting, statistics
  runner.py       # batch execution entry points
  export.py       # markdown/latex/json/csv output
```

With the following conceptual split:

- **Core library**: deterministic metrics and light runners
- **Extension modules**: heavier or domain-specific evaluators
- **External experiment protocols**: schemas, analyzers, and reporting tools

## Online Demo Route

The deployment path should stay pragmatic:

1. **Stable Python API + CLI**
2. **Colab notebook**
3. **Hugging Face Space**

### CLI + Python API

This is the base layer. Everything else should call into the same public API.
The CLI should wrap batch evaluation, exports, and protocol presets.

### Colab

Colab is the best first interactive surface because it is easy to reproduce,
cheap to share, and can host larger examples than a browser-only demo.

Recommended notebook scopes:

- upload or mount predictions and masks
- run image COD metrics
- export Markdown/LaTeX tables
- optionally enable heavier generation metrics when dependencies are available

### Codespaces

Codespaces is useful for contributors and maintainers, but it is not a good
public-facing replacement for Colab. It is better treated as a development
environment than as the primary demo surface.

### Hugging Face Space

A Space is suitable once the core API is stable. The first version should stay
light:

- upload `pred` / `gt`
- compute image-level detection metrics
- visualize thresholds and error maps
- export small result tables

Heavy multi-model or mission-level experiments should remain outside the Space.

## Implementation Priority

The recommended order is:

1. finish and harden layer-1 core metrics
2. add protocol metadata and CLI support
3. add Colab for reproducible public use
4. expand extension modules
5. add a lightweight Hugging Face Space
6. add human and mission-level analyzers as protocol modules
