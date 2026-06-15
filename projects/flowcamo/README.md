# flowcamo

**Role in CamoGED:** Generation **and** Detection · Intelligent domain · Video —
the clearest single example of the hide ⇄ seek loop (§1.4).

> Motion-aware video camouflage generation + detection (original method anchor)

`flowcamo` spans both pillars on the **video** track: a generation branch
(synthesising motion-aware video camouflage) and a detection branch (video COD).
It is the project that most directly embodies the co-evolutionary thesis — the same
motion cues serve the hider and the seeker. Book coverage:

- Generation branch — [Chapter 8](../../book/chapters/08-intelligent-generation.qmd)
  **§8.7 `{#sec-08-flowcamo}`**.
- Detection branch — [Chapter 12](../../book/chapters/12-video-cod.qmd)
  **§12.6 `{#sec-12-flowcamo}`**.

> **No-fabrication policy.** Positioning, design intent, evaluation contract and
> reproduction wiring only. Architecture, ablations and numbers land **after the
> paper is released**; until then all metrics stay `null` / `verified: false`.
> See [`ETHICS.md`](../../ETHICS.md) and `AGENTS.md` §3.

## Design intent (no numbers yet)

Video shifts the battlefield from a single frame to a sequence, and **motion** is
both the new weapon and the new problem (the "motion paradox", §12.1). `flowcamo`
treats time as a shared resource across generation and detection: the generation
branch produces temporally consistent, motion-aware hard cases; the detection branch
exploits the same motion–appearance coupling to localise them. The boundary with
`dualvcod` is deliberate — `flowcamo` does **semantic** video COD (where is the
target, is the mask temporally stable), while `dualvcod` does **instance** video COD
(who is each target, is the ID consistent across frames). `flowcamo`'s foreground
output can serve as `dualvcod`'s candidate proposal.

## Where it plugs in

| Surface | Binding | Status |
|---------|---------|--------|
| Book (generation) | §8.7 `{#sec-08-flowcamo}` in [08-intelligent-generation.qmd](../../book/chapters/08-intelligent-generation.qmd) | written (placeholder, no numbers) |
| Book (detection) | §12.6 `{#sec-12-flowcamo}` in [12-video-cod.qmd](../../book/chapters/12-video-cod.qmd) | written (placeholder, no numbers) |
| Website | `/demo` video (generation + detection) | pending weights |
| camo-eval | protocol [`protocol.json`](protocol.json) (`video-cod`: Sm, MAE, J, J&F, Temporal) | protocol registered |

Detection metrics use `camo-eval`'s video group (`J`, `JF`, `Temporal`) plus
per-frame `Sm`/`MAE`, matching Chapter 15's video section. The generation branch is
scored with `camo-eval`'s generation group (`fid_lite`, `kid_lite`, `lpips_lite`,
`dists_lite`) once synthesised clips are available.

## Status

- [x] Anchor page, dual role, and design intent recorded
- [x] `camo-eval` detection protocol registered ([`protocol.json`](protocol.json))
- [ ] Code linked / vendored from the standalone `flowcamo` repository
- [ ] Pretrained weights referenced (not committed; see [`.gitignore`](.gitignore))
- [ ] Video-metric and generation-metric results verified and filled into §8.7 / §12.6
- [ ] Online `/demo` (generation + detection) wired into the website

## Reproduce

### 1. Toolchain smoke test (runs today)

Wiring check of the video-metric path on the bundled demo masks (treated as a
degenerate single-frame sequence) — **not `flowcamo`'s results**:

```bash
cd CamoGED
pip install -e ./camo-eval
camo-eval evaluate \
  --pred-dir camo-eval/demo_data/cod_sota_masks/pred \
  --gt-dir   camo-eval/demo_data/cod_sota_masks/gt \
  --metrics sm mae j jf temporal --format markdown
```

### 2. Full reproduction (once predictions / weights are released)

Place released per-frame predicted masks into `preds/` and ground-truth masks into
`gts/` (matching basenames, frame-ordered), then run the registered protocol:

```bash
camo-eval evaluate-protocol --manifest projects/flowcamo/protocol.json --root projects/flowcamo
```

See [`../README.md`](../README.md) for the pillar map and
[`../../docs/PROJECT_PLAN.md`](../../docs/PROJECT_PLAN.md) §七 for the integration plan.
