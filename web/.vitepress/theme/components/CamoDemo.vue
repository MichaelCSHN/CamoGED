<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import { withBase } from "vitepress";

const samples = [
  {
    id: "cod10k-batfish",
    label: "Aquatic: BatFish",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-seadragon",
    label: "Aquatic: LeafySeaDragon",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-octopus",
    label: "Aquatic: Octopus",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-chameleon",
    label: "Terrestrial: Chameleon",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-cheetah",
    label: "Terrestrial: Cheetah",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-moth",
    label: "Flying: Moth",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-frog",
    label: "Aquatic: FrogFish",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  },
  {
    id: "cod10k-human",
    label: "Terrestrial: Human",
    caption: "Real COD10K Test image with object mask.",
    scene: "scene.png",
    pred: "prediction.png",
    gt: "ground-truth.png"
  }
];

const selectedId = ref(samples[0].id);
const scoresBySample = ref({});
const diagnosticsBySample = ref({});
const generationScores = ref({});

const editorCanvas = ref(null);
const imageName = ref("Aquatic: BatFish");
const imageWidth = ref(0);
const imageHeight = ref(0);
const sourcePixels = ref(null);
const targetMask = ref(null);
const manualBackgroundMask = ref(null);
const maskVersion = ref(0);
const activeTool = ref("seed");
const brushSize = ref(18);
const tolerance = ref(42);
const backgroundMode = ref("near");
const lastSeed = ref(null);

const selectedSample = computed(
  () => samples.find((sample) => sample.id === selectedId.value) || samples[0]
);
const score = computed(() => scoresBySample.value[selectedSample.value.id] || {});
const diagnostics = computed(
  () => diagnosticsBySample.value[selectedSample.value.id] || {}
);
const difficulty = computed(() => diagnostics.value.camouflage_difficulty || {});

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

function asset(path) {
  return withBase(`/demo-artifacts/${path}`);
}

async function fetchJson(path) {
  const response = await fetch(asset(path));
  if (!response.ok) throw new Error(`Failed to load ${path}`);
  return response.json();
}

function formatValue(value) {
  if (value === undefined || value === null || Number.isNaN(value)) return "n/a";
  if (typeof value !== "number") return String(value);
  if (Math.abs(value) >= 100) return value.toFixed(1);
  if (Math.abs(value) >= 10) return value.toFixed(2);
  return value.toFixed(3);
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

function scaledSize(width, height, maxSide = 640) {
  const scale = Math.min(1, maxSide / Math.max(width, height));
  return {
    width: Math.max(1, Math.round(width * scale)),
    height: Math.max(1, Math.round(height * scale))
  };
}

async function setEditorImage(img, name) {
  const size = scaledSize(img.naturalWidth || img.width, img.naturalHeight || img.height);
  imageWidth.value = size.width;
  imageHeight.value = size.height;
  imageName.value = name;
  await nextTick();

  const canvas = document.createElement("canvas");
  canvas.width = size.width;
  canvas.height = size.height;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  ctx.drawImage(img, 0, 0, size.width, size.height);
  sourcePixels.value = ctx.getImageData(0, 0, size.width, size.height);
  targetMask.value = new Uint8Array(size.width * size.height);
  manualBackgroundMask.value = new Uint8Array(size.width * size.height);
  maskVersion.value += 1;
  lastSeed.value = null;
  drawEditor();
}

async function loadBundledIntoEditor(sample = samples[0]) {
  const img = await loadImage(asset(`${sample.id}/${sample.scene}`));
  await setEditorImage(img, sample.label);
}

async function onFileUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  try {
    const img = await loadImage(url);
    await setEditorImage(img, file.name);
  } finally {
    URL.revokeObjectURL(url);
    event.target.value = "";
  }
}

function drawEditor() {
  const canvas = editorCanvas.value;
  if (!canvas || !sourcePixels.value) return;
  canvas.width = imageWidth.value;
  canvas.height = imageHeight.value;
  const ctx = canvas.getContext("2d");
  const rendered = new ImageData(
    new Uint8ClampedArray(sourcePixels.value.data),
    imageWidth.value,
    imageHeight.value
  );
  const bg = currentBackgroundMask();
  for (let i = 0; i < targetMask.value.length; i += 1) {
    const offset = i * 4;
    if (bg[i]) {
      rendered.data[offset] = Math.round(rendered.data[offset] * 0.55 + 40 * 0.45);
      rendered.data[offset + 1] = Math.round(rendered.data[offset + 1] * 0.55 + 110 * 0.45);
      rendered.data[offset + 2] = Math.round(rendered.data[offset + 2] * 0.55 + 210 * 0.45);
    }
    if (targetMask.value[i]) {
      rendered.data[offset] = Math.round(rendered.data[offset] * 0.45 + 248 * 0.55);
      rendered.data[offset + 1] = Math.round(rendered.data[offset + 1] * 0.45 + 176 * 0.55);
      rendered.data[offset + 2] = Math.round(rendered.data[offset + 2] * 0.45 + 35 * 0.55);
    }
  }
  ctx.putImageData(rendered, 0, 0);
}

function pointFromEvent(event) {
  const rect = editorCanvas.value.getBoundingClientRect();
  return {
    x: Math.max(0, Math.min(imageWidth.value - 1, Math.floor((event.clientX - rect.left) * imageWidth.value / rect.width))),
    y: Math.max(0, Math.min(imageHeight.value - 1, Math.floor((event.clientY - rect.top) * imageHeight.value / rect.height)))
  };
}

function paintAt(x, y) {
  if (!targetMask.value) return;
  const radius = Math.max(1, Math.round(brushSize.value / 2));
  for (let yy = y - radius; yy <= y + radius; yy += 1) {
    if (yy < 0 || yy >= imageHeight.value) continue;
    for (let xx = x - radius; xx <= x + radius; xx += 1) {
      if (xx < 0 || xx >= imageWidth.value) continue;
      if ((xx - x) ** 2 + (yy - y) ** 2 > radius ** 2) continue;
      const index = yy * imageWidth.value + xx;
      if (activeTool.value === "target") {
        targetMask.value[index] = 1;
        manualBackgroundMask.value[index] = 0;
      } else if (activeTool.value === "background") {
        manualBackgroundMask.value[index] = 1;
        targetMask.value[index] = 0;
      } else if (activeTool.value === "erase") {
        targetMask.value[index] = 0;
        manualBackgroundMask.value[index] = 0;
      }
    }
  }
  maskVersion.value += 1;
  drawEditor();
}

let pointerDown = false;

function onPointerDown(event) {
  if (!sourcePixels.value) return;
  const point = pointFromEvent(event);
  if (activeTool.value === "seed") {
    autoSegment(point.x, point.y);
    return;
  }
  pointerDown = true;
  editorCanvas.value.setPointerCapture?.(event.pointerId);
  paintAt(point.x, point.y);
}

function onPointerMove(event) {
  if (!pointerDown || activeTool.value === "seed") return;
  const point = pointFromEvent(event);
  paintAt(point.x, point.y);
}

function onPointerUp() {
  pointerDown = false;
}

function colorDistance(index, seed) {
  const data = sourcePixels.value.data;
  const offset = index * 4;
  const dr = data[offset] - seed[0];
  const dg = data[offset + 1] - seed[1];
  const db = data[offset + 2] - seed[2];
  return Math.sqrt(dr * dr + dg * dg + db * db);
}

function autoSegment(x = Math.floor(imageWidth.value / 2), y = Math.floor(imageHeight.value / 2)) {
  if (!sourcePixels.value) return;
  const width = imageWidth.value;
  const height = imageHeight.value;
  const seedIndex = y * width + x;
  const offset = seedIndex * 4;
  const seed = [
    sourcePixels.value.data[offset],
    sourcePixels.value.data[offset + 1],
    sourcePixels.value.data[offset + 2]
  ];
  const visited = new Uint8Array(width * height);
  const proposed = new Uint8Array(width * height);
  const queue = [seedIndex];
  visited[seedIndex] = 1;
  const limit = Number(tolerance.value);

  for (let head = 0; head < queue.length; head += 1) {
    const index = queue[head];
    if (colorDistance(index, seed) > limit) continue;
    proposed[index] = 1;
    const px = index % width;
    const py = Math.floor(index / width);
    const neighbors = [
      [px - 1, py],
      [px + 1, py],
      [px, py - 1],
      [px, py + 1]
    ];
    for (const [nx, ny] of neighbors) {
      if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
      const next = ny * width + nx;
      if (!visited[next]) {
        visited[next] = 1;
        queue.push(next);
      }
    }
  }

  targetMask.value = proposed;
  manualBackgroundMask.value = new Uint8Array(width * height);
  maskVersion.value += 1;
  lastSeed.value = { x, y };
  drawEditor();
}

function clearMasks() {
  if (!sourcePixels.value) return;
  targetMask.value = new Uint8Array(imageWidth.value * imageHeight.value);
  manualBackgroundMask.value = new Uint8Array(imageWidth.value * imageHeight.value);
  maskVersion.value += 1;
  lastSeed.value = null;
  drawEditor();
}

function dilate(mask, iterations = 5) {
  let current = mask;
  const width = imageWidth.value;
  const height = imageHeight.value;
  for (let iter = 0; iter < iterations; iter += 1) {
    const next = new Uint8Array(current);
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const index = y * width + x;
        if (current[index]) continue;
        let hit = false;
        for (let dy = -1; dy <= 1; dy += 1) {
          for (let dx = -1; dx <= 1; dx += 1) {
            const nx = x + dx;
            const ny = y + dy;
            if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
            if (current[ny * width + nx]) hit = true;
          }
        }
        if (hit) next[index] = 1;
      }
    }
    current = next;
  }
  return current;
}

function currentBackgroundMask() {
  const total = imageWidth.value * imageHeight.value;
  const bg = new Uint8Array(total);
  if (!targetMask.value) return bg;
  if (backgroundMode.value === "manual") {
    return manualBackgroundMask.value || bg;
  }
  if (backgroundMode.value === "all") {
    for (let i = 0; i < total; i += 1) bg[i] = targetMask.value[i] ? 0 : 1;
    return bg;
  }
  const dilated = dilate(targetMask.value, 5);
  for (let i = 0; i < total; i += 1) bg[i] = dilated[i] && !targetMask.value[i] ? 1 : 0;
  return bg;
}

function grayAt(index) {
  const offset = index * 4;
  const data = sourcePixels.value.data;
  return (0.299 * data[offset] + 0.587 * data[offset + 1] + 0.114 * data[offset + 2]) / 255;
}

function stats(values) {
  if (!values.length) return { mean: NaN, std: NaN };
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const variance = values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length;
  return { mean, std: Math.sqrt(variance) };
}

function histogram(values, bins = 32) {
  const hist = new Array(bins).fill(0);
  for (const value of values) {
    const bin = Math.max(0, Math.min(bins - 1, Math.floor(value * bins)));
    hist[bin] += 1;
  }
  const denom = Math.max(1, values.length);
  return hist.map((value) => value / denom);
}

function sobelMagnitude(index) {
  const width = imageWidth.value;
  const height = imageHeight.value;
  const x = index % width;
  const y = Math.floor(index / width);
  if (x === 0 || y === 0 || x === width - 1 || y === height - 1) return 0;
  const g = (xx, yy) => grayAt(yy * width + xx);
  const gx =
    -g(x - 1, y - 1) - 2 * g(x - 1, y) - g(x - 1, y + 1) +
    g(x + 1, y - 1) + 2 * g(x + 1, y) + g(x + 1, y + 1);
  const gy =
    -g(x - 1, y - 1) - 2 * g(x, y - 1) - g(x + 1, y - 1) +
    g(x - 1, y + 1) + 2 * g(x, y + 1) + g(x + 1, y + 1);
  return Math.sqrt(gx * gx + gy * gy);
}

const interactiveMetrics = computed(() => {
  maskVersion.value;
  if (!sourcePixels.value || !targetMask.value) return [];
  const bgMask = currentBackgroundMask();
  const target = [];
  const background = [];
  const gradients = [];
  for (let i = 0; i < targetMask.value.length; i += 1) {
    const gray = grayAt(i);
    gradients.push(sobelMagnitude(i));
    if (targetMask.value[i]) target.push(gray);
    if (bgMask[i]) background.push(gray);
  }
  const targetStats = stats(target);
  const backgroundStats = stats(background);
  const targetHist = histogram(target);
  const backgroundHist = histogram(background);
  const histIntersection = targetHist.reduce(
    (sum, value, index) => sum + Math.min(value, backgroundHist[index]),
    0
  );
  const gradStats = stats(gradients);
  const edgeThreshold = gradStats.mean + gradStats.std;
  const edgeDensity = gradients.filter((value) => value > edgeThreshold).length / gradients.length;
  const meanAbsDiff = Math.abs(targetStats.mean - backgroundStats.mean);
  const contrastAbsDiff = Math.abs(targetStats.std - backgroundStats.std);
  const difficultyScore = Math.max(
    0,
    Math.min(1, 0.5 * histIntersection + 0.3 * (1 - meanAbsDiff) + 0.2 * edgeDensity)
  );
  return [
    ["Target pixels", target.length],
    ["Background pixels", background.length],
    ["Target area", target.length / targetMask.value.length],
    ["Mean abs diff", meanAbsDiff],
    ["Contrast abs diff", contrastAbsDiff],
    ["Histogram overlap", histIntersection],
    ["Edge density", edgeDensity],
    ["Camouflage difficulty", difficultyScore]
  ];
});

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
  await loadBundledIntoEditor(samples[0]);
});
</script>

<template>
  <section class="camo-demo">
    <div class="demo-hero">
      <div>
        <p class="eyebrow">Interactive browser demo</p>
        <h1>Upload. Segment. Choose background. Measure camouflage.</h1>
        <p class="hero-copy">
          This demo runs entirely in the browser for lightweight measurement. Use
          seed-based auto segmentation, manual mask/background brushes, or send the
          image to a SAM3 Space for model-assisted segmentation.
        </p>
      </div>
      <div class="hero-panel">
        <strong>4</strong>
        <span>workflow steps</span>
        <small>image → mask → background → metrics</small>
      </div>
    </div>

    <section class="lab-card">
      <div class="lab-header">
        <div>
          <p class="eyebrow">Try your own image</p>
          <h2>Segmentation and metric lab</h2>
          <p>
            Click the object with Seed auto, refine with brushes, select a background
            rule, then read the target/background metrics immediately.
          </p>
        </div>
        <div class="lab-actions">
          <input class="file-picker" type="file" accept="image/*" @change="onFileUpload" />
          <button
            v-for="sample in samples.slice(0, 2)"
            :key="`quick-${sample.id}`"
            type="button"
            @click="loadBundledIntoEditor(sample)"
          >
            {{ sample.label }}
          </button>
          <a href="https://huggingface.co/spaces/prithivMLmods/SAM3-Demo" target="_blank" rel="noreferrer">Open SAM3</a>
        </div>
      </div>

      <div class="lab-grid">
        <div class="editor-wrap">
          <div class="canvas-shell">
            <canvas
              ref="editorCanvas"
              aria-label="Interactive segmentation canvas"
              @pointerdown="onPointerDown"
              @pointermove="onPointerMove"
              @pointerup="onPointerUp"
              @pointerleave="onPointerUp"
            />
          </div>
          <div class="legend">
            <span><i class="target-dot"></i>target mask</span>
            <span><i class="background-dot"></i>background</span>
            <span>{{ imageName }} · {{ imageWidth }}×{{ imageHeight }}</span>
          </div>
        </div>

        <aside class="controls-card">
          <p class="eyebrow">Controls</p>
          <div class="tool-grid">
            <button type="button" :class="{ active: activeTool === 'seed' }" @click="activeTool = 'seed'">Seed auto</button>
            <button type="button" :class="{ active: activeTool === 'target' }" @click="activeTool = 'target'">Paint target</button>
            <button type="button" :class="{ active: activeTool === 'background' }" @click="activeTool = 'background'; backgroundMode = 'manual'">Paint background</button>
            <button type="button" :class="{ active: activeTool === 'erase' }" @click="activeTool = 'erase'">Erase</button>
          </div>

          <label>
            Auto tolerance
            <input v-model.number="tolerance" type="range" min="8" max="150" />
            <span>{{ tolerance }}</span>
          </label>
          <label>
            Brush size
            <input v-model.number="brushSize" type="range" min="4" max="80" />
            <span>{{ brushSize }}</span>
          </label>
          <label>
            Background mode
            <select v-model="backgroundMode" @change="drawEditor">
              <option value="near">Auto near ring</option>
              <option value="all">Auto all non-target</option>
              <option value="manual">Manual background</option>
            </select>
          </label>

          <div class="control-buttons">
            <button type="button" @click="autoSegment(lastSeed?.x, lastSeed?.y)">Re-run auto</button>
            <button type="button" @click="clearMasks">Clear masks</button>
          </div>

          <p class="control-note">
            Browser auto segmentation is color-connected region growing, not SAM3.
            Use the SAM3 Space link when a model-assisted mask is needed.
          </p>
        </aside>
      </div>

      <div class="interactive-metrics">
        <article v-for="[name, value] in interactiveMetrics" :key="name" class="metric-card">
          <span>{{ name }}</span>
          <strong>{{ formatValue(value) }}</strong>
        </article>
      </div>
    </section>

    <section class="run-strip sam-strip">
      <div>
        <p class="eyebrow">Model-assisted route</p>
        <h2>SAM3 belongs in a backend Space, not static Pages</h2>
        <p>
          GitHub Pages cannot host GPU inference or SAM3 weights. The browser lab
          computes lightweight metrics locally; SAM3 can supply masks through the
          linked Hugging Face Space or a future dedicated CamoGED Space.
        </p>
      </div>
      <a href="https://huggingface.co/spaces/prithivMLmods/SAM3-Demo" target="_blank" rel="noreferrer">SAM3 Demo</a>
      <a href="https://huggingface.co/facebook/sam3" target="_blank" rel="noreferrer">facebook/sam3</a>
      <a href="https://github.com/facebookresearch/sam3" target="_blank" rel="noreferrer">SAM3 code</a>
    </section>

    <section class="execution-ladder">
      <div class="section-title">
        <p class="eyebrow">Execution ladder</p>
        <h2>Choose the surface by compute cost</h2>
        <p>
          The browser handles annotation and lightweight metrics. Anything that needs
          model weights, GPUs, videos, or larger datasets should move to a hosted
          notebook, Codespace, Kaggle runtime, or a dedicated project implementation.
        </p>
      </div>

      <div class="route-grid">
        <article class="route-card">
          <span>01 · Browser</span>
          <h3>Manual and lightweight auto segmentation</h3>
          <p>
            Upload an image, click a seed, paint target/background regions, and compute
            target-background measurements immediately on GitHub Pages.
          </p>
          <ul>
            <li>No login, no backend, no model weights.</li>
            <li>Best for quick camouflage-difficulty inspection.</li>
          </ul>
        </article>

        <article class="route-card">
          <span>02 · HF Space</span>
          <h3>SAM3-assisted masks</h3>
          <p>
            Use SAM3 for text/click/exemplar segmentation, then bring the mask back to
            CamoGED metrics or run a future CamoGED Space with both segmentation and
            measurement in one backend.
          </p>
          <div class="route-links">
            <a href="https://huggingface.co/spaces/prithivMLmods/SAM3-Demo" target="_blank" rel="noreferrer">SAM3 Demo</a>
            <a href="https://huggingface.co/facebook/sam3" target="_blank" rel="noreferrer">Model card</a>
          </div>
        </article>

        <article class="route-card">
          <span>03 · Notebook runtimes</span>
          <h3>Colab, Codespaces, Kaggle</h3>
          <p>
            Use these when the user needs Python, persistent files, GPU/CPU runtime, or
            batch evaluation beyond what a static page can safely run.
          </p>
          <div class="route-links">
            <a href="https://colab.research.google.com/github/MichaelCSHN/CamoGED/blob/main/camo-eval/notebooks/camo_eval_colab_demo.ipynb" target="_blank" rel="noreferrer">Open Colab</a>
            <a href="https://codespaces.new/MichaelCSHN/CamoGED" target="_blank" rel="noreferrer">Open Codespace</a>
            <a href="https://www.kaggle.com/code" target="_blank" rel="noreferrer">Kaggle notebooks</a>
          </div>
        </article>

        <article class="route-card">
          <span>04 · Research implementations</span>
          <h3>Complex segmentation and benchmark work</h3>
          <p>
            Full SAM3 inference, video tracking, promptable concept segmentation, and
            heavyweight benchmark claims should point to the corresponding paper,
            model, and code rather than being hidden behind a fragile static demo.
          </p>
          <div class="route-links">
            <a href="https://ai.meta.com/research/sam3/" target="_blank" rel="noreferrer">Meta SAM3</a>
            <a href="https://arxiv.org/abs/2511.16719" target="_blank" rel="noreferrer">SAM3 paper</a>
            <a href="https://github.com/facebookresearch/sam3" target="_blank" rel="noreferrer">Official repo</a>
          </div>
        </article>
      </div>
    </section>

    <section class="sample-gallery">
      <div class="section-title">
        <p class="eyebrow">Real COD10K samples</p>
        <h2>Choose a bundled benchmark image</h2>
        <p>
          These thumbnails are sampled from `D:\ML\COD_datasets\COD10K-v3`.
          COD10K is an animal/human camouflage dataset and does not provide
          military target classes, so the previous synthetic military examples
          have been removed.
        </p>
      </div>

      <div class="sample-tabs" aria-label="Bundled demo samples">
      <button
        v-for="sample in samples"
        :key="sample.id"
        type="button"
        :class="{ active: selectedId === sample.id }"
        @click="selectedId = sample.id"
      >
        <img :src="asset(`${sample.id}/${sample.scene}`)" :alt="`${sample.label} thumbnail`" />
        <span>{{ sample.label }}</span>
      </button>
      </div>
    </section>

    <div class="demo-layout">
      <article class="visual-card">
        <div class="card-heading">
          <div>
            <p class="eyebrow">Bundled benchmark-style example</p>
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
            <img :src="asset(`${selectedSample.id}/${selectedSample.pred}`)" alt="Prediction mask" />
            <figcaption>Prediction</figcaption>
          </figure>
          <figure>
            <img :src="asset(`${selectedSample.id}/${selectedSample.gt}`)" alt="Ground-truth mask" />
            <figcaption>Ground truth</figcaption>
          </figure>
          <figure>
            <img :src="asset(`${selectedSample.id}/mask_overlay.png`)" alt="Mask overlay visualization" />
            <figcaption>Overlay</figcaption>
          </figure>
          <figure>
            <img :src="asset(`${selectedSample.id}/error_map.png`)" alt="Error map visualization" />
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
        <p class="eyebrow">Bundled metric browser</p>
        <h2>What the repository sample computes</h2>
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
.lab-header h2,
.section-title h2,
.run-strip h2,
.visual-card h2 {
  margin: 0;
  color: #17251f;
  line-height: 1.04;
}

.demo-hero h1 {
  max-width: 780px;
  font-size: clamp(38px, 6vw, 72px);
  letter-spacing: -0.06em;
}

.hero-copy {
  max-width: 760px;
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

.lab-card,
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

.lab-card {
  padding: 24px;
}

.lab-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: start;
  margin-bottom: 20px;
}

.lab-header p {
  max-width: 760px;
  margin: 10px 0 0;
  color: #5d685f;
}

.lab-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

button,
.lab-actions a,
.run-strip a {
  border: 0;
  border-radius: 999px;
  padding: 10px 16px;
  background: #1d3529;
  color: #fff9e8;
  cursor: pointer;
  font: inherit;
  font-weight: 800;
  text-decoration: none;
}

.lab-actions button {
  background: #e8efe2;
  color: #1d3529;
}

.file-picker {
  max-width: 260px;
  border: 1px solid rgba(29, 53, 41, 0.22);
  border-radius: 999px;
  padding: 8px;
  background: #fffdf7;
  color: #1d3529;
  font-weight: 800;
}

.file-picker::file-selector-button {
  margin-right: 10px;
  border: 0;
  border-radius: 999px;
  padding: 8px 12px;
  background: #1d3529;
  color: #fff9e8;
  cursor: pointer;
  font: inherit;
  font-weight: 800;
}

.lab-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 20px;
}

.canvas-shell {
  overflow: hidden;
  border: 1px solid rgba(39, 59, 49, 0.14);
  border-radius: 22px;
  background: #e7ece0;
}

canvas {
  display: block;
  width: 100%;
  max-height: 70vh;
  object-fit: contain;
  touch-action: none;
  cursor: crosshair;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
  color: #5f6b62;
  font-size: 13px;
  font-weight: 700;
}

.legend i {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 6px;
  border-radius: 999px;
}

.target-dot {
  background: #f8b023;
}

.background-dot {
  background: #286ed2;
}

.controls-card {
  padding: 18px;
  border-radius: 22px;
  background: #eef3e7;
}

.tool-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.tool-grid button,
.control-buttons button {
  background: #fffdf7;
  color: #23362d;
}

.tool-grid button.active {
  background: #1d3529;
  color: #fff9e8;
}

.controls-card label {
  display: grid;
  gap: 6px;
  margin-top: 14px;
  color: #3f5047;
  font-weight: 800;
}

.controls-card input,
.controls-card select {
  width: 100%;
}

.control-buttons {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.control-note {
  margin: 14px 0 0;
  color: #687268;
  font-size: 13px;
  line-height: 1.5;
}

.interactive-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 20px;
}

.sample-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.sample-gallery {
  display: grid;
  gap: 16px;
}

.sample-tabs button {
  display: grid;
  gap: 8px;
  border: 1px solid rgba(72, 91, 79, 0.22);
  border-radius: 18px;
  padding: 8px;
  background: #f6f3ea;
  color: #26362e;
  text-align: left;
}

.sample-tabs button.active {
  border-color: #1d3529;
  background: #e8efe2;
  color: #17251f;
  box-shadow: 0 14px 32px rgba(29, 53, 41, 0.18);
}

.sample-tabs img {
  width: 100%;
  aspect-ratio: 1.35 / 1;
  border-radius: 12px;
  object-fit: cover;
}

.sample-tabs span {
  padding: 0 4px 4px;
  font-size: 13px;
  font-weight: 900;
}

.demo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 22px;
}

.visual-card,
.metric-panel {
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
  font-size: 28px;
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

.execution-ladder {
  display: grid;
  gap: 18px;
}

.section-title p:last-child {
  max-width: 820px;
  margin: 10px 0 0;
  color: #5f6b62;
}

.group-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.route-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.group-card,
.route-card {
  padding: 18px;
}

.route-card {
  border: 1px solid rgba(39, 59, 49, 0.14);
  border-radius: 24px;
  background: #fffdf7;
  box-shadow: 0 18px 60px rgba(28, 48, 38, 0.08);
}

.route-card span {
  color: #58715b;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.group-card h3,
.route-card h3 {
  margin: 0 0 14px;
  color: #17251f;
}

.route-card h3 {
  margin-top: 8px;
}

.route-card p,
.route-card li {
  color: #5d685f;
  line-height: 1.55;
}

.route-card ul {
  margin: 12px 0 0;
  padding-left: 18px;
}

.route-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.route-links a {
  border-radius: 999px;
  padding: 8px 12px;
  background: #e8efe2;
  color: #1d3529;
  font-size: 13px;
  font-weight: 800;
  text-decoration: none;
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

.run-strip p {
  margin: 8px 0 0;
  color: #5f6b62;
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
  .lab-header,
  .lab-grid,
  .demo-layout,
  .run-strip {
    grid-template-columns: 1fr;
  }

  .lab-actions {
    justify-content: flex-start;
  }

  .group-grid,
  .route-grid,
  .sample-tabs,
  .interactive-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .demo-hero,
  .lab-card,
  .visual-card,
  .metric-panel,
  .run-strip,
  .command-card {
    padding: 16px;
    border-radius: 20px;
  }

  .image-grid,
  .group-grid,
  .route-grid,
  .sample-tabs,
  .interactive-metrics {
    grid-template-columns: 1fr;
  }

  figure.wide {
    grid-column: span 1;
  }
}
</style>
