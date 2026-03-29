<script lang="ts">
  import { onMount } from "svelte";

  import { api } from "../../../lib/api";
  import PoetryDispatcher from "./PoetryDispatcher.svelte";
  import PoetryNavigation from "./PoetryNavigation.svelte";

  type Hierarchy = {
    author: { id: number; slug: string; name: string };
    work: { id: number; slug: string; title: string };
    chapter: { id: number; slug: string; number: number; title: string };
  };

  type PoetryNode = {
    id: number;
    poetry_type: string;
    sequence_no: number;
    main_text: string;
    prosody_metadata?: Record<string, unknown> | null;
    text_devanagari?: string | null;
    text_romanized?: string | null;
    meaning?: string | null;
  };

  type NavSummary = { id: number; poetry_type: string; sequence_no: number } | null;

  export let chapterId: number;
  export let hierarchy: Hierarchy;
  export let items: PoetryNode[] = [];
  export let total = 0;
  export let initialLimit = 25;

  let loadedItems: PoetryNode[] = [...items];
  let loadingMore = false;

  let currentIndex = 0;
  let previous: NavSummary = null;
  let next: NavSummary = null;
  let navError: string | null = null;

  $: currentNode = loadedItems[currentIndex] ?? null;
  $: canGoPrevious = currentIndex > 0;
  $: canGoNext = currentIndex < loadedItems.length - 1;
  $: hasMore = loadedItems.length < (total || loadedItems.length);
  $: positionText = currentNode ? `${currentNode.sequence_no} / ${total || loadedItems.length}` : `0 / ${total || 0}`;

  async function loadMore() {
    if (loadingMore || !hasMore) return;
    loadingMore = true;
    try {
      const res = await api<{ items: PoetryNode[] }>(
        `/api/v1/poetry/chapters/${chapterId}/stream?offset=${loadedItems.length}&limit=${initialLimit}`
      );
      const nextItems = Array.isArray(res?.items) ? res.items : [];
      if (nextItems.length > 0) {
        const existing = new Set(loadedItems.map((n) => n.id));
        loadedItems = [...loadedItems, ...nextItems.filter((n) => !existing.has(n.id))];
      }
    } catch (error: any) {
      navError = error?.message || "Could not load more chapter items.";
    } finally {
      loadingMore = false;
    }
  }

  async function fetchNavForCurrent() {
    navError = null;
    if (!currentNode) {
      previous = null;
      next = null;
      return;
    }

    try {
      const res = await api<{
        hierarchy: Hierarchy;
        current: PoetryNode;
        previous: NavSummary;
        next: NavSummary;
      }>(`/api/v1/poetry/chapters/${chapterId}/nav?sequence_no=${currentNode.sequence_no}`);

      previous = res?.previous ?? null;
      next = res?.next ?? null;
      if (res?.hierarchy) hierarchy = res.hierarchy;
    } catch (error: any) {
      previous = null;
      next = null;
      navError = error?.message || "Could not load navigation details.";
    }
  }

  function goToPrevious() {
    if (!canGoPrevious) return;
    currentIndex -= 1;
    fetchNavForCurrent();
    focusCurrent();
  }

  function goToNext() {
    if (!canGoNext && hasMore) {
      loadMore().then(() => {
        if (currentIndex < loadedItems.length - 1) {
          currentIndex += 1;
          fetchNavForCurrent();
          focusCurrent();
        }
      });
      return;
    }
    if (!canGoNext) return;
    currentIndex += 1;
    fetchNavForCurrent();
    focusCurrent();
  }

  function focusCurrent() {
    requestAnimationFrame(() => {
      const el = document.querySelector<HTMLElement>(`[data-poetry-seq='${currentNode?.sequence_no}']`);
      el?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function onReaderKeydown(event: KeyboardEvent) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      goToPrevious();
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      goToNext();
    }
  }

  onMount(() => {
    fetchNavForCurrent();
  });
</script>

<svelte:window on:keydown={onReaderKeydown} />

<section class="space-y-5" aria-label="Chapter poetry reader">
  <div class="glass-panel p-4 md:p-5">
    <div class="flex flex-wrap items-end justify-between gap-2">
      <div>
        <p class="text-xs uppercase tracking-wide text-slate-400">Chapter Position</p>
        <p class="mt-1 text-sm text-slate-100">{positionText}</p>
      </div>
      <p class="text-xs text-slate-400">Keyboard: use left and right arrow keys</p>
    </div>
  </div>

    <div class="chapter-flow" role="list" aria-label="Poetry sequence">
      {#each loadedItems as node, index}
      <article
        data-poetry-seq={node.sequence_no}
        class={`chapter-entry ${index === currentIndex ? "is-current" : ""}`}
        aria-current={index === currentIndex ? "true" : undefined}
        role="listitem"
      >
        <div class="chapter-entry-meta">
          <span class="chapter-entry-type">{node.poetry_type}</span>
          <span class="chapter-entry-seq">#{node.sequence_no}</span>
        </div>
        <a class="chapter-entry-link" href={`/poetry/${node.id}`} aria-label={`Open verse ${node.sequence_no} details`}>
          <PoetryDispatcher poetryNode={node} chapterId={chapterId} mode="chapter" />
        </a>
      </article>
    {/each}
  </div>

    {#if hasMore}
      <div class="flex justify-center pt-2">
        <button
          type="button"
          class="ui-button"
          data-variant="ghost"
          on:click={loadMore}
          disabled={loadingMore}
          aria-label="Load more chapter lines"
        >
          {loadingMore ? "Loading..." : `Load More (${loadedItems.length} of ${total})`}
        </button>
      </div>
    {/if}

  <PoetryNavigation
    {previous}
    {next}
    {canGoPrevious}
    {canGoNext}
    onPrevious={goToPrevious}
    onNext={goToNext}
  />

  {#if navError}
    <p class="text-sm text-amber-200">{navError}</p>
  {/if}
</section>
