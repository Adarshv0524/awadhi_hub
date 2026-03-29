<script lang="ts">
  import { onMount } from "svelte";

  import { API_BASE } from "../../lib/api";

  type ArticleSummary = {
    id: number;
    title: string;
    excerpt?: string | null;
    tags?: string[] | null;
    created_at?: string | null;
  };

  type ArticleStats = {
    total_articles: number;
    by_tag: Record<string, number>;
    recent_count: number;
  };

  export let activeTag: string | null = null;

  let loading = true;
  let error = "";
  let tags: string[] = [];
  let recent: ArticleSummary[] = [];
  let stats: ArticleStats | null = null;

  function hrefForTag(tag: string): string {
    return `/articles/tag/${encodeURIComponent(tag)}`;
  }

  function formatDate(value?: string | null): string {
    if (!value) return "";
    try {
      return new Date(value).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return value;
    }
  }

  async function loadDiscoveryData() {
    loading = true;
    error = "";
    try {
      const [tagRes, recentRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/articles/tags/list`),
        fetch(`${API_BASE}/articles/recent/list?limit=8`),
        fetch(`${API_BASE}/articles/stats`),
      ]);

      if (!tagRes.ok || !recentRes.ok || !statsRes.ok) {
        throw new Error("Failed to load article discovery data");
      }

      const tagsBody = await tagRes.json();
      const recentBody = await recentRes.json();
      const statsBody = await statsRes.json();

      tags = Array.isArray(tagsBody?.tags) ? tagsBody.tags : [];
      recent = Array.isArray(recentBody) ? recentBody : [];
      stats = statsBody || null;
    } catch (e: any) {
      error = e?.message || "Could not load article discovery data";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    void loadDiscoveryData();
  });
</script>

<aside class="rounded-2xl border border-slate-700 bg-slate-900/60 p-4 md:p-5">
  <div class="mb-4 flex items-center justify-between gap-2">
    <h2 class="text-lg font-semibold text-slate-100">Article Hub</h2>
    <button class="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300 hover:bg-slate-800" on:click={loadDiscoveryData}>
      Refresh
    </button>
  </div>

  {#if loading}
    <p class="text-sm text-slate-400">Loading discovery widgets...</p>
  {:else if error}
    <p class="text-sm text-red-400">{error}</p>
  {:else}
    {#if stats}
      <div class="mb-5 grid grid-cols-2 gap-2">
        <div class="rounded-lg border border-cyan-700/40 bg-cyan-950/20 p-3">
          <p class="text-[11px] uppercase tracking-wide text-cyan-300">Total Articles</p>
          <p class="mt-1 text-xl font-bold text-cyan-200">{stats.total_articles}</p>
        </div>
        <div class="rounded-lg border border-emerald-700/40 bg-emerald-950/20 p-3">
          <p class="text-[11px] uppercase tracking-wide text-emerald-300">Recent (30d)</p>
          <p class="mt-1 text-xl font-bold text-emerald-200">{stats.recent_count}</p>
        </div>
      </div>
    {/if}

    <section class="mb-5">
      <h3 class="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-300">Browse by Tag</h3>
      {#if tags.length === 0}
        <p class="text-xs text-slate-500">No tags found.</p>
      {:else}
        <div class="flex flex-wrap gap-2">
          {#each tags as tag}
            <a
              href={hrefForTag(tag)}
              class={`rounded-full border px-2.5 py-1 text-xs transition ${activeTag === tag ? "border-purple-400 bg-purple-500/20 text-purple-200" : "border-slate-600 text-slate-300 hover:border-purple-400/60 hover:text-purple-200"}`}
            >
              #{tag}
              {#if stats?.by_tag?.[tag]}
                <span class="ml-1 text-[10px] text-slate-400">({stats.by_tag[tag]})</span>
              {/if}
            </a>
          {/each}
        </div>
      {/if}
    </section>

    <section>
      <h3 class="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-300">Recent Articles</h3>
      {#if recent.length === 0}
        <p class="text-xs text-slate-500">No recent articles yet.</p>
      {:else}
        <ul class="space-y-2">
          {#each recent as article}
            <li class="rounded-lg border border-slate-700 bg-slate-950/40 p-3">
              <a href={`/articles/${article.id}`} class="line-clamp-2 text-sm font-medium text-slate-100 hover:text-cyan-300">
                {article.title}
              </a>
              {#if article.created_at}
                <p class="mt-1 text-xs text-slate-500">{formatDate(article.created_at)}</p>
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  {/if}
</aside>
