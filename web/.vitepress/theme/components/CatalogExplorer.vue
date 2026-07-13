<script setup>
import { computed, onMounted, ref } from "vue";
import { withBase } from "vitepress";

const loading = ref(true);
const error = ref("");
const resources = ref([]);
const coverageThrough = ref("");
const lastHumanReview = ref("");

const query = ref("");
const task = ref("");
const modality = ref("");
const supervision = ref("");
const context = ref("");
const resourceType = ref("");
const verification = ref("");
const yearFrom = ref("");
const curatedOnly = ref(false);
const codeOnly = ref(false);

function list(item, field) {
  const value = item?.[field];
  if (Array.isArray(value)) return value.map(String);
  return value == null || value === "" ? [] : [String(value)];
}

function options(field) {
  return computed(() => {
    const values = new Set();
    for (const item of resources.value) {
      for (const value of list(item, field)) values.add(value);
    }
    return [...values].sort((a, b) => a.localeCompare(b));
  });
}

const tasks = options("tasks");
const modalities = options("modalities");
const supervisionOptions = options("supervision");
const contexts = options("contexts");
const resourceTypes = options("resource_type");
const verificationOptions = options("verification_status");
const years = computed(() =>
  [...new Set(resources.value.map((item) => Number(item.year)).filter(Boolean))].sort((a, b) => b - a),
);

const filtered = computed(() => {
  const needle = query.value.trim().toLowerCase();
  const minimumYear = Number(yearFrom.value || 0);
  return resources.value.filter((item) => {
    const searchable = [
      item.title,
      item.authors,
      item.venue,
      item.description,
      ...list(item, "tasks"),
      ...list(item, "modalities"),
      ...list(item, "supervision"),
      ...list(item, "contexts"),
      ...list(item, "method_families"),
    ]
      .join(" ")
      .toLowerCase();
    if (needle && !searchable.includes(needle)) return false;
    if (task.value && !list(item, "tasks").includes(task.value)) return false;
    if (modality.value && !list(item, "modalities").includes(modality.value)) return false;
    if (supervision.value && !list(item, "supervision").includes(supervision.value)) return false;
    if (context.value && !list(item, "contexts").includes(context.value)) return false;
    if (resourceType.value && item.resource_type !== resourceType.value) return false;
    if (verification.value && item.verification_status !== verification.value) return false;
    if (minimumYear && Number(item.year || 0) < minimumYear) return false;
    if (curatedOnly.value && item.curated !== true) return false;
    if (codeOnly.value && !item.code) return false;
    return true;
  });
});

function reset() {
  query.value = "";
  task.value = "";
  modality.value = "";
  supervision.value = "";
  context.value = "";
  resourceType.value = "";
  verification.value = "";
  yearFrom.value = "";
  curatedOnly.value = false;
  codeOnly.value = false;
}

onMounted(async () => {
  try {
    const response = await fetch(withBase("/catalog.json"), { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    resources.value = Array.isArray(payload.resources) ? payload.resources : [];
    coverageThrough.value = payload.coverage_through || "";
    lastHumanReview.value = payload.last_human_review || "";
  } catch (cause) {
    error.value = `Catalog data could not be loaded (${cause.message}). Use the static fallback below.`;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="catalog-explorer" aria-labelledby="catalog-explorer-title">
    <div class="catalog-heading">
      <div>
        <p class="eyebrow">Interactive accepted-metadata view</p>
        <h2 id="catalog-explorer-title">Filter the research catalog</h2>
      </div>
      <p class="catalog-meta">
        Coverage: <strong>{{ coverageThrough || "loading" }}</strong><br />
        Human review: <strong>{{ lastHumanReview || "loading" }}</strong>
      </p>
    </div>

    <p v-if="loading">Loading catalog data…</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>

    <template v-else>
      <form class="filters" @submit.prevent>
        <label class="wide">
          Search title, author, venue, description, or tag
          <input v-model="query" type="search" placeholder="e.g. SAM2, tracking, biological" />
        </label>
        <label>Task<select v-model="task"><option value="">All</option><option v-for="value in tasks" :key="value">{{ value }}</option></select></label>
        <label>Modality<select v-model="modality"><option value="">All</option><option v-for="value in modalities" :key="value">{{ value }}</option></select></label>
        <label>Supervision<select v-model="supervision"><option value="">All</option><option v-for="value in supervisionOptions" :key="value">{{ value }}</option></select></label>
        <label>Context<select v-model="context"><option value="">All</option><option v-for="value in contexts" :key="value">{{ value }}</option></select></label>
        <label>Resource type<select v-model="resourceType"><option value="">All</option><option v-for="value in resourceTypes" :key="value">{{ value }}</option></select></label>
        <label>Verification<select v-model="verification"><option value="">All</option><option v-for="value in verificationOptions" :key="value">{{ value }}</option></select></label>
        <label>Published since<select v-model="yearFrom"><option value="">Any year</option><option v-for="value in years" :key="value" :value="value">{{ value }}</option></select></label>
        <label class="check"><input v-model="curatedOnly" type="checkbox" /> Curated only</label>
        <label class="check"><input v-model="codeOnly" type="checkbox" /> Code/project link</label>
        <button type="button" class="reset" @click="reset">Reset filters</button>
      </form>

      <p class="count" aria-live="polite"><strong>{{ filtered.length }}</strong> of {{ resources.length }} accepted records</p>

      <div class="cards">
        <article v-for="item in filtered" :key="item.id" class="card">
          <div class="card-title">
            <h3>{{ item.title }}</h3>
            <span>{{ item.year || "n.d." }}</span>
          </div>
          <p class="byline">{{ item.authors }} · {{ item.venue }}</p>
          <p>{{ item.description }}</p>
          <div class="badges">
            <span>{{ item.resource_type }}</span>
            <span>{{ item.publication_status }}</span>
            <span>{{ item.verification_status }}</span>
            <span v-if="item.curated">curated</span>
          </div>
          <p class="tags"><strong>Tasks:</strong> {{ list(item, "tasks").join(", ") }}</p>
          <p class="tags"><strong>Modalities:</strong> {{ list(item, "modalities").join(", ") }}</p>
          <p class="tags"><strong>Supervision:</strong> {{ list(item, "supervision").join(", ") }}</p>
          <p class="tags"><strong>Contexts:</strong> {{ list(item, "contexts").join(", ") }}</p>
          <p class="links">
            <a v-if="item.paper" :href="item.paper" target="_blank" rel="noreferrer">Primary/source record</a>
            <a v-if="item.code" :href="item.code" target="_blank" rel="noreferrer">Code/project</a>
          </p>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.catalog-explorer { margin: 1.5rem 0 2rem; }
.catalog-heading { display: flex; gap: 1.5rem; justify-content: space-between; align-items: flex-start; }
.catalog-heading h2 { margin-top: 0; }
.eyebrow { margin: 0 0 .25rem; font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .7; }
.catalog-meta { margin: 0; text-align: right; font-size: .86rem; }
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .8rem; padding: 1rem; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); }
.filters label { display: grid; gap: .3rem; font-size: .8rem; font-weight: 600; }
.filters .wide { grid-column: 1 / -1; }
.filters input[type="search"], .filters select { width: 100%; padding: .55rem .65rem; border: 1px solid var(--vp-c-divider); border-radius: 7px; background: var(--vp-c-bg); color: var(--vp-c-text-1); }
.filters .check { display: flex; align-items: center; gap: .45rem; }
.reset { align-self: end; padding: .58rem .75rem; border: 1px solid var(--vp-c-brand-1); border-radius: 7px; background: transparent; color: var(--vp-c-brand-1); cursor: pointer; }
.count { margin: 1rem 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.card { padding: 1rem; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); }
.card-title { display: flex; gap: .8rem; justify-content: space-between; }
.card-title h3 { margin: 0; font-size: 1rem; }
.byline, .tags { font-size: .82rem; opacity: .82; }
.badges { display: flex; flex-wrap: wrap; gap: .35rem; margin: .75rem 0; }
.badges span { padding: .15rem .45rem; border: 1px solid var(--vp-c-divider); border-radius: 999px; font-size: .72rem; }
.links { display: flex; flex-wrap: wrap; gap: .8rem; margin-bottom: 0; }
.error { padding: .8rem; border: 1px solid var(--vp-c-danger-1); border-radius: 8px; }
@media (max-width: 640px) { .catalog-heading { display: block; } .catalog-meta { text-align: left; } }
</style>
