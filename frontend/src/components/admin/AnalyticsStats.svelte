<!-- src/components/admin/AnalyticsStats.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  export let apiBase: string = "";

  let loading = true;
  let stats: any = null;
  let error: string | null = null;

  async function load() {
    loading = true;
    error = null;
    try {
      // Fetch engagement KPI aggregates
      const kpis = await api("/analytics/top?limit=100");
      
      // Handle both array response and object with results
      const items = Array.isArray(kpis) ? kpis : (kpis?.results || []);
      
      // Calculate totals
      const totalViews = items.reduce((sum: number, item: any) => sum + (item.views || 0), 0);
      const totalLikes = items.reduce((sum: number, item: any) => sum + (item.likes || 0), 0);
      const totalSearchHits = items.reduce((sum: number, item: any) => sum + (item.search_hits || 0), 0);
      
      // Find top performer
      const topItem = items.length > 0 ? items[0] : null;
      
      stats = {
        totalViews,
        totalLikes,
        totalSearchHits,
        totalContent: items.length,
        topPerformer: topItem ? {
          type: topItem.content_type,
          title: topItem.title_or_text || "Unknown",
          score: topItem.score
        } : null
      };
      
      loading = false;
    } catch (e: any) {
      console.error("[AnalyticsStats] load error", e);
      error = e?.message || "Failed to load statistics";
      loading = false;
    }
  }

  onMount(() => {
    load();
  });
</script>

<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  {#if loading}
    <div class="col-span-full text-center text-slate-500 text-sm py-4">
      Loading platform statistics...
    </div>
  {:else if error}
    <div class="col-span-full bg-red-900/20 border border-red-700/50 rounded-lg p-6 text-center">
      <div class="text-red-400 text-sm mb-3">{error}</div>
      <button
        class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded text-sm transition-colors"
        on:click={load}
      >
        Retry
      </button>
    </div>
  {:else if stats}
    <!-- Total Views -->
    <div class="bg-gradient-to-br from-cyan-900/40 to-cyan-800/20 border border-cyan-700/50 rounded-lg p-4">
      <div class="text-cyan-400 text-xs font-medium uppercase tracking-wide mb-1">Total Views</div>
      <div class="text-3xl font-bold text-white">{stats.totalViews.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">All content types</div>
    </div>

    <!-- Total Likes -->
    <div class="bg-gradient-to-br from-pink-900/40 to-pink-800/20 border border-pink-700/50 rounded-lg p-4">
      <div class="text-pink-400 text-xs font-medium uppercase tracking-wide mb-1">Total Likes</div>
      <div class="text-3xl font-bold text-white">{stats.totalLikes.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Engagement count</div>
    </div>

    <!-- Total Search Hits -->
    <div class="bg-gradient-to-br from-indigo-900/40 to-indigo-800/20 border border-indigo-700/50 rounded-lg p-4">
      <div class="text-indigo-400 text-xs font-medium uppercase tracking-wide mb-1">Search Hits</div>
      <div class="text-3xl font-bold text-white">{stats.totalSearchHits.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Discovery metrics</div>
    </div>

    <!-- Active Content -->
    <div class="bg-gradient-to-br from-purple-900/40 to-purple-800/20 border border-purple-700/50 rounded-lg p-4">
      <div class="text-purple-400 text-xs font-medium uppercase tracking-wide mb-1">Active Content</div>
      <div class="text-3xl font-bold text-white">{stats.totalContent.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Total items</div>
    </div>

    <!-- Top Performer (if available, spans 2 columns) -->
    {#if stats.topPerformer}
      <div class="col-span-2 bg-gradient-to-br from-amber-900/40 to-amber-800/20 border border-amber-700/50 rounded-lg p-4">
        <div class="text-amber-400 text-xs font-medium uppercase tracking-wide mb-1">🏆 Top Performer</div>
        <div class="text-lg font-semibold text-white truncate">{stats.topPerformer.title}</div>
        <div class="flex items-center gap-3 mt-2">
          <span class="text-xs px-2 py-0.5 bg-amber-700/30 text-amber-300 rounded capitalize">
            {stats.topPerformer.type}
          </span>
          <span class="text-xs text-slate-400">
            Score: <span class="text-amber-400 font-mono">{stats.topPerformer.score}</span>
          </span>
        </div>
      </div>
    {/if}
  {/if}
</div>
