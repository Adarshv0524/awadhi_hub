<script lang="ts">
  export let previousId: number | undefined = undefined;
  export let nextId: number | undefined = undefined;
  export let previousHref: string | undefined = undefined;
  export let nextHref: string | undefined = undefined;
  export let previousText: string | undefined = undefined;
  export let nextText: string | undefined = undefined;
  export let previousContentType: string | undefined = undefined;
  export let nextContentType: string | undefined = undefined;
  export let previousKind: string | undefined = undefined;
  export let nextKind: string | undefined = undefined;

  let isLoading = false;

  function routeForContentType(contentType: string | undefined): string | undefined {
    if (!contentType) return undefined;
    if (contentType === "doha") return "/poetry";
    if (contentType === "dictionary") return "/dictionary";
    if (contentType === "idiom") return "/idioms";
    if (contentType === "article") return "/articles";
    return undefined;
  }

  function kindForContentType(contentType: string | undefined): string {
    if (contentType === "doha") return "Verse";
    if (contentType === "dictionary") return "Definition";
    if (contentType === "idiom") return "Idiom";
    if (contentType === "article") return "Article";
    return "Item";
  }

  function resolveTarget(
    targetId: number | undefined,
    targetHref: string | undefined,
    targetContentType: string | undefined,
  ): string | undefined {
    if (targetHref) return targetHref;
    if (typeof targetId !== "number") return undefined;
    const routeBase = routeForContentType(targetContentType);
    if (!routeBase) return undefined;
    return `${routeBase}/${targetId}`;
  }

  function normalizePreview(text: string | undefined): string | undefined {
    if (!text) return undefined;
    const compact = text.replace(/\s+/g, " ").trim();
    return compact.length > 160 ? `${compact.slice(0, 157)}...` : compact;
  }

  function handleNavigation(target: string): void {
    isLoading = true;
    setTimeout(() => {
      window.location.href = target;
    }, 100);
  }

  $: previousTarget = resolveTarget(previousId, previousHref, previousContentType);
  $: nextTarget = resolveTarget(nextId, nextHref, nextContentType);
  $: previousPreview = normalizePreview(previousText);
  $: nextPreview = normalizePreview(nextText);
  $: previousKindLabel = previousKind || kindForContentType(previousContentType);
  $: nextKindLabel = nextKind || kindForContentType(nextContentType);
</script>

<div class="sticky top-4 z-20 mb-8 rounded-xl border border-slate-700/80 bg-slate-900/75 p-3 backdrop-blur">
  <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
    {#if previousTarget}
      <button
        on:click={() => handleNavigation(previousTarget)}
        disabled={isLoading}
        class="min-w-0 w-full rounded-lg border border-slate-600 bg-gradient-to-r from-slate-700 to-slate-600 px-4 py-3 text-left text-slate-100 transition-all hover:from-slate-600 hover:to-slate-500 disabled:cursor-not-allowed disabled:opacity-50"
        title={previousPreview ? `Previous: ${previousPreview}` : `Previous ${previousKindLabel}`}
      >
        <div class="text-[11px] uppercase tracking-wide text-slate-300">Previous {previousKindLabel}</div>
        <div class="mt-1 flex items-center gap-2 text-sm font-medium">
          <span class="text-base">←</span>
          <span class="truncate">{previousPreview || "Go to previous item"}</span>
        </div>
      </button>
    {:else}
      <div class="w-full rounded-lg border border-slate-700/70 bg-slate-800/50 px-4 py-3 text-left text-slate-500 opacity-60">
        <div class="text-[11px] uppercase tracking-wide">Previous {previousKindLabel}</div>
        <div class="mt-1 flex items-center gap-2 text-sm font-medium">
          <span class="text-base">←</span>
          <span>No previous item</span>
        </div>
      </div>
    {/if}

    {#if nextTarget}
      <button
        on:click={() => handleNavigation(nextTarget)}
        disabled={isLoading}
        class="min-w-0 w-full rounded-lg border border-cyan-500/60 bg-gradient-to-r from-cyan-600 to-cyan-500 px-4 py-3 text-right text-slate-950 transition-all hover:from-cyan-500 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        title={nextPreview ? `Next: ${nextPreview}` : `Next ${nextKindLabel}`}
      >
        <div class="text-[11px] uppercase tracking-wide text-slate-900/80">Next {nextKindLabel}</div>
        <div class="mt-1 flex items-center justify-end gap-2 text-sm font-semibold">
          <span class="truncate">{nextPreview || "Go to next item"}</span>
          <span class="text-base">→</span>
        </div>
      </button>
    {:else}
      <div class="w-full rounded-lg border border-slate-700/70 bg-slate-800/50 px-4 py-3 text-right text-slate-500 opacity-60">
        <div class="text-[11px] uppercase tracking-wide">Next {nextKindLabel}</div>
        <div class="mt-1 flex items-center justify-end gap-2 text-sm font-medium">
          <span>No next item</span>
          <span class="text-base">→</span>
        </div>
      </div>
    {/if}
  </div>
</div>