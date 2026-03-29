<!-- src/components/admin/AnalyticsTop.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { fetchAdminContentPerformance } from "../../lib/analytics";
  import { downloadCSV } from "../../lib/csv";

  export let apiBase: string = "";
  void apiBase;

  let loading = false;
  let error: string | null = null;
  let data: any[] = [];
  let contentType = ""; // empty = all
  let limit = 20;
  let page = 0;
  let startDate = "";
  let endDate = "";

  async function load() {
    loading = true;
    error = null;
    try {
      const res = await fetchAdminContentPerformance({
        content_type: contentType || undefined,
        limit,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      // API returns array
      data = Array.isArray(res) ? res : res?.results ?? [];
      page = 0;
    } catch (e: any) {
      console.error("[AnalyticsTop] load error", e);
      error = e?.message || "Failed to load top content";
    } finally {
      loading = false;
    }
  }

  function prevPage() {
    if (page > 0) { page -= 1; window.scrollTo({ top: 0, behavior: "smooth" }); }
  }
  function nextPage() {
    page += 1;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  $: paged = data.slice(page * limit, (page + 1) * limit);

  onMount(() => {
    load();
  });
</script>

<div>
  <!-- Date Range and Filters -->
  <div class="flex flex-col sm:flex-row gap-3 mb-4 p-4 bg-slate-900 rounded-lg border border-slate-700">
    <div class="flex gap-2 flex-1">
      <input
        type="date"
        bind:value={startDate}
        class="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
        placeholder="Start date"
        aria-label="Start date"
      />
      <input
        type="date"
        bind:value={endDate}
        class="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
        placeholder="End date"
        aria-label="End date"
      />
    </div>
    <button
      class="admin-btn admin-btn-primary"
      on:click={load}
    >
      Apply Dates
    </button>
  </div>

  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
    <div class="flex items-center gap-2">
      <label for="content-type" class="text-sm text-slate-400 font-medium">Content type</label>
      <select id="content-type" bind:value={contentType} on:change={() => load()} class="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-slate-500">
        <option value="">All Types</option>
        <option value="doha">Doha</option>
        <option value="dictionary">Dictionary</option>
        <option value="idiom">Idiom</option>
        <option value="article">Article</option>
      </select>
    </div>

    <div class="flex items-center gap-2">
      <label for="limit-select" class="text-sm text-slate-400 font-medium">Show</label>
      <select id="limit-select" bind:value={limit} on:change={() => load()} class="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-slate-500">
        <option value="10">10</option>
        <option value="20">20</option>
        <option value="50">50</option>
        <option value="100">100</option>
      </select>

      <button on:click={load} class="admin-btn admin-btn-primary">
        🔄 Refresh
      </button>
      <button
        on:click={() => downloadCSV("analytics_top.csv", data)}
        class="admin-btn"
        disabled={data.length === 0}
      >
        📥 Export CSV
      </button>
    </div>
  </div>

  {#if loading}
    <div class="mt-8 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-slate-400"></div>
      <p class="mt-4 text-sm text-slate-300">Loading top content...</p>
    </div>
  {:else if error}
    <div class="mt-4 p-4 bg-rose-900/15 border border-rose-500/30 rounded-lg">
      <p class="text-sm text-rose-200">⚠️ {error}</p>
    </div>
  {:else if data.length === 0}
    <div class="mt-4 p-8 text-center border-2 border-dashed border-slate-700 rounded-lg">
      <p class="text-slate-400">No content data available for the selected filters.</p>
    </div>
  {:else}
    <div class="overflow-x-auto rounded-lg border border-slate-700">
      <table class="w-full text-sm">
        <thead class="bg-slate-900">
          <tr class="text-left border-b border-slate-600">
            <th class="px-4 py-3 text-slate-400 font-semibold">#</th>
            <th class="px-4 py-3 text-slate-400 font-semibold">Type</th>
            <th class="px-4 py-3 text-slate-400 font-semibold">Title / Text</th>
            <th class="px-4 py-3 text-slate-400 font-semibold text-right">Score</th>
            <th class="px-4 py-3 text-slate-400 font-semibold text-right">Views</th>
            <th class="px-4 py-3 text-slate-400 font-semibold text-right">Likes</th>
            <th class="px-4 py-3 text-slate-400 font-semibold text-right">Searches</th>
          </tr>
        </thead>
        <tbody>
          {#each paged as item, i}
            <tr class="border-t border-slate-700/50 hover:bg-slate-700/30 transition-colors">
              <td class="px-4 py-3 text-slate-500 font-mono">{page * limit + i + 1}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 bg-slate-900/70 text-slate-300 rounded text-xs font-semibold uppercase tracking-wide border border-slate-700">
                  {item.content_type}
                </span>
              </td>
              <td class="px-4 py-3 max-w-md">
                <div class="truncate text-slate-200 font-medium">
                  {item.title_or_text ?? item.main_text ?? item.text_devanagari ?? "Untitled"}
                </div>
              </td>
              <td class="px-4 py-3 text-right font-mono text-slate-200 font-semibold">
                {Number(item.score ?? item.weight_score ?? 0).toFixed(2)}
              </td>
              <td class="px-4 py-3 text-right text-slate-300">{item.views?.toLocaleString() ?? "—"}</td>
              <td class="px-4 py-3 text-right text-slate-300 font-medium">{(item.likes ?? item.likes_count)?.toLocaleString() ?? "—"}</td>
              <td class="px-4 py-3 text-right text-slate-300 font-medium">{item.search_hits?.toLocaleString() ?? "—"}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between mt-4 px-2">
      <div class="text-sm text-slate-400">
        Showing <span class="font-semibold text-slate-200">{page * limit + 1}</span> - <span class="font-semibold text-slate-200">{Math.min((page + 1) * limit, data.length)}</span> of <span class="font-semibold text-slate-200">{data.length}</span> items
      </div>
      <div class="flex gap-2">
        <button 
          class="admin-btn disabled:opacity-50 disabled:cursor-not-allowed"
          on:click={prevPage} 
          disabled={page === 0}
        >
          ← Previous
        </button>
        <button 
          class="admin-btn disabled:opacity-50 disabled:cursor-not-allowed"
          on:click={nextPage} 
          disabled={(page + 1) * limit >= data.length}
        >
          Next →
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  /* small, self-contained styles */
  table td, table th { padding: 8px 6px; }
</style>
