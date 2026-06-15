# 🔬 Projects — original method anchors

CamoGED is more than an aggregator: it carries three **original** projects that turn
the survey-grade knowledge in the book into reproducible, comparable, demo-able
anchors across the three pillars. They make the platform "人无我有" (offer what others
don't) rather than another static list.

| Project | Pillar(s) · Domain · Track | Book | Website | camo-eval |
|---------|----------------------------|------|---------|-----------|
| [`coder`](coder/) | Detection · Intelligent · **Image COD** | §11.7 `{#sec-coder}` | `/demo` image · `/leaderboard` | [`coder/protocol.json`](coder/protocol.json) — `image-cod` |
| [`flowcamo`](flowcamo/) | **Generation + Detection** · Intelligent · **Video** | §8.7 + §12.6 | `/demo` video | [`flowcamo/protocol.json`](flowcamo/protocol.json) — `video-cod` |
| [`dualvcod`](dualvcod/) | Detection · Intelligent · **Video instance** | §13.4 `{#sec-dualvcod}` | `/demo` instance | [`dualvcod/protocol.json`](dualvcod/protocol.json) — `instance-cod` |

`flowcamo` straddles both **generation (the hider)** and **detection (the seeker)**,
making it the clearest demonstration of the §1.4 hide ⇄ seek loop.

## How an anchor stays honest

Each project directory is an **integration anchor**, not a code dump. It holds:

- a structured `README.md` — role, design intent, the exact `camo-eval` evaluation
  contract, reproduction wiring, and a status checklist;
- a `protocol.json` — a real [`camo-eval`](../camo-eval/) protocol manifest
  (consumable by `camo-eval evaluate-protocol`) that fixes the observer/channel/task,
  protocol string, and metric keys *before* any numbers exist;
- a `.gitignore` — weights and prediction masks are **linked, never committed**.

> **No-fabrication policy (`AGENTS.md` §3).** Architecture details, ablations and
> quantitative results are added only **after each paper is released**. Until then
> every leaderboard metric stays `null` with `verified: false`, and the book sections
> remain design-intent placeholders. The standalone method repositories are
> vendored/submoduled here once public.

## Reproduce, today

Every anchor ships a **toolchain smoke test** that runs against the bundled
`camo-eval` demo masks, so the evaluation path is verifiable now (it is a wiring
check on synthetic data, not the method's results):

```bash
cd CamoGED && pip install -e ./camo-eval
camo-eval evaluate \
  --pred-dir camo-eval/demo_data/cod_sota_masks/pred \
  --gt-dir   camo-eval/demo_data/cod_sota_masks/gt \
  --metrics mae fw sm em --format markdown
```

The full-reproduction command in each README swaps the demo dirs for the project's
released predictions via its `protocol.json`. See
[`../docs/PROJECT_PLAN.md`](../docs/PROJECT_PLAN.md) §七 for the integration plan.
