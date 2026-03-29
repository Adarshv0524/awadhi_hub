<script lang="ts">
  export let history: Array<{ version: number; updated_at?: string }> = [];
</script>

<div class="rounded-md border border-slate-700/60 bg-slate-900/40 p-3">
  <h3 class="text-sm font-semibold text-slate-200">Content History</h3>
  {#if history.length === 0}
    <p class="mt-2 text-sm text-slate-400">No version history available.</p>
  {:else}
    <ul class="mt-2 space-y-1 text-sm text-slate-300">
      {#each history as item}
        <li>Version {item.version}{item.updated_at ? ` - ${item.updated_at}` : ""}</li>
      {/each}
    </ul>
  {/if}
</div>
