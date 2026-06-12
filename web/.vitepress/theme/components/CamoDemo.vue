<script setup>
import { computed, onMounted, ref } from "vue";
import { withBase } from "vitepress";

const samples = [
  {
    id: "cod-sample1",
    label: "COD sample 1",
    caption: "Low-contrast target with a compact mask and local clutter.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod-sample2",
    label: "COD sample 2",
    caption: "Second bundled scene for comparing mask and clutter behavior.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  }
];

const selectedId = ref(samples[0].id);
const scoresBySample = ref({});
const diagnosticsBySample = ref({});
const generationScores = ref({});

const selectedSample = computed(
  () => samples.find((sample) => sample.id === selectedId.value) || samples[0]
);

const score = computed(() => scoresBySample.value[selectedSample.value.id] || {});
const diagnostics = computed(
  () => diagnosticsBySample.value[selectedSample.value.id] || {}
);
const difficulty = computed(() => diagnostics.value.camouflage_difficulty || {});

function asset(path) {
  return withBase(`/demo-artifacts/${path}`);
}

async function fetchJson(path) {
  const response = await fetch(asset(path));
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`);
  }
  return response.json();
}

function formatValue(value) {
  if (value === undefined || value === null) return "n/a";
  if (typeof value !== "number") return String(value);
  if (Math.abs(value) >= 100) return value.toFixed(1);
  if (Math.abs(value) >= 10) return value.toFixed(2);
  return value.toFixed(3);
}

const headlineMetrics = computed(() => [
  { label: "MAE", value: score.value.MAE, hint: "lower is better" },
  { label: "S-measure", value: score.value.Sm, hint: "higher is better" },
  { label: "F adaptive", value: score.value.F_adaptive, hint: "higher is better" },
  { label: "IoU", value: score.value.IoU, hint: "higher is better" },
  { label: "Boundary IoU", value: score.value.BoundaryIoU, hint: "higher is better" },
  { label: "Difficulty", value: difficulty.value.difficulty, hint: "higher is harder" }
]);

const metricGroups = computed(() => [
  {
    title: "Detection",
    items: [
      ["MAE", score.value.MAE],
      ["Fw", score.value.Fw],
      ["Sm", score.value.Sm],
      ["Em max", score.value.Em_max],
      ["F max", score.value.F_max]
    ]
  },
  {
    title: "Precision/Recall",
    items: [
      ["P max", score.value.P_max],
      ["P adaptive", score.value.P_adaptive],
      ["R max", score.value.R_max],
      ["R adaptive", score.value.R_adaptive]
    ]
  },
  {
    title: "Region, Boundary, Perceptual",
    items: [
      ["IoU", score.value.IoU],
      ["Dice", score.value.Dice],
      ["Boundary IoU", score.value.BoundaryIoU],
      ["LPIPS lite", score.value.LPIPS_lite],
      ["DISTS lite", score.value.DISTS_lite]
    ]
  },
  {
    title: "Clutter and Difficulty",
    items: [
      ["Edge density", diagnostics.value.edge_density],
      ["Subband entropy", diagnostics.value.subband_entropy],
      ["Feature congestion", diagnostics.value.feature_congestion],
      ["Near mean diff", difficulty.value.near_mean_abs_diff],
      ["Near histogram overlap", difficulty.value.near_histogram_intersection]
    ]
  }
]);

onMounted(async () => {
  const scoreEntries = await Promise.all(
    samples.map(async (sample) => [sample.id, await fetchJson(`${sample.id}/scores.json`)])
  );
  scoresBySample.value = Object.fromEntries(scoreEntries);

  const diagnosticEntries = await Promise.all(
    samples.map(async (sample) => [
      sample.id,
      await fetchJson(`${sample.id}/diagnostics.json`)
    ])
  );
  diagnosticsBySample.value = Object.fromEntries(diagnosticEntries);
  generationScores.value = await fetchJson("cod-demo-generation.json");
});
</script>

<template>
  <section class="camo-demo">
    <div class="demo-hero">
      <div>
        <p class="eyebrow">Browser demo</p>
        <h1>Camouflage metric workbench</h1>
        <p class="hero-copy">
          Inspect bundled camouflaged-object samples, compare prediction masks, view
          PR curves, and read lightweight metric outputs without downloading large
          datasets or model weights.
        </p>
      </div>
      <div class="hero-panel">
        <strong>29</strong>
        <span>browser-visible scalar outputs</span>
        <small>plus overlay, error map, and PR visualizations</small>
      </div>
    </div>

    <div class="sample-tabs" aria-label="Demo samples">
      <button
        v-for="sample in samples"
        :key="sample.id"
        type="button"
        :class="{ active: selectedId === sample.id }"
        @click="selectedId = sample.id"
      >
        {{ sample.label }}
      </button>
    </div>

    <div class="demo-layout">
      <article class="visual-card">
        <div class="card-heading">
          <div>
            <p class="eyebrow">Selected bundle</p>
            <h2>{{ selectedSample.label }}</h2>
          </div>
          <p>{{ selectedSample.caption }}</p>
        </div>

        <div class="image-grid">
          <figure>
            <img :src="asset(`${selectedSample.id}/${selectedSample.scene}`)" alt="Scene image" />
            <figcaption>Scene</figcaption>
          </figure>
          <figure>
            <img
              :src="asset(`${selectedSample.id}/${selectedSample.pred}`)"
              alt="Prediction mask"
            />
            <figcaption>Prediction</figcaption>
          </figure>
          <figure>
            <img
              :src="asset(`${selectedSample.id}/${selectedSample.gt}`)"
              alt="Ground-truth mask"
            />
            <figcaption>Ground truth</figcaption>
          </figure>
          <figure>
            <img
              :src="asset(`${selectedSample.id}/mask_overlay.png`)"
              alt="Mask overlay visualization"
            />
            <figcaption>Overlay</figcaption>
          </figure>
          <figure>
            <img
              :src="asset(`${selectedSample.id}/error_map.png`)"
              alt="Error map visualization"
            />
            <figcaption>Error map</figcaption>
          </figure>
          <figure class="wide">
            <img :src="asset(`${selectedSample.id}/pr_curve.png`)" alt="Precision-recall curve" />
            <figcaption>Precision-Recall curve</figcaption>
          </figure>
        </div>
      </article>

      <aside class="metric-panel">
        <p class="eyebrow">Metric snapshot</p>
        <div class="metric-cards">
          <div v-for="metric in headlineMetrics" :key="metric.label" class="metric-card">
            <span>{{ metric.label }}</span>
            <strong>{{ formatValue(metric.value) }}</strong>
            <small>{{ metric.hint }}</small>
          </div>
        </div>

        <div class="generation-card">
          <span>Demo-set generation surrogate</span>
          <div>
            <strong>FID_lite {{ formatValue(generationScores.FID_lite) }}</strong>
            <strong>KID_lite {{ formatValue(generationScores.KID_lite) }}</strong>
          </div>
        </div>
      </aside>
    </div>

    <section class="metric-browser">
      <div class="section-title">
        <p class="eyebrow">Metric browser</p>
        <h2>What this demo computes now</h2>
      </div>
      <div class="group-grid">
        <article v-for="group in metricGroups" :key="group.title" class="group-card">
          <h3>{{ group.title }}</h3>
          <dl>
            <template v-for="[name, value] in group.items" :key="name">
              <dt>{{ name }}</dt>
              <dd>{{ formatValue(value) }}</dd>
            </template>
          </dl>
        </article>
      </div>
    </section>

    <section class="run-strip">
      <div>
        <p class="eyebrow">Run it yourself</p>
        <h2>Same metrics, three execution surfaces</h2>
      </div>
      <a href="https://colab.research.google.com/github/MichaelCSHN/CamoGED/blob/main/camo-eval/notebooks/camo_eval_colab_demo.ipynb">Open Colab</a>
      <a href="https://github.com/MichaelCSHN/CamoGED/tree/main/web/hf-space">HF Space source</a>
      <a href="https://github.com/MichaelCSHN/CamoGED/tree/main/camo-eval">CLI source</a>
    </section>

    <section class="command-card">
      <p class="eyebrow">CLI equivalent</p>
      <pre><code>camo-eval visualize --pred camo-eval/demo_data/cod_sota_masks/pred/sample1.png --gt camo-eval/demo_data/cod_sota_masks/gt/sample1.png --output-dir demo-output
camo-eval image-diagnostics --image camo-eval/demo_data/cod_sota_masks/images/sample1.png --mask camo-eval/demo_data/cod_sota_masks/gt/sample1.png
camo-eval generation-distance --real-dir camo-eval/demo_data/cod_sota_masks/gt --fake-dir camo-eval/demo_data/cod_sota_masks/pred</code></pre>
    </section>
  </section>
</template>

<style scoped>
.camo-demo {
  display: grid;
  gap: 28px;
  margin-top: 10px;
}

.demo-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 240px;
  gap: 28px;
  align-items: stretch;
  padding: 32px;
  border: 1px solid rgba(28, 55, 45, 0.15);
  border-radius: 28px;
  background:
    radial-gradient(circle at 12% 18%, rgba(103, 139, 93, 0.2), transparent 28%),
    linear-gradient(135deg, #f6f1df 0%, #e7efe3 55%, #d8e4d0 100%);
  color: #17251f;
}

.eyebrow {
  margin: 0 0 8px;
  color: #58715b;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.demo-hero h1,
.section-title h2,
.run-strip h2,
.visual-card h2 {
  margin: 0;
  color: #17251f;
  line-height: 1.04;
}

.demo-hero h1 {
  max-width: 720px;
  font-size: clamp(38px, 6vw, 72px);
  letter-spacing: -0.06em;
}

.hero-copy {
  max-width: 720px;
  margin: 18px 0 0;
  color: #39483f;
  font-size: 18px;
  line-height: 1.7;
}

.hero-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.58);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7);
}

.hero-panel strong {
  color: #182b22;
  font-size: 64px;
  line-height: 1;
}

.hero-panel span {
  color: #223b31;
  font-weight: 800;
}

.hero-panel small {
  margin-top: 10px;
  color: #5d6d61;
}

.sample-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.sample-tabs button {
  border: 1px solid rgba(72, 91, 79, 0.22);
  border-radius: 999px;
  padding: 10px 18px;
  background: #f6f3ea;
  color: #26362e;
  cursor: pointer;
  font-weight: 800;
}

.sample-tabs button.active {
  border-color: #1d3529;
  background: #1d3529;
  color: #fff9e8;
}

.demo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 22px;
}

.visual-card,
.metric-panel,
.group-card,
.run-strip,
.command-card {
  border: 1px solid rgba(39, 59, 49, 0.14);
  border-radius: 24px;
  background: #fffdf7;
  box-shadow: 0 18px 60px rgba(28, 48, 38, 0.08);
}

.visual-card {
  padding: 22px;
}

.card-heading {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}

.card-heading p:last-child {
  max-width: 340px;
  margin: 0;
  color: #687268;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

figure {
  overflow: hidden;
  margin: 0;
  border: 1px solid rgba(48, 67, 57, 0.12);
  border-radius: 18px;
  background: #eff2e8;
}

figure.wide {
  grid-column: span 2;
}

figure img {
  display: block;
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  background:
    linear-gradient(45deg, rgba(0, 0, 0, 0.04) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(0, 0, 0, 0.04) 25%, transparent 25%);
  background-size: 16px 16px;
}

figure.wide img {
  aspect-ratio: 1.55 / 1;
  background: #fff;
}

figcaption {
  padding: 9px 12px;
  color: #4d5c52;
  font-size: 12px;
  font-weight: 800;
}

.metric-panel {
  padding: 20px;
}

.metric-cards {
  display: grid;
  gap: 12px;
}

.metric-card {
  padding: 14px;
  border-radius: 18px;
  background: #eef3e7;
}

.metric-card span,
.generation-card span {
  display: block;
  color: #5c685f;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.metric-card strong {
  display: block;
  margin-top: 3px;
  color: #15291f;
  font-size: 30px;
}

.metric-card small {
  color: #6c756d;
}

.generation-card {
  margin-top: 16px;
  padding: 16px;
  border-radius: 18px;
  background: #1d3529;
  color: #fff9e8;
}

.generation-card span {
  color: #b6c7b8;
}

.generation-card div {
  display: grid;
  gap: 6px;
  margin-top: 10px;
}

.metric-browser {
  display: grid;
  gap: 16px;
}

.group-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.group-card {
  padding: 18px;
}

.group-card h3 {
  margin: 0 0 14px;
  color: #17251f;
}

dl {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px 12px;
  margin: 0;
}

dt {
  color: #627067;
}

dd {
  margin: 0;
  color: #17251f;
  font-weight: 800;
}

.run-strip {
  display: grid;
  grid-template-columns: minmax(0, 1fr) repeat(3, auto);
  gap: 14px;
  align-items: center;
  padding: 22px;
  background: #eef3e7;
}

.run-strip a {
  border-radius: 999px;
  padding: 10px 16px;
  background: #1d3529;
  color: #fff9e8;
  font-weight: 800;
  text-decoration: none;
}

.command-card {
  padding: 20px;
}

.command-card pre {
  overflow-x: auto;
  margin: 0;
  padding: 18px;
  border-radius: 16px;
  background: #16241d;
  color: #ecf7e6;
}

@media (max-width: 980px) {
  .demo-hero,
  .demo-layout,
  .run-strip {
    grid-template-columns: 1fr;
  }

  .group-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .demo-hero,
  .visual-card,
  .metric-panel,
  .run-strip,
  .command-card {
    padding: 16px;
    border-radius: 20px;
  }

  .image-grid,
  .group-grid {
    grid-template-columns: 1fr;
  }

  figure.wide {
    grid-column: span 1;
  }
}
</style>
