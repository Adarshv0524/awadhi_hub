<!-- ContentSkeleton.svelte - Reusable loading skeleton for content pages -->
<script lang="ts">
  export let variant: 'detail' | 'list' | 'card' = 'detail';
  export let count: number = 1;
</script>

{#if variant === 'detail'}
  <!-- Detail page skeleton (doha/[id], dictionary/[id], etc.) -->
  <div class="max-w-4xl mx-auto px-4 py-8 animate-pulse">
    <!-- Header skeleton -->
    <div class="mb-6">
      <div class="h-8 bg-gray-700 rounded w-3/4 mb-3"></div>
      <div class="h-4 bg-gray-700 rounded w-1/2"></div>
    </div>

    <!-- Main content skeleton -->
    <div class="bg-gray-800 rounded-lg p-6 mb-6">
      <div class="space-y-3">
        <div class="h-6 bg-gray-700 rounded w-full"></div>
        <div class="h-6 bg-gray-700 rounded w-11/12"></div>
        <div class="h-6 bg-gray-700 rounded w-10/12"></div>
      </div>
    </div>

    <!-- Metadata skeleton -->
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="h-20 bg-gray-700 rounded"></div>
      <div class="h-20 bg-gray-700 rounded"></div>
    </div>

    <!-- Interaction bar skeleton -->
    <div class="flex gap-4 mb-8">
      <div class="h-10 bg-gray-700 rounded w-24"></div>
      <div class="h-10 bg-gray-700 rounded w-24"></div>
      <div class="h-10 bg-gray-700 rounded w-24"></div>
    </div>

    <!-- Recommendations skeleton -->
    <div class="space-y-3">
      <div class="h-6 bg-gray-700 rounded w-48 mb-4"></div>
      <div class="h-16 bg-gray-700 rounded"></div>
      <div class="h-16 bg-gray-700 rounded"></div>
      <div class="h-16 bg-gray-700 rounded"></div>
    </div>
  </div>

{:else if variant === 'list'}
  <!-- List page skeleton (doha, dictionary, etc.) -->
  <div class="max-w-4xl mx-auto px-4 py-8">
    {#each Array(count) as _, i}
      <div class="bg-gray-800 rounded-lg p-6 mb-4 animate-pulse" style="animation-delay: {i * 100}ms">
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <div class="h-6 bg-gray-700 rounded w-3/4 mb-2"></div>
            <div class="h-4 bg-gray-700 rounded w-1/2"></div>
          </div>
          <div class="h-8 w-8 bg-gray-700 rounded-full"></div>
        </div>
        <div class="space-y-2">
          <div class="h-4 bg-gray-700 rounded w-full"></div>
          <div class="h-4 bg-gray-700 rounded w-5/6"></div>
        </div>
      </div>
    {/each}
  </div>

{:else if variant === 'card'}
  <!-- Card grid skeleton (for search results, recommendations) -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each Array(count) as _, i}
      <div class="bg-gray-800 rounded-lg p-4 animate-pulse" style="animation-delay: {i * 100}ms">
        <div class="h-5 bg-gray-700 rounded w-3/4 mb-3"></div>
        <div class="space-y-2">
          <div class="h-3 bg-gray-700 rounded w-full"></div>
          <div class="h-3 bg-gray-700 rounded w-5/6"></div>
          <div class="h-3 bg-gray-700 rounded w-4/6"></div>
        </div>
        <div class="flex gap-2 mt-4">
          <div class="h-6 bg-gray-700 rounded w-16"></div>
          <div class="h-6 bg-gray-700 rounded w-16"></div>
        </div>
      </div>
    {/each}
  </div>
{/if}

<style>
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>
