<!-- src/components/content/ModerationInfo.svelte -->
<script lang="ts">
  export let createdAt: string;
  export let updatedAt: string | null = null;
  export let version: number = 1;
  export let hasVersionHistory: boolean = false;
  export let contentType: string = "content";
  export let contentId: number | string;

  $: lastUpdated = updatedAt || createdAt;
  $: wasUpdated = updatedAt && updatedAt !== createdAt;

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  }

  function formatFullDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="flex flex-wrap items-center gap-4 text-sm text-slate-500 border-t border-slate-700 pt-4 mt-6">
  <!-- Last Updated -->
  <div 
    class="flex items-center gap-2"
    title={formatFullDate(lastUpdated)}
  >
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span>
      {#if wasUpdated}
        <span class="text-slate-400">Updated</span> {formatDate(lastUpdated)}
      {:else}
        <span class="text-slate-400">Added</span> {formatDate(createdAt)}
      {/if}
    </span>
  </div>

  <!-- Version -->
  {#if version > 1}
    <div class="flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
      </svg>
      <span class="text-slate-400">Version {version}</span>
    </div>
  {/if}

  <!-- Version History Link -->
  {#if hasVersionHistory}
    <button 
      class="flex items-center gap-2 hover:text-cyan-400 transition-colors group"
      on:click={() => {
        // Open version history modal or navigate to history page
        window.location.href = `/content/${contentType}/${contentId}/history`;
      }}
    >
      <svg class="w-4 h-4 group-hover:text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span class="underline decoration-dotted">Version history available</span>
    </button>
  {/if}
</div>
