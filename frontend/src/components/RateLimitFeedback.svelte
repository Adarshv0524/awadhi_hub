<!-- src/components/RateLimitFeedback.svelte -->
<script lang="ts">
  export let show = false;
  export let retryAfter: number | null = null; // seconds
  export let message = "Rate limit exceeded";
  export let onDismiss: (() => void) | null = null;

  let countdown = retryAfter || 0;
  let interval: number | null = null;

  $: if (show && retryAfter) {
    countdown = retryAfter;
    if (typeof window !== "undefined") {
      if (interval) clearInterval(interval);
      interval = window.setInterval(() => {
        countdown -= 1;
        if (countdown <= 0) {
          if (interval) clearInterval(interval);
          interval = null;
          dismiss();
        }
      }, 1000);
    }
  }

  function dismiss() {
    show = false;
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
    if (onDismiss) onDismiss();
  }

  function formatTime(seconds: number): string {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  }
</script>

{#if show}
  <div 
    class="fixed bottom-4 right-4 max-w-md bg-slate-800 border-2 border-yellow-500 rounded-lg shadow-2xl overflow-hidden z-40 animate-in slide-in-from-bottom-5"
    role="alert"
    aria-live="polite"
  >
    <!-- Header -->
    <div class="bg-gradient-to-r from-yellow-600 to-orange-600 px-4 py-3">
      <div class="flex items-center gap-2">
        <div class="text-2xl">⏱️</div>
        <div>
          <h3 class="font-bold text-white">Rate Limit Reached</h3>
        </div>
      </div>
    </div>

    <!-- Body -->
    <div class="p-4 space-y-3">
      <p class="text-slate-300 text-sm">
        {message}
      </p>

      {#if countdown > 0}
        <div class="flex items-center gap-3 p-3 bg-yellow-900/30 border border-yellow-700/50 rounded">
          <div class="flex-1">
            <div class="text-xs text-yellow-200/80 mb-1">Please wait</div>
            <div class="text-2xl font-bold text-yellow-400">{formatTime(countdown)}</div>
          </div>
          <div class="w-12 h-12 rounded-full border-4 border-yellow-600 border-t-transparent animate-spin"></div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
          <div 
            class="bg-gradient-to-r from-yellow-500 to-orange-500 h-2 rounded-full transition-all duration-1000"
            style="width: {retryAfter ? ((retryAfter - countdown) / retryAfter) * 100 : 0}%"
          ></div>
        </div>
      {/if}

      <!-- Dismiss Button -->
      <button
        on:click={dismiss}
        class="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-200 rounded transition-colors text-sm font-medium"
      >
        ✕ Dismiss
      </button>

      <!-- Info -->
      <p class="text-xs text-slate-500 text-center">
        This helps ensure fair usage for all users.
      </p>
    </div>
  </div>
{/if}

<style>
  @keyframes slide-in-from-bottom-5 {
    from {
      transform: translateY(1.25rem);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .animate-in {
    animation: slide-in-from-bottom-5 0.3s ease-out;
  }
</style>
