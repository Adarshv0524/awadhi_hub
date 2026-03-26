<script lang="ts">
  export let previousId: number | undefined = undefined;
  export let nextId: number | undefined = undefined;
  export let previousHref: string | undefined = undefined;
  export let nextHref: string | undefined = undefined;
  export let previousText: string | undefined = undefined;
  export let nextText: string | undefined = undefined;

  let isLoading = false;

  const resolveTarget = (targetId: number | undefined, targetHref: string | undefined) => {
    if (targetHref) return targetHref;
    if (targetId) return `/doha/${targetId}`;
    return undefined;
  };

  const handleNavigation = async (target: string) => {
    isLoading = true;
    // Navigation will be handled by browser; loading state provides visual feedback
    setTimeout(() => {
      window.location.href = target;
    }, 100);
  };

  $: previousTarget = resolveTarget(previousId, previousHref);
  $: nextTarget = resolveTarget(nextId, nextHref);
</script>

<div class="mb-8 flex items-center justify-between gap-4">
  <!-- Previous Button -->
  {#if previousTarget}
    <button
      on:click={() => handleNavigation(previousTarget)}
      disabled={isLoading}
      class="flex-1 px-4 py-3 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 disabled:opacity-50 disabled:cursor-not-allowed text-slate-100 font-medium rounded-lg transition-all flex items-center gap-2 group"
      title={previousText ? `Previous: ${previousText.substring(0, 60)}...` : "Previous item"}
    >
      <span class="text-lg group-hover:-translate-x-1 transition-transform">←</span>
      <span>Previous</span>
    </button>
  {:else}
    <div class="flex-1 px-4 py-3 bg-slate-800/50 text-slate-500 font-medium rounded-lg opacity-50 cursor-not-allowed flex items-center gap-2">
      <span class="text-lg">←</span>
      <span>Previous</span>
    </div>
  {/if}

  <!-- Next Button -->
  {#if nextTarget}
    <button
      on:click={() => handleNavigation(nextTarget)}
      disabled={isLoading}
      class="flex-1 px-4 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-900 font-medium rounded-lg transition-all flex items-center justify-end gap-2 group"
      title={nextText ? `Next: ${nextText.substring(0, 60)}...` : "Next item"}
    >
      <span>Next</span>
      <span class="text-lg group-hover:translate-x-1 transition-transform">→</span>
    </button>
  {:else}
    <div class="flex-1 px-4 py-3 bg-slate-800/50 text-slate-500 font-medium rounded-lg opacity-50 cursor-not-allowed flex items-center justify-end gap-2">
      <span>Next</span>
      <span class="text-lg">→</span>
    </div>
  {/if}
</div>

<style>
  /* Navigation controls styling */
</style>
