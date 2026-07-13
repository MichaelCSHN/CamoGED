<script setup>
import { onMounted, ref } from "vue";

const loading = ref(true);
const error = ref("");
const issue = ref(null);
const issueSearch = "https://github.com/MichaelCSHN/CamoGED/issues?q=label%3Aawesome%3Atriage";
const apiUrl = "https://api.github.com/repos/MichaelCSHN/CamoGED/issues?state=all&labels=awesome%3Atriage&sort=created&direction=desc&per_page=1";
const cacheKey = "camoged-awesome-scan-status-v1";
const maxAgeMs = 30 * 60 * 1000;

function usePayload(payload) {
  issue.value = payload?.issue || null;
}

onMounted(async () => {
  try {
    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      const payload = JSON.parse(cached);
      if (Date.now() - Number(payload.cached_at || 0) < maxAgeMs) {
        usePayload(payload);
        loading.value = false;
        return;
      }
    }

    const response = await fetch(apiUrl, {
      headers: { Accept: "application/vnd.github+json" },
    });
    if (!response.ok) throw new Error(`GitHub API HTTP ${response.status}`);
    const records = await response.json();
    const latest = Array.isArray(records) && records.length ? records[0] : null;
    const payload = {
      cached_at: Date.now(),
      issue: latest
        ? {
            number: latest.number,
            title: latest.title,
            state: latest.state,
            created_at: latest.created_at,
            updated_at: latest.updated_at,
            html_url: latest.html_url,
          }
        : null,
    };
    sessionStorage.setItem(cacheKey, JSON.stringify(payload));
    usePayload(payload);
  } catch (cause) {
    error.value = cause.message;
  } finally {
    loading.value = false;
  }
});

function formatDate(value) {
  if (!value) return "unknown";
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
</script>

<template>
  <aside class="scan-status" aria-live="polite">
    <div>
      <p class="eyebrow">Live maintenance signal</p>
      <h2>Latest automated Awesome scan</h2>
    </div>
    <p v-if="loading">Checking the public triage queue…</p>
    <template v-else-if="issue">
      <p>
        <strong>{{ formatDate(issue.created_at) }}</strong> · issue #{{ issue.number }} ·
        <span class="state">{{ issue.state }}</span>
      </p>
      <p>{{ issue.title }}</p>
      <p><a :href="issue.html_url" target="_blank" rel="noreferrer">Open the latest triage report</a></p>
    </template>
    <template v-else>
      <p>
        No triage issue could be displayed<span v-if="error"> ({{ error }})</span>. This widget uses the
        public GitHub API and may be rate-limited; it does not affect the scheduled scanner.
      </p>
      <p><a :href="issueSearch" target="_blank" rel="noreferrer">Browse all Awesome triage issues</a></p>
    </template>
    <p class="note">Candidate discovery is automatic. Acceptance, substantive verification, and curated promotion remain human decisions.</p>
  </aside>
</template>

<style scoped>
.scan-status { margin: 1.5rem 0; padding: 1rem 1.1rem; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); }
.scan-status h2 { margin: 0 0 .6rem; font-size: 1.15rem; }
.eyebrow { margin: 0 0 .2rem; font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .7; }
.state { padding: .12rem .4rem; border: 1px solid var(--vp-c-divider); border-radius: 999px; font-size: .75rem; }
.note { margin-bottom: 0; font-size: .82rem; opacity: .8; }
</style>
