<script setup>
import { computed, onMounted, ref } from "vue";

const records = ref([]);
const query = ref("");
const task = ref("");
const modality = ref("");
const context = ref("");
const error = ref("");

onMounted(async () => {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}catalog-data.json`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    records.value = await response.json();
  } catch (exc) {
    error.value = `Catalog data could not be loaded: ${exc}`;
  }
});

const values = (field) => [...new Set(records.value.flatMap((item) => item[field] || []))].sort();
const tasks = computed(() => values("tasks"));
const modalities = computed(() => values("modalities"));
const contexts = computed(() => values("contexts"));
const filtered = computed(() => {
  const needle = query.value.trim().toLowerCase();
  return records.value.filter((item) => {
    const haystack = [item.title, item.description, ...(item.tasks || []), ...(item.contexts || [])].join(" ").toLowerCase();
    return (!needle || haystack.includes(needle)) &&
      (!task.value || (item.tasks || []).includes(task.value)) &&
      (!modality.value || (item.modalities || []).includes(modality.value)) &&
      (!context.value || (item.contexts || []).includes(context.value));
  });
});
</script>

<template>
  <div class="catalog-explorer">
    <div class="catalog-controls">
      <input v-model="query" aria-label="Search catalog" placeholder="Search title, description, or tag" />
      <select v-model="task" aria-label="Filter by task"><option value="">All tasks</option><option v-for="value in tasks" :key="value">{{ value }}</option></select>
      <select v-model="modality" aria-label="Filter by modality"><option value="">All modalities</option><option v-for="value in modalities" :key="value">{{ value }}</option></select>
      <select v-model="context" aria-label="Filter by context"><option value="">All contexts</option><option v-for="value in contexts" :key="value">{{ value }}</option></select>
    </div>
    <p v-if="error">{{ error }}</p>
    <p v-else><strong>{{ filtered.length }}</strong> of {{ records.length }} accepted records</p>
    <details v-for="item in filtered.slice(0, 100)" :key="item.id">
      <summary>{{ item.year }} · {{ item.title }}</summary>
      <p>{{ item.description }}</p>
      <p><code>{{ (item.tasks || []).join(", ") }}</code></p>
      <p><a :href="item.paper">Source</a><span v-if="item.code"> · <a :href="item.code">Code/project</a></span></p>
    </details>
  </div>
</template>

<style scoped>
.catalog-controls { display: grid; grid-template-columns: 2fr repeat(3, 1fr); gap: .6rem; margin: 1rem 0; }
.catalog-controls input, .catalog-controls select { border: 1px solid var(--vp-c-divider); border-radius: 6px; padding: .55rem; background: var(--vp-c-bg); color: var(--vp-c-text-1); }
details { border-top: 1px solid var(--vp-c-divider); padding: .55rem 0; }
@media (max-width: 800px) { .catalog-controls { grid-template-columns: 1fr; } }
</style>
