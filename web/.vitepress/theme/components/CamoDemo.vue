<script setup>
import { computed, nextTick, onMounted, ref } from "vue";

const canvasRef = ref(null);
const width = ref(560);
const height = ref(340);
const source = ref(null);
const mask = ref(null);
const seed = ref(null);
const tool = ref("seed");
const tolerance = ref(42);
const brush = ref(16);
const version = ref(0);
const label = ref("Synthetic bark scene");

function makeScene(kind) {
  const canvas = document.createElement("canvas");
  canvas.width = width.value;
  canvas.height = height.value;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const gradient = ctx.createLinearGradient(0, 0, width.value, height.value);
  if (kind === "bark") {
    gradient.addColorStop(0, "#5f5a49");
    gradient.addColorStop(1, "#81765d");
  } else if (kind === "leaf") {
    gradient.addColorStop(0, "#5b774f");
    gradient.addColorStop(1, "#8f9b62");
  } else {
    gradient.addColorStop(0, "#77878a");
    gradient.addColorStop(1, "#a0a59b");
  }
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width.value, height.value);
  const rng = mulberry32(kind === "bark" ? 13 : kind === "leaf" ? 29 : 41);
  for (let i = 0; i < 900; i += 1) {
    const value = 55 + Math.floor(rng() * 90);
    ctx.fillStyle = `rgba(${value},${value + 8},${Math.max(30, value - 15)},0.20)`;
    ctx.fillRect(rng() * width.value, rng() * height.value, 1 + rng() * 9, 1 + rng() * 3);
  }
  const target = new Uint8Array(width.value * height.value);
  const cx = width.value * 0.58;
  const cy = height.value * 0.52;
  const rx = kind === "leaf" ? 88 : 72;
  const ry = kind === "leaf" ? 44 : 62;
  ctx.fillStyle = kind === "bark" ? "rgba(102,96,76,0.96)" : kind === "leaf" ? "rgba(105,126,74,0.96)" : "rgba(132,142,136,0.96)";
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, kind === "leaf" ? -0.45 : 0.15, 0, Math.PI * 2);
  ctx.fill();
  for (let y = 0; y < height.value; y += 1) {
    for (let x = 0; x < width.value; x += 1) {
      const cos = Math.cos(kind === "leaf" ? -0.45 : 0.15);
      const sin = Math.sin(kind === "leaf" ? -0.45 : 0.15);
      const dx = x - cx;
      const dy = y - cy;
      const xr = dx * cos + dy * sin;
      const yr = -dx * sin + dy * cos;
      if ((xr * xr) / (rx * rx) + (yr * yr) / (ry * ry) <= 1) target[y * width.value + x] = 1;
    }
  }
  return { pixels: ctx.getImageData(0, 0, width.value, height.value), target };
}

function mulberry32(seedValue) {
  return function random() {
    let value = (seedValue += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

async function loadSynthetic(kind) {
  label.value = `Synthetic ${kind} scene`;
  const generated = makeScene(kind);
  source.value = generated.pixels;
  mask.value = generated.target;
  seed.value = null;
  version.value += 1;
  await nextTick();
  draw();
}

async function upload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  try {
    const image = await new Promise((resolve, reject) => {
      const item = new Image();
      item.onload = () => resolve(item);
      item.onerror = reject;
      item.src = url;
    });
    const scale = Math.min(1, 720 / Math.max(image.width, image.height));
    width.value = Math.max(1, Math.round(image.width * scale));
    height.value = Math.max(1, Math.round(image.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width.value;
    canvas.height = height.value;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(image, 0, 0, width.value, height.value);
    source.value = ctx.getImageData(0, 0, width.value, height.value);
    mask.value = new Uint8Array(width.value * height.value);
    seed.value = { x: Math.floor(width.value / 2), y: Math.floor(height.value / 2) };
    label.value = file.name;
    version.value += 1;
    await nextTick();
    draw();
  } finally {
    URL.revokeObjectURL(url);
    event.target.value = "";
  }
}

function point(event) {
  const rect = canvasRef.value.getBoundingClientRect();
  return {
    x: Math.floor(((event.clientX - rect.left) / rect.width) * width.value),
    y: Math.floor(((event.clientY - rect.top) / rect.height) * height.value),
  };
}

function regionGrow(x, y) {
  if (!source.value) return;
  const data = source.value.data;
  const start = y * width.value + x;
  const base = [data[start * 4], data[start * 4 + 1], data[start * 4 + 2]];
  const visited = new Uint8Array(width.value * height.value);
  const result = new Uint8Array(width.value * height.value);
  const queue = [start];
  visited[start] = 1;
  for (let head = 0; head < queue.length; head += 1) {
    const index = queue[head];
    const offset = index * 4;
    const distance = Math.hypot(data[offset] - base[0], data[offset + 1] - base[1], data[offset + 2] - base[2]);
    if (distance > tolerance.value) continue;
    result[index] = 1;
    const px = index % width.value;
    const py = Math.floor(index / width.value);
    for (const [nx, ny] of [[px - 1, py], [px + 1, py], [px, py - 1], [px, py + 1]]) {
      if (nx < 0 || nx >= width.value || ny < 0 || ny >= height.value) continue;
      const next = ny * width.value + nx;
      if (!visited[next]) {
        visited[next] = 1;
        queue.push(next);
      }
    }
  }
  mask.value = result;
  version.value += 1;
  draw();
}

let painting = false;
function pointerDown(event) {
  const p = point(event);
  if (tool.value === "seed") {
    seed.value = p;
    regionGrow(p.x, p.y);
    return;
  }
  painting = true;
  paint(p.x, p.y);
}
function pointerMove(event) {
  if (!painting) return;
  const p = point(event);
  paint(p.x, p.y);
}
function pointerUp() { painting = false; }
function paint(x, y) {
  const radius = Math.max(1, Math.round(brush.value / 2));
  for (let yy = y - radius; yy <= y + radius; yy += 1) {
    for (let xx = x - radius; xx <= x + radius; xx += 1) {
      if (xx < 0 || yy < 0 || xx >= width.value || yy >= height.value) continue;
      if ((xx - x) ** 2 + (yy - y) ** 2 > radius ** 2) continue;
      mask.value[yy * width.value + xx] = tool.value === "paint" ? 1 : 0;
    }
  }
  version.value += 1;
  draw();
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas || !source.value || !mask.value) return;
  canvas.width = width.value;
  canvas.height = height.value;
  const data = new Uint8ClampedArray(source.value.data);
  for (let i = 0; i < mask.value.length; i += 1) {
    if (!mask.value[i]) continue;
    data[i * 4] = Math.round(data[i * 4] * 0.45 + 245 * 0.55);
    data[i * 4 + 1] = Math.round(data[i * 4 + 1] * 0.45 + 165 * 0.55);
    data[i * 4 + 2] = Math.round(data[i * 4 + 2] * 0.45 + 35 * 0.55);
  }
  canvas.getContext("2d").putImageData(new ImageData(data, width.value, height.value), 0, 0);
}

function gray(index) {
  const data = source.value.data;
  return (0.299 * data[index * 4] + 0.587 * data[index * 4 + 1] + 0.114 * data[index * 4 + 2]) / 255;
}
function histogram(values, bins = 24) {
  const output = new Array(bins).fill(0);
  values.forEach((value) => output[Math.min(bins - 1, Math.floor(value * bins))]++);
  return output.map((value) => value / Math.max(1, values.length));
}
const metrics = computed(() => {
  version.value;
  if (!source.value || !mask.value) return null;
  const target = [];
  const background = [];
  for (let i = 0; i < mask.value.length; i += 1) (mask.value[i] ? target : background).push(gray(i));
  if (!target.length || !background.length) return null;
  const mean = (values) => values.reduce((sum, value) => sum + value, 0) / values.length;
  const tMean = mean(target);
  const bMean = mean(background);
  const tHist = histogram(target);
  const bHist = histogram(background);
  const overlap = tHist.reduce((sum, value, index) => sum + Math.min(value, bHist[index]), 0);
  const meanDifference = Math.abs(tMean - bMean);
  const exploratory = Math.max(0, Math.min(1, 0.65 * overlap + 0.35 * (1 - meanDifference)));
  return { target: target.length, overlap, meanDifference, exploratory };
});

onMounted(() => loadSynthetic("bark"));
</script>

<template>
  <main class="demo">
    <header>
      <p class="eyebrow">Synthetic teaching demo</p>
      <h1>Explore target–background similarity</h1>
      <p>
        This page uses deterministic synthetic scenes or an image kept locally in your browser.
        It is not a COD model, not a benchmark, and not a standard camo-eval score.
      </p>
    </header>

    <section class="controls">
      <button @click="loadSynthetic('bark')">Synthetic bark</button>
      <button @click="loadSynthetic('leaf')">Synthetic leaf</button>
      <button @click="loadSynthetic('stone')">Synthetic stone</button>
      <label class="upload">Upload local image <input type="file" accept="image/*" @change="upload" /></label>
    </section>

    <section class="workspace">
      <div>
        <canvas ref="canvasRef" @pointerdown="pointerDown" @pointermove="pointerMove" @pointerup="pointerUp" @pointerleave="pointerUp" />
        <p>{{ label }} · orange overlay = current target mask</p>
      </div>
      <aside>
        <label>Tool
          <select v-model="tool">
            <option value="seed">Seeded colour region</option>
            <option value="paint">Paint target</option>
            <option value="erase">Erase mask</option>
          </select>
        </label>
        <label>Region tolerance <input v-model.number="tolerance" type="range" min="5" max="150" /></label>
        <label>Brush size <input v-model.number="brush" type="range" min="4" max="60" /></label>
        <button v-if="seed" @click="regionGrow(seed.x, seed.y)">Re-run seeded region</button>
      </aside>
    </section>

    <section class="results">
      <h2>Exploratory diagnostics</h2>
      <div v-if="metrics" class="grid">
        <article><strong>{{ metrics.target }}</strong><span>target pixels</span></article>
        <article><strong>{{ metrics.overlap.toFixed(3) }}</strong><span>grayscale histogram overlap</span></article>
        <article><strong>{{ metrics.meanDifference.toFixed(3) }}</strong><span>mean luminance difference</span></article>
        <article><strong>{{ metrics.exploratory.toFixed(3) }}</strong><span>exploratory heuristic</span></article>
      </div>
      <p class="warning">
        The heuristic combines histogram overlap and luminance similarity. It has no claim to human detectability,
        ecological fitness, detector failure, or mission effectiveness. Use validated metrics and a declared protocol for research reporting.
      </p>
    </section>
  </main>
</template>

<style scoped>
.demo { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 4rem; }
.eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; }
.controls { display: flex; flex-wrap: wrap; gap: .7rem; margin: 1.5rem 0; }
button, .upload, select { border: 1px solid var(--vp-c-divider); border-radius: 8px; padding: .65rem .85rem; background: var(--vp-c-bg-soft); }
.upload input { display: block; margin-top: .45rem; }
.workspace { display: grid; grid-template-columns: minmax(0, 1fr) 260px; gap: 1rem; }
canvas { width: 100%; max-height: 620px; object-fit: contain; border-radius: 10px; border: 1px solid var(--vp-c-divider); touch-action: none; }
aside { display: grid; align-content: start; gap: 1rem; padding: 1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; }
aside label { display: grid; gap: .4rem; }
.results { margin-top: 2rem; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; }
article { padding: 1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; }
article strong, article span { display: block; }
article strong { font-size: 1.5rem; }
.warning { padding: 1rem; border-left: 4px solid var(--vp-c-warning-1); background: var(--vp-c-warning-soft); }
@media (max-width: 760px) { .workspace { grid-template-columns: 1fr; } .grid { grid-template-columns: 1fr 1fr; } }
</style>
