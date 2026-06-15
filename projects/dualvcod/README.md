# dualvcod

**Role in CamoGED:** Detection · Intelligent domain · Video **instance** COD —
the instance-level baseline and a `/demo` model.

> Dual-path video camouflage instance detection (original method anchor)

`dualvcod` is CamoGED's anchor on the hardest recognition track: **video camouflage
instance detection**. It stacks the three difficulty layers of
[Chapter 13](../../book/chapters/13-instance-extended.qmd): target–instance double
similarity, occlusion-blurred boundaries, and cross-frame instance-ID association.
It is detailed in **§13.4 `{#sec-dualvcod}`**.

> **No-fabrication policy.** Positioning, design intent, evaluation contract and
> reproduction wiring only. Architecture, ablations and numbers land **after the
> paper is released**; until then all metrics stay `null` / `verified: false`.
> See [`ETHICS.md`](../../ETHICS.md) and `AGENTS.md` §3.

## Design intent (no numbers yet)

The dual-path design reads as *"appearance answers **what**, motion answers **whether
it is the same one**"*: the appearance path proposes candidate instances per frame,
the motion path resolves correspondence across time. When two targets look identical
but move differently, motion separates them; when a target is briefly static,
appearance keeps the candidate; after occlusion, short/long-term memory restores the
ID. The boundary with `flowcamo` is deliberate — `flowcamo` finds the foreground
(semantic VCOD); `dualvcod` adds instance queries, trajectory association and ID
maintenance on top, and may consume `flowcamo`'s foreground as candidates.

## Where it plugs in

| Surface | Binding | Status |
|---------|---------|--------|
| Book | §13.4 `{#sec-dualvcod}` in [13-instance-extended.qmd](../../book/chapters/13-instance-extended.qmd) | written (placeholder, no numbers) |
| Website | `/demo` instance segmentation (per-frame mask + trajectory view) | pending weights |
| camo-eval | protocol [`protocol.json`](protocol.json) (`instance-cod`: IoU, Dice, Boundary-IoU) | partial — see note |

**Metric note.** `camo-eval`'s instance group (`IoU`, `Dice`, `BoundaryIoU`) covers
mask quality. Full evaluation of video instance detection also needs **AP/AR**,
**ID-switch** and **track mAP**, which require an external tracking evaluator
(cross-frame ID matching must persist over the sequence, not reset per frame). That
gap is logged for the camo-eval maintainer in
[`../../NOTES_FOR_MAINTAINER.md`](../../NOTES_FOR_MAINTAINER.md); until then this
protocol scores per-frame mask quality only.

## Status

- [x] Anchor page, role, and dual-path design intent recorded
- [x] `camo-eval` mask-quality protocol registered ([`protocol.json`](protocol.json))
- [ ] Code linked / vendored from the standalone `dualvcod` repository
- [ ] Pretrained weights referenced (not committed; see [`.gitignore`](.gitignore))
- [ ] Instance + tracking metrics (AP/AR/ID-switch) wired (needs camo-eval support)
- [ ] Results verified and filled into §13.4
- [ ] Online `/demo` (frame + trajectory views) wired into the website

## Reproduce

### 1. Toolchain smoke test (runs today)

Wiring check of the instance mask-quality path on the bundled demo masks —
**not `dualvcod`'s results**:

```bash
cd CamoGED
pip install -e ./camo-eval
camo-eval evaluate \
  --pred-dir camo-eval/demo_data/cod_sota_masks/pred \
  --gt-dir   camo-eval/demo_data/cod_sota_masks/gt \
  --metrics iou dice boundary_iou --format markdown
```

### 2. Full reproduction (once predictions / weights are released)

Place released per-frame instance masks into `preds/` and ground truth into `gts/`
(matching basenames), then run the registered protocol for mask quality:

```bash
camo-eval evaluate-protocol --manifest projects/dualvcod/protocol.json --root projects/dualvcod
```

Report AP/AR/ID-switch/track-mAP via the external tracking evaluator (see metric
note) alongside these mask-quality numbers.

See [`../README.md`](../README.md) for the pillar map and
[`../../docs/PROJECT_PLAN.md`](../../docs/PROJECT_PLAN.md) §七 for the integration plan.
