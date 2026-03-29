<script lang="ts">
  import { onMount } from "svelte";

  import { fetchAdminSloSummary, type AdminSloSummary } from "../../lib/observability";

  let loading = true;
  let error: string | null = null;
  let summary: AdminSloSummary | null = null;
  let windowMinutes = 60;

  async function load() {
    loading = true;
    error = null;
    try {
      summary = await fetchAdminSloSummary(windowMinutes);
    } catch (e: any) {
      error = e?.message || "Failed to load admin SLO metrics";
      summary = null;
    } finally {
      loading = false;
    }
  }

  function formatPercent(value: number): string {
    return `${value.toFixed(2)}%`;
  }

  onMount(load);
</script>

<section class="admin-panel p-4 md:p-5">
  <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <div>
      <h2 class="text-lg font-semibold text-slate-100">Admin SLO Signals</h2>
      <p class="text-sm text-slate-400">Error rate, p95 latency, and action success rate from centralized telemetry.</p>
    </div>

    <div class="flex items-center gap-2">
      <label for="slo-window" class="text-sm text-slate-300">Window</label>
      <select id="slo-window" bind:value={windowMinutes} class="rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm">
        <option value={15}>15m</option>
        <option value={60}>1h</option>
        <option value={360}>6h</option>
        <option value={1440}>24h</option>
      </select>
      <button class="admin-btn" on:click={load}>Refresh</button>
    </div>
  </div>

  {#if loading}
    <p class="text-sm text-slate-400">Loading SLO telemetry...</p>
  {:else if error}
    <p class="text-sm admin-state-bad">{error}</p>
  {:else if summary}
    <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
      <div class="admin-kpi">
        <p class="admin-kpi-label">Error Rate</p>
        <p class="admin-kpi-value">{formatPercent(summary.error_rate)}</p>
        <p class="text-xs text-slate-400 mt-1">{summary.failed_events} / {summary.total_events} events</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">p95 Latency</p>
        <p class="admin-kpi-value">{summary.latency_ms.p95.toFixed(1)} ms</p>
        <p class="text-xs text-slate-400 mt-1">p50 {summary.latency_ms.p50.toFixed(1)} ms</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">Action Success Rate</p>
        <p class="admin-kpi-value">{formatPercent(summary.action_success_rate)}</p>
        <p class="text-xs text-slate-400 mt-1">{summary.success_events} successful actions</p>
      </div>
    </div>

    <div class="mt-4 grid gap-3 md:grid-cols-2">
      <div class="rounded-lg border border-slate-700 bg-slate-900/60 p-3">
        <h3 class="text-sm font-semibold text-slate-200 mb-2">Failure Class Breakdown</h3>
        {#if summary.top_failure_classes.length === 0}
          <p class="text-xs text-slate-400">No failures recorded in the selected window.</p>
        {:else}
          <ul class="space-y-1">
            {#each summary.top_failure_classes as item}
              <li class="flex items-center justify-between text-xs">
                <span class="text-slate-300">{item.failure_class}</span>
                <span class="text-slate-100 font-semibold">{item.count}</span>
              </li>
            {/each}
          </ul>
        {/if}
      </div>

      <div class="rounded-lg border border-slate-700 bg-slate-900/60 p-3">
        <h3 class="text-sm font-semibold text-slate-200 mb-2">Telemetry Context</h3>
        <p class="text-xs text-slate-400">Window: last {summary.window_minutes} minutes</p>
        <p class="text-xs text-slate-400">Generated: {new Date(summary.generated_at).toLocaleString()}</p>
      </div>
    </div>
  {/if}
</section>
