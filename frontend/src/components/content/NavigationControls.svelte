<script lang="ts">
  export let previousId: number | undefined = undefined;
  export let nextId: number | undefined = undefined;
  export let previousText: string | undefined = undefined;
  export let nextText: string | undefined = undefined;

  let isLoading = false;

  const handleNavigation = async (targetId: number) => {
    isLoading = true;
    // Navigation will be handled by browser; loading state provides visual feedback
    setTimeout(() => {
      window.location.href = `/doha/${targetId}`;
    }, 100);
  };
</script>

<div class="mb-8 flex items-center justify-between gap-4">
  <!-- Previous Button -->
  {#if previousId}
    <button
      on:click={() => handleNavigation(previousId)}
      disabled={isLoading}
      class="flex-1 px-4 py-3 bg-gradient-to-r from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 disabled:opacity-50 disabled:cursor-not-allowed text-slate-100 font-medium rounded-lg transition-all flex items-center gap-2 group"
      title={previousText ? `Previous: ${previousText.substring(0, 60)}...` : "Previous verse"}
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
  {#if nextId}
    <button
      on:click={() => handleNavigation(nextId)}
      disabled={isLoading}
      class="flex-1 px-4 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-900 font-medium rounded-lg transition-all flex items-center justify-end gap-2 group"
      title={nextText ? `Next: ${nextText.substring(0, 60)}...` : "Next verse"}
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
