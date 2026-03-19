<!-- EmptyState.svelte - Reusable empty state component -->
<script lang="ts">
  export let icon: string = "📭";
  export let title: string = "Nothing here yet";
  export let description: string = "";
  export let actionText: string = "";
  export let actionHref: string = "";
  export let actionClick: (() => void) | undefined = undefined;
</script>

<div class="flex flex-col items-center justify-center py-12 px-4 text-center">
  <!-- Icon/Emoji -->
  <div class="text-6xl mb-4 select-none" role="img" aria-label={title}>
    {icon}
  </div>

  <!-- Title -->
  <h3 class="text-xl font-semibold text-gray-200 mb-2">
    {title}
  </h3>

  <!-- Description -->
  {#if description}
    <p class="text-gray-400 max-w-md mb-6">
      {description}
    </p>
  {/if}

  <!-- Action Button -->
  {#if actionText}
    {#if actionHref}
      <a 
        href={actionHref}
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        {actionText}
      </a>
    {:else if actionClick}
      <button
        type="button"
        on:click={actionClick}
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        {actionText}
      </button>
    {/if}
  {/if}

  <!-- Slot for custom content -->
  <slot />
</div>
