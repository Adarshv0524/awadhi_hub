<!-- src/components/ErrorDisplay.svelte -->
<script lang="ts">
  export let error: string | null = null;
  export let type: "error" | "warning" | "info" = "error";
  export let title: string | null = null;
  export let action: { label: string; onClick: () => void } | null = null;
  export let dismissible = false;
  export let onDismiss: (() => void) | null = null;

  let isDismissed = false;

  function dismiss() {
    isDismissed = true;
    if (onDismiss) onDismiss();
  }

  $: bgColor = type === "error" ? "bg-red-900/20" : type === "warning" ? "bg-yellow-900/20" : "bg-blue-900/20";
  $: borderColor = type === "error" ? "border-red-700" : type === "warning" ? "border-yellow-700" : "border-blue-700";
  $: textColor = type === "error" ? "text-red-400" : type === "warning" ? "text-yellow-400" : "text-blue-400";
  $: icon = type === "error" ? "⚠️" : type === "warning" ? "⚡" : "ℹ️";
</script>

{#if error && !isDismissed}
  <div class="p-4 {bgColor} border {borderColor} rounded-lg" role="alert">
    <div class="flex items-start gap-3">
      <div class="text-2xl">{icon}</div>
      <div class="flex-1 min-w-0">
        {#if title}
          <h3 class="font-semibold {textColor} mb-1">{title}</h3>
        {/if}
        <p class="text-sm {textColor === 'text-red-400' ? 'text-red-300' : textColor === 'text-yellow-400' ? 'text-yellow-300' : 'text-blue-300'}">
          {error}
        </p>
      </div>
      
      <div class="flex gap-2">
        {#if action}
          <button
            on:click={action.onClick}
            class="px-3 py-1 bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-200 rounded text-sm transition-colors font-medium"
          >
            {action.label}
          </button>
        {/if}
        
        {#if dismissible}
          <button
            on:click={dismiss}
            class="px-2 py-1 text-slate-400 hover:text-slate-300 transition-colors"
            aria-label="Dismiss"
          >
            ✕
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}
