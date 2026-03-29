<!-- src/components/admin/AnalyticsDemand.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { fetchDemand } from "../../lib/analytics";
  import { downloadCSV } from "../../lib/csv";

  export let apiBase: string = "";
  void apiBase;

  let loading = false;
  let error: string | null = null;
  let demand: Record<string, { count: number; percent: number }> | null = null;

  async function load() {
    loading = true; error = null;
    try {
      const res = await fetchDemand();
      demand = res;
    } catch (e: any) {
      error = e?.message || "Failed to load demand distribution";
      console.error("[AnalyticsDemand] err", e);
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

<div>
  {#if loading}
    <div class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-slate-400"></div>
      <p class="mt-4 text-sm text-slate-300">Loading demand distribution...</p>
    </div>
  {:else if error}
    <div class="p-4 bg-rose-900/15 border border-rose-500/30 rounded-lg">
      <p class="text-sm text-rose-200">⚠️ {error}</p>
    </div>
  {:else if demand}
    <button
      class="mb-4 w-full admin-btn"
      on:click={() => {
        if (!demand) return;
        downloadCSV(
          "analytics_demand.csv",
          Object.entries(demand).map(([k, v]) => ({
            content_type: k,
            count: v.count,
            percent: v.percent,
          }))
        );
      }}
    >
      📥 Export CSV
    </button>

    <!-- Calculate total for summary -->
    {@const totalSearches = Object.values(demand).reduce((sum, v) => sum + v.count, 0)}
    
    <!-- Summary Card -->
    <div class="mb-4 p-4 admin-panel">
      <div class="text-center">
        <div class="text-3xl font-bold text-slate-200">{totalSearches.toLocaleString()}</div>
        <div class="text-xs text-slate-500 mt-1">Total searches tracked</div>
      </div>
    </div>

    <div class="space-y-4">
      {#each Object.entries(demand).sort((a, b) => b[1].percent - a[1].percent) as [k, v]}
        {@const barColor = k === 'doha' ? '#7aa6d8' : k === 'dictionary' ? '#8eb7c3' : k === 'idiom' ? '#9aa6c7' : '#b59db8'}
        <div class="space-y-2 p-3 bg-slate-900 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" style="background-color: {barColor}"></div>
              <div class="font-medium text-slate-200 capitalize">{k}</div>
            </div>
            <div class="text-right">
              <div class="text-lg font-bold" style="color: {barColor}">{Number(v.percent).toFixed(1)}%</div>
            </div>
          </div>
          <div class="text-xs text-slate-500">{v.count.toLocaleString()} searches</div>
          <div class="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
            <div 
              class="h-3 rounded-full transition-all duration-500 ease-out shadow-lg"
              style="width: {v.percent}%; background: linear-gradient(90deg, {barColor}, {barColor}dd)"
            ></div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="p-8 text-center border-2 border-dashed border-slate-700 rounded-lg">
      <p class="text-slate-400">No demand data yet.</p>
    </div>
  {/if}
</div>
