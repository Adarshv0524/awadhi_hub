<!-- src/components/content/TrustSignals.svelte -->
<script lang="ts">
  export let isCanonical: boolean = false;
  export let confidenceLevel: number | null = null;
  export let sourceReference: any = null;
  export let verifiedBy: string | null = null;
  export let verifiedAt: string | null = null;

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  }

  function getConfidenceLabel(level: number): { text: string; color: string } {
    if (level >= 90) return { text: "Very High", color: "text-green-400 bg-green-900/30 border-green-700" };
    if (level >= 70) return { text: "High", color: "text-blue-400 bg-blue-900/30 border-blue-700" };
    if (level >= 50) return { text: "Medium", color: "text-yellow-400 bg-yellow-900/30 border-yellow-700" };
    return { text: "Low", color: "text-orange-400 bg-orange-900/30 border-orange-700" };
  }

  $: hasSignals = isCanonical || confidenceLevel !== null || sourceReference || verifiedBy;
</script>

{#if hasSignals}
  <div class="flex flex-wrap gap-2 items-center">
    {#if isCanonical}
      <div 
        class="inline-flex items-center gap-2 px-3 py-1.5 bg-cyan-900/30 border border-cyan-700 rounded-full text-sm font-medium text-cyan-400"
        title="This is verified canonical content"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span>Verified</span>
      </div>
    {/if}

    {#if confidenceLevel !== null}
      {@const conf = getConfidenceLabel(confidenceLevel)}
      <div 
        class="inline-flex items-center gap-2 px-3 py-1.5 border rounded-full text-sm font-medium {conf.color}"
        title="Confidence level: {confidenceLevel}%"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <span>{conf.text} Confidence</span>
      </div>
    {/if}

    {#if sourceReference}
      <button 
        class="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-full text-sm font-medium text-slate-300 transition-colors"
        on:click={() => {
          const modal = document.getElementById('source-reference-modal');
          if (modal) modal.classList.remove('hidden');
        }}
        title="View source reference"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <span>Source</span>
      </button>
    {/if}

    {#if verifiedBy && verifiedAt}
      <div 
        class="inline-flex items-center gap-2 px-3 py-1.5 bg-purple-900/30 border border-purple-700 rounded-full text-sm text-purple-400"
        title="Verified by {verifiedBy} on {formatDate(verifiedAt)}"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
        </svg>
        <span class="hidden sm:inline">Verified {formatDate(verifiedAt)}</span>
        <span class="sm:hidden">Verified</span>
      </div>
    {/if}
  </div>

  <!-- Source Reference Modal -->
  {#if sourceReference}
    <div id="source-reference-modal" class="hidden fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div class="max-w-2xl w-full bg-slate-800 border border-slate-700 rounded-lg shadow-2xl overflow-hidden">
        <div class="bg-gradient-to-r from-cyan-600 to-blue-600 px-6 py-4 flex items-center justify-between">
          <h3 class="text-xl font-bold text-white">Source Reference</h3>
          <button 
            on:click={() => {
              const modal = document.getElementById('source-reference-modal');
              if (modal) modal.classList.add('hidden');
            }}
            class="text-white hover:text-slate-200 transition-colors"
            aria-label="Close source reference"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-4">
          {#if typeof sourceReference === 'object'}
            {#each Object.entries(sourceReference) as [key, value]}
              <div class="flex gap-3">
                <div class="text-sm font-semibold text-slate-400 capitalize min-w-32">{key.replace(/_/g, ' ')}:</div>
                <div class="text-sm text-slate-300 flex-1">{value}</div>
              </div>
            {/each}
          {:else}
            <p class="text-slate-300">{sourceReference}</p>
          {/if}
        </div>

        <div class="bg-slate-900 px-6 py-4 text-xs text-slate-500 border-t border-slate-700">
          This information is provided for reference and transparency.
        </div>
      </div>
    </div>
  {/if}
{/if}
