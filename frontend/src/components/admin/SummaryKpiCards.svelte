<script lang="ts">
  import { onMount } from "svelte";

  import { fetchAdminSummary, fetchSummary } from "../../lib/analytics";

  export let title: string = "Global Summary";
  export let useAdminSummary: boolean = false;

  let loading = true;
  let error: string | null = null;
  let summary: { today_approved: number; pending_review: number; total_approved: number } | null = null;

  async function load() {
    loading = true;
    error = null;
    try {
      summary = useAdminSummary ? await fetchAdminSummary() : await fetchSummary();
    } catch (e: any) {
      error = e?.message || "Failed to load summary";
      summary = null;
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

<section class="rounded-xl border border-slate-700 bg-slate-900/60 p-4 md:p-5">
  <div class="mb-4 flex items-center justify-between gap-3">
    <h2 class="text-lg font-semibold text-slate-100">{title}</h2>
    <button class="admin-btn" on:click={load}>Refresh</button>
  </div>

  {#if loading}
    <p class="text-sm text-slate-400">Loading KPI summary...</p>
  {:else if error}
    <p class="text-sm admin-state-bad">{error}</p>
  {:else if summary}
    <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
      <div class="admin-kpi">
        <p class="admin-kpi-label">Approved Today</p>
        <p class="admin-kpi-value">{summary.today_approved.toLocaleString()}</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">Pending Review</p>
        <p class="admin-kpi-value">{summary.pending_review.toLocaleString()}</p>
      </div>

      <div class="admin-kpi">
        <p class="admin-kpi-label">Total Approved</p>
        <p class="admin-kpi-value">{summary.total_approved.toLocaleString()}</p>
      </div>
    </div>
  {/if}
</section>
