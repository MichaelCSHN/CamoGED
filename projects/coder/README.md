# coder

**Role in CamoGED:** Detection · Intelligent domain · Image COD — also a `/leaderboard`
self-entry and the `/demo` image model.

> Image camouflaged object detection (original method anchor)

`coder` is CamoGED's original anchor on the **image COD** track. It continues the
method evolution narrated in [Chapter 11](../../book/chapters/11-image-cod.qmd)
(§11.1–11.6: traditional limits → search–identification → structure modelling →
frequency cues → graph/sequence → weak/semi-supervision) and is detailed in
**§11.7 `{#sec-coder}`**.

> **No-fabrication policy.** This anchor records *positioning, design intent, the
> evaluation contract, and reproduction wiring* only. Architecture details,
> ablations and quantitative numbers are filled in **after the paper is released**.
> Until then every metric stays `null` in [`data/leaderboard.yaml`](../../data/leaderboard.yaml)
> (`verified: false`). See [`ETHICS.md`](../../ETHICS.md) and `AGENTS.md` §3.

## Design intent (no numbers yet)

Sections 11.1–11.6 expose recurring limits in prior image-COD methods: the
boundary-vs-global-semantics trade-off (most methods lean to one side), degradation
at extreme target scales (very large / very small), and missed detections in highly
overlapping multi-target scenes. `coder` is designed against one or more of these
core limits. The concrete architecture, motivation, ablations and a SOTA comparison
table are released with the paper and mirrored into §11.7.

## Where it plugs in

| Surface | Binding | Status |
|---------|---------|--------|
| Book | §11.7 `{#sec-coder}` in [11-image-cod.qmd](../../book/chapters/11-image-cod.qmd) | written (placeholder, no numbers) |
| Leaderboard | `coder (ours)` / `cod10k` in [`data/leaderboard.yaml`](../../data/leaderboard.yaml) | registered, metrics `null` |
| Website | `/demo` image inference · `/leaderboard` | pending weights |
| camo-eval | protocol [`protocol.json`](protocol.json) (`image-cod`: MAE, Fw, Sm, Em) | protocol registered |

The metric keys (`MAE`, `Fw`, `Sm`, `Em`) match `camo-eval`'s detection group, the
`leaderboard.yaml` schema (`data/SCHEMA.md` §4) and Chapter 15 — so a released
result drops straight into the leaderboard with no key translation.

## Status

- [x] Anchor page, role, and design intent recorded
- [x] `camo-eval` evaluation protocol registered ([`protocol.json`](protocol.json))
- [x] Leaderboard entry reserved (`coder (ours)`, metrics `null`)
- [ ] Code linked / vendored from the standalone `coder` repository
- [ ] Pretrained weights referenced (not committed; see [`.gitignore`](.gitignore))
- [ ] Quantitative results verified and filled into §11.7 + `leaderboard.yaml`
- [ ] Online `/demo` wired into the website

## Reproduce

### 1. Toolchain smoke test (runs today)

Verifies the evaluation path end-to-end against the bundled demo masks — this is a
**wiring check on synthetic demo data, not `coder`'s results**:

```bash
cd CamoGED
pip install -e ./camo-eval
camo-eval evaluate \
  --pred-dir camo-eval/demo_data/cod_sota_masks/pred \
  --gt-dir   camo-eval/demo_data/cod_sota_masks/gt \
  --metrics mae fw sm em --format markdown
```

### 2. Full reproduction (once predictions / weights are released)

Drop the released prediction masks into `preds/` and the dataset ground truth into
`gts/` (basenames must match), then run this project's registered protocol:

```bash
camo-eval evaluate-protocol --manifest projects/coder/protocol.json --root projects/coder
```

The resulting `MAE/Fw/Sm/Em` are what get verified and written into
`data/leaderboard.yaml` (`verified: true` + a resolvable `source`).

See [`../README.md`](../README.md) for how the three projects map onto the
generation / detection / evaluation pillars, and
[`../../docs/PROJECT_PLAN.md`](../../docs/PROJECT_PLAN.md) §七 for the integration plan.
