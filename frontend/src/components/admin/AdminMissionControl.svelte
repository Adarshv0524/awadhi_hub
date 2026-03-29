<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  type GovernanceChecklist = {
    pii_minimization: string;
    retention_policy: string;
    row_level_controls: string;
    immutable_model_trail: string;
    review_ready: boolean;
  };

  let loading = true;
  let error: string | null = null;
  let governance: GovernanceChecklist | null = null;
  let triageCount = 0;
  let highConfidence = 0;

  async function load() {
    loading = true;
    error = null;
    try {
      const [checklist, triage] = await Promise.all([
        api<GovernanceChecklist>("/api/v1/governance/checklist"),
        api<any[]>("/api/v1/ai/moderation-triage?limit=100"),
      ]);

      governance = checklist;
      const triageRows = Array.isArray(triage) ? triage : [];
      triageCount = triageRows.length;
      highConfidence = triageRows.filter((t) => Number(t?.confidence || 0) >= 0.8).length;
    } catch (e: any) {
      error = e?.message || "Failed to load mission-control insights";
      governance = null;
      triageCount = 0;
      highConfidence = 0;
    } finally {
      loading = false;
    }
  }

  function statusTone(value: string | undefined): "positive" | "warning" {
    return String(value || "").toLowerCase() === "ok" ? "positive" : "warning";
  }

  onMount(load);
</script>

<section class="admin-panel p-5">
  <div class="mb-4 flex items-center justify-between gap-2">
    <div>
      <h2 class="text-xl font-semibold text-slate-100">Mission Control</h2>
      <p class="text-sm text-slate-400">Decision intelligence, governance posture, and AI-ops runway in one glance.</p>
    </div>
    <button class="admin-btn" on:click={load}>Refresh</button>
  </div>

  {#if loading}
    <p class="text-sm text-slate-400">Loading mission-control intelligence...</p>
  {:else if error}
    <p class="text-sm admin-state-bad">{error}</p>
  {:else}
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="admin-kpi">
        <p class="admin-kpi-label">AI Triage Queue</p>
        <p class="admin-kpi-value">{triageCount}</p>
        <p class="mt-1 text-xs text-slate-400">{highConfidence} high-confidence suggestions</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">Human-In-Loop Coverage</p>
        <p class="admin-kpi-value">100%</p>
        <p class="mt-1 text-xs text-slate-400">Irreversible actions require explicit human approval</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">Governance Review Readiness</p>
        <p class="admin-kpi-value">{governance?.review_ready ? "Ready" : "Needs Work"}</p>
        <p class="mt-1 text-xs text-slate-400">PII, retention, RLS, and immutable model trail</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">Future Agent Readiness</p>
        <p class="admin-kpi-value">Scaffolded</p>
        <p class="mt-1 text-xs text-slate-400">Telemetry contracts + model-decision logs are in place</p>
      </div>
    </div>

    {#if governance}
      <div class="mt-4 flex flex-wrap gap-2 text-xs">
        <span class="ui-badge" data-tone={statusTone(governance.pii_minimization)}>PII minimization: {governance.pii_minimization}</span>
        <span class="ui-badge" data-tone={statusTone(governance.retention_policy)}>Retention: {governance.retention_policy}</span>
        <span class="ui-badge" data-tone={statusTone(governance.row_level_controls)}>RLS controls: {governance.row_level_controls}</span>
        <span class="ui-badge" data-tone={statusTone(governance.immutable_model_trail)}>Model trail: {governance.immutable_model_trail}</span>
      </div>
    {/if}
  {/if}
</section>
