<!-- src/components/admin/AnalyticsGrowth.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { fetchGrowth } from "../../lib/analytics";
  import { downloadCSV } from "../../lib/csv";
  import Sparkline from "./Sparkline.svelte";

  export let apiBase: string = "";

  let loading = false;
  let error: string | null = null;
  let growthData: { dates: string[]; series: Record<string, number[]> } | null = null;
  let viewMode: "chart" | "table" = "chart";
  let startDate = "";
  let endDate = "";

  async function load() {
    loading = true; error = null;
    try {
      const res = await fetchGrowth({
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      growthData = res;
    } catch (e: any) {
      console.error("[AnalyticsGrowth] load error", e);
      error = e?.message || "Failed to load growth trends";
    } finally {
      loading = false;
    }
  }

  const metricColors: Record<string, string> = {
    doha: "#22d3ee",
    dictionary: "#60a5fa",
    idiom: "#a78bfa",
    article: "#f472b6",
    users: "#34d399",
  };

  onMount(load);
</script>

<div>
  {#if loading}
    <div class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
      <p class="mt-4 text-sm text-blue-400">Loading growth trends...</p>
    </div>
  {:else if error}
    <div class="p-4 bg-red-900/20 border border-red-700 rounded-lg">
      <p class="text-sm text-red-400">⚠️ {error}</p>
    </div>
  {:else if growthData}
    <!-- Controls -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6 p-4 bg-slate-900 rounded-lg border border-slate-700">
      <div class="flex gap-2 flex-1">
        <input
          type="date"
          bind:value={startDate}
          class="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Start date"
          aria-label="Start date"
        />
        <input
          type="date"
          bind:value={endDate}
          class="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="End date"
          aria-label="End date"
        />
      </div>
      <button
        class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors font-medium shadow-lg"
        on:click={load}
      >
        Apply Dates
      </button>
    </div>

    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
      <div class="flex gap-2">
        <button
          class="px-4 py-2 border border-slate-600 rounded text-sm transition-colors font-medium"
          class:bg-blue-600={viewMode === "chart"}
          class:border-blue-500={viewMode === "chart"}
          class:text-white={viewMode === "chart"}
          class:text-slate-200={viewMode !== "chart"}
          class:hover:bg-slate-700={viewMode !== "chart"}
          on:click={() => viewMode = "chart"}
        >
          📊 Chart View
        </button>
        <button
          class="px-4 py-2 border border-slate-600 rounded text-sm transition-colors font-medium"
          class:bg-blue-600={viewMode === "table"}
          class:border-blue-500={viewMode === "table"}
          class:text-white={viewMode === "table"}
          class:text-slate-200={viewMode !== "table"}
          class:hover:bg-slate-700={viewMode !== "table"}
          on:click={() => viewMode = "table"}
        >
          📋 Table View
        </button>
      </div>
      
      <button
        class="px-4 py-2 border border-slate-600 hover:border-blue-500 hover:bg-slate-700 text-slate-200 rounded text-sm transition-colors font-medium"
        on:click={() => {
          if (!growthData) return;
          const rows = growthData.dates.map((d, i) => {
            const row: any = { date: d };
            for (const k in growthData!.series) row[k] = growthData!.series[k][i];
            return row;
          });
          downloadCSV("analytics_growth.csv", rows);
        }}
      >
        📥 Export CSV
      </button>
    </div>

    {#if viewMode === "chart"}
      <!-- Chart View with Sparklines -->
      <div class="space-y-6">
        {#each Object.keys(growthData.series) as metric}
          {@const values = growthData.series[metric]}
          {@const total = values.reduce((sum, v) => sum + v, 0)}
          {@const avg = (total / values.length).toFixed(1)}
          {@const max = Math.max(...values)}
          {@const color = metricColors[metric] || "#64748b"}
          
          <div class="bg-slate-900 rounded-lg p-5 border border-slate-700 hover:border-slate-600 transition-colors shadow-lg">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="w-4 h-4 rounded-full shadow-lg" style="background-color: {color}"></div>
                <div>
                  <h3 class="font-semibold text-slate-200 capitalize text-lg">{metric}</h3>
                  <p class="text-xs text-slate-500 mt-1">Daily submissions over time</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold" style="color: {color}">{total.toLocaleString()}</div>
                <div class="text-xs text-slate-500 mt-1">Total • Avg: {avg}/day</div>
                <div class="text-xs text-slate-600">Peak: {max}</div>
              </div>
            </div>
            
            <div class="flex justify-center bg-slate-950 rounded-lg p-4 border border-slate-800">
              <Sparkline values={values} width={700} height={100} color={color} fillOpacity={0.2} />
            </div>
            
            <div class="mt-3 flex justify-between text-xs text-slate-500">
              <span>📅 {new Date(growthData.dates[0]).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
              <span class="text-slate-600">{growthData.dates.length} days</span>
              <span>📅 {new Date(growthData.dates[growthData.dates.length - 1]).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <!-- Table View -->
      <div class="overflow-x-auto rounded-lg border border-slate-700">
        <table class="w-full text-sm">
          <thead class="bg-slate-900 sticky top-0">
            <tr class="border-b border-slate-600">
              <th class="text-left px-4 py-3 text-slate-400 font-semibold sticky left-0 bg-slate-900 z-10">Metric</th>
              {#each growthData.dates as d}
                <th class="text-center px-3 py-3 text-slate-400 font-semibold min-w-24">
                  {new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </th>
              {/each}
              <th class="text-right px-4 py-3 text-slate-400 font-semibold sticky right-0 bg-slate-900 z-10">Total</th>
            </tr>
          </thead>
          <tbody>
            {#each Object.keys(growthData.series) as metric}
              {@const values = growthData.series[metric]}
              {@const total = values.reduce((sum, v) => sum + v, 0)}
              {@const color = metricColors[metric] || "#64748b"}
              <tr class="border-t border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                <td class="px-4 py-3 font-medium capitalize sticky left-0 bg-slate-800 z-10" style="color: {color}">
                  <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full" style="background-color: {color}"></div>
                    {metric}
                  </div>
                </td>
                {#each values as v}
                  <td class="px-3 py-3 text-center text-slate-300 font-mono text-xs">
                    {v > 0 ? v : '·'}
                  </td>
                {/each}
                <td class="px-4 py-3 text-right font-bold sticky right-0 bg-slate-800 z-10" style="color: {color}">
                  {total.toLocaleString()}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  {:else}
    <div class="p-8 text-center border-2 border-dashed border-slate-700 rounded-lg">
      <p class="text-slate-400">No growth data available.</p>
    </div>
  {/if}
</div>
