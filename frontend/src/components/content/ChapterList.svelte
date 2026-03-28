<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { api } from "../../lib/api";

  export let endpointBase: string;
  export let initialItems: any[] = [];
  export let total = 0;
  export let initialOffset = 0;
  export let pageSize = 30;
  export let sequenceUnitLabel = "Verse";

  let items: any[] = [...initialItems];
  let offset = initialOffset;
  let loading = false;
  let loadError: string | null = null;
  let observer: IntersectionObserver | null = null;
  let sentinelEl: HTMLDivElement | null = null;

  $: hasMore = items.length < total;

  function normalizeAndAppend(newItems: any[]) {
    if (!newItems.length) return;

    const byId = new Map<number, any>();
    for (const item of items) {
      if (typeof item?.id === "number") byId.set(item.id, item);
    }
    for (const item of newItems) {
      if (typeof item?.id === "number") {
        byId.set(item.id, item);
      } else {
        items = [...items, item];
      }
    }

    const merged = Array.from(byId.values());
    merged.sort((a, b) => {
      const aNum = typeof a?.number_in_chapter === "number" ? a.number_in_chapter : Number.MAX_SAFE_INTEGER;
      const bNum = typeof b?.number_in_chapter === "number" ? b.number_in_chapter : Number.MAX_SAFE_INTEGER;
      if (aNum !== bNum) return aNum - bNum;
      return (a?.id ?? 0) - (b?.id ?? 0);
    });

    items = merged;
  }

  async function loadMore() {
    if (loading || !hasMore) return;

    loading = true;
    loadError = null;
    try {
      const res = await api(`${endpointBase}?offset=${offset}&limit=${pageSize}`);
      const newItems = Array.isArray(res?.items) ? res.items : [];
      total = Number(res?.total ?? total ?? items.length + newItems.length);
      normalizeAndAppend(newItems);
      offset += newItems.length;

      if (newItems.length === 0) {
        offset = items.length;
      }
    } catch (e: any) {
      loadError = e?.message || "Could not load more verses.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (typeof window === "undefined") return;
    if (!sentinelEl) return;

    observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          loadMore();
        }
      },
      {
        root: null,
        rootMargin: "280px 0px",
        threshold: 0.01,
      }
    );

    observer.observe(sentinelEl);
  });

  onDestroy(() => {
    observer?.disconnect();
    observer = null;
  });
</script>

<ul class="space-y-3" aria-live="polite" aria-busy={loading}>
  {#each items as i, idx}
    {@const itemId = i?.id}
    {@const verseNumber = typeof i?.number_in_chapter === "number" ? i.number_in_chapter : idx + 1}
    {@const itemLabel = i?.main_text || i?.hierarchy_path || `Verse ${verseNumber}`}
    <li class="doha-card rounded-lg border border-slate-700 bg-slate-950/45 px-4 py-3">
      <div class="sequence-badge">
        {sequenceUnitLabel} {idx + 1} of {total || items.length}
      </div>
      {#if itemId}
        <a href={`/doha/${encodeURIComponent(itemId)}`} class="text-slate-100 hover:text-cyan-300">
          {String(itemLabel).slice(0, 180)}
        </a>
      {:else}
        <span class="text-slate-300">{String(itemLabel).slice(0, 180)}</span>
      {/if}
    </li>
  {/each}
</ul>

{#if loading}
  <div class="mt-4 flex items-center justify-center gap-2 text-sm text-slate-400">
    <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-cyan-400"></span>
    <span>Loading more {sequenceUnitLabel.toLowerCase()}s...</span>
  </div>
{/if}

{#if loadError}
  <div class="mt-4 rounded-md border border-amber-400/35 bg-amber-500/10 px-3 py-2 text-sm text-amber-100">
    {loadError}
  </div>
{/if}

{#if hasMore}
  <div bind:this={sentinelEl} class="h-1 w-full" aria-hidden="true"></div>
  <div class="mt-4 flex justify-center">
    <button
      type="button"
      class="rounded-md border border-cyan-500/60 bg-cyan-900/20 px-4 py-2 text-sm text-cyan-200 hover:bg-cyan-800/30 disabled:opacity-50"
      on:click={loadMore}
      disabled={loading}
      aria-label={`Load more ${sequenceUnitLabel.toLowerCase()}s`}
    >
      {loading ? "Loading..." : `Load More ${sequenceUnitLabel}s`}
    </button>
  </div>
{:else if items.length > 0}
  <p class="mt-4 text-center text-xs text-slate-500">You have reached the end of this chapter.</p>
{/if}
