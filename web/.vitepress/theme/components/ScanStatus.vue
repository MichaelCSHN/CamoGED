<script setup>
import { onMounted, ref } from "vue";
const status = ref("Loading latest scan status…");
const url = ref("https://github.com/MichaelCSHN/CamoGED/issues?q=label%3Aawesome%3Atriage");
onMounted(async () => {
  try {
    const response = await fetch("https://api.github.com/repos/MichaelCSHN/CamoGED/issues?labels=awesome%3Atriage&state=all&per_page=1&sort=created&direction=desc");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const issues = await response.json();
    if (!issues.length) {
      status.value = "No scheduled triage issue has been published yet.";
      return;
    }
    const issue = issues[0];
    status.value = `Latest automated scan issue: ${issue.title} (${issue.created_at.slice(0, 10)})`;
    url.value = issue.html_url;
  } catch (exc) {
    status.value = "Live scan status is temporarily unavailable; open the GitHub triage list.";
  }
});
</script>

<template><p class="scan-status"><a :href="url">{{ status }}</a></p></template>
<style scoped>.scan-status { padding: .75rem 1rem; border-left: 4px solid var(--vp-c-brand-1); background: var(--vp-c-bg-soft); }</style>
