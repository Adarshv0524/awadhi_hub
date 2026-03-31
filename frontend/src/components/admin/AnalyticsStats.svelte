<!-- src/components/admin/AnalyticsStats.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { fetchAdminEngagementSummary } from "../../lib/analytics";

  export let apiBase: string = "";
  void apiBase;

  let loading = true;
  let stats: any = null;
  let error: string | null = null;
  let lastUpdated = "";

  async function load() {
    loading = true;
    error = null;
    try {
      const summary = await fetchAdminEngagementSummary();
      stats = {
        totalViews: Number(summary?.total_views || 0),
        totalLikes: Number(summary?.total_likes || 0),
        totalBookmarks: Number(summary?.total_bookmarks || 0),
        totalShares: Number(summary?.total_shares || 0),
        totalSearchHits: Number(summary?.total_search_hits || 0),
        totalContent: Number(summary?.active_content || 0),
        topPerformer: summary?.top_performer
          ? {
              type: summary.top_performer.content_type,
              title: summary.top_performer.title_or_text || "Unknown",
              score: summary.top_performer.score,
            }
          : null,
      };
      lastUpdated = new Date().toLocaleTimeString();
      
      loading = false;
    } catch (e: any) {
      console.error("[AnalyticsStats] load error", e);
      error = e?.message || "Failed to load statistics";
      loading = false;
    }
  }

  onMount(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  });
</script>

<div class="mb-3 flex items-center justify-between gap-3">
  <p class="text-xs text-slate-400">Last updated: {lastUpdated || "-"}</p>
  <button class="admin-btn" on:click={load}>Refresh</button>
</div>

<div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
  {#if loading}
    <div class="col-span-full text-center text-slate-500 text-sm py-4">
      Loading platform statistics...
    </div>
  {:else if error}
    <div class="col-span-full bg-rose-900/15 border border-rose-500/30 rounded-lg p-6 text-center">
      <div class="text-rose-200 text-sm mb-3">{error}</div>
      <button
        class="admin-btn admin-btn-danger"
        on:click={load}
      >
        Retry
      </button>
    </div>
  {:else if stats}
    <!-- Total Views -->
    <div class="admin-kpi">
      <div class="admin-kpi-label">Total Views</div>
      <div class="admin-kpi-value">{stats.totalViews.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">All content types</div>
    </div>

    <!-- Total Likes -->
    <div class="admin-kpi">
      <div class="admin-kpi-label">Total Likes</div>
      <div class="admin-kpi-value">{stats.totalLikes.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Engagement count</div>
    </div>

    <!-- Total Search Hits -->
    <div class="admin-kpi">
      <div class="admin-kpi-label">Search Hits</div>
      <div class="admin-kpi-value">{stats.totalSearchHits.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Discovery metrics</div>
    </div>

    <!-- Total Bookmarks -->
    <div class="admin-kpi">
      <div class="admin-kpi-label">Bookmarks</div>
      <div class="admin-kpi-value">{stats.totalBookmarks.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Saved interactions</div>
    </div>

    <!-- Total Shares -->
    <div class="admin-kpi">
      <div class="admin-kpi-label">Shares</div>
      <div class="admin-kpi-value">{stats.totalShares.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Distribution events</div>
    </div>

    <!-- Active Content -->
    <div class="admin-kpi">
      <div class="admin-kpi-label">Active Content</div>
      <div class="admin-kpi-value">{stats.totalContent.toLocaleString()}</div>
      <div class="text-xs text-slate-400 mt-1">Total items</div>
    </div>

    <!-- Top Performer (if available, spans 2 columns) -->
    {#if stats.topPerformer}
      <div class="col-span-2 md:col-span-3 xl:col-span-6 admin-kpi">
        <div class="admin-kpi-label">Top Performer</div>
        <div class="text-lg font-semibold text-slate-100 truncate">{stats.topPerformer.title}</div>
        <div class="flex items-center gap-3 mt-2">
          <span class="text-xs px-2 py-0.5 bg-slate-800/80 text-slate-300 rounded capitalize border border-slate-700">
            {stats.topPerformer.type}
          </span>
          <span class="text-xs text-slate-400">
            Score: <span class="text-slate-200 font-mono">{stats.topPerformer.score}</span>
          </span>
        </div>
      </div>
    {/if}
  {/if}
</div>
