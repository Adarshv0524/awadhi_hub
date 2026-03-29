<!-- src/components/ErrorBoundary.svelte -->
<script lang="ts">
  import { onMount } from "svelte";

  export let showBoundary = false;
  export let errorMessage = "";
  export let errorDetails = "";

  let isDismissed = false;

  function dismiss() {
    isDismissed = true;
    showBoundary = false;
  }

  function reload() {
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  }

  onMount(() => {
    // Global error handler
    const handleError = (event: ErrorEvent) => {
      console.error("[ErrorBoundary] Caught error:", event.error);
      errorMessage = event.error?.message || "An unexpected error occurred";
      errorDetails = event.error?.stack || "";
      showBoundary = true;
      isDismissed = false;
      event.preventDefault();
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error("[ErrorBoundary] Unhandled promise rejection:", event.reason);
      errorMessage = event.reason?.message || "An unexpected error occurred";
      errorDetails = event.reason?.stack || String(event.reason);
      showBoundary = true;
      isDismissed = false;
      event.preventDefault();
    };

    if (typeof window !== "undefined") {
      window.addEventListener("error", handleError);
      window.addEventListener("unhandledrejection", handleUnhandledRejection);

      return () => {
        window.removeEventListener("error", handleError);
        window.removeEventListener("unhandledrejection", handleUnhandledRejection);
      };
    }
  });
</script>

{#if showBoundary && !isDismissed}
  <div 
    class="fixed inset-0 bg-black/80 z-layer-overlay flex items-center justify-center p-4 backdrop-blur-sm"
    role="alert"
    aria-live="assertive"
  >
    <div class="max-w-2xl w-full bg-slate-800 border-2 border-red-500 rounded-lg shadow-2xl overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-red-600 to-rose-600 px-6 py-4">
        <div class="flex items-center gap-3">
          <div class="text-3xl">⚠️</div>
          <div>
            <h2 class="text-xl font-bold text-white">Something Went Wrong</h2>
            <p class="text-red-100 text-sm mt-1">An error occurred while processing your request</p>
          </div>
        </div>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-4">
        <!-- Error Message -->
        <div class="p-4 bg-red-900/30 border border-red-700/50 rounded-lg">
          <p class="text-red-200 font-medium">{errorMessage}</p>
        </div>

        {#if errorDetails && import.meta.env.DEV}
          <!-- Error Details (Dev Only) -->
          <details class="text-xs">
            <summary class="cursor-pointer text-slate-400 hover:text-slate-300 mb-2">
              Show technical details
            </summary>
            <pre class="bg-slate-900 p-3 rounded border border-slate-700 overflow-x-auto text-slate-400 max-h-40 overflow-y-auto">{errorDetails}</pre>
          </details>
        {/if}

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-3 pt-4">
          <button
            on:click={reload}
            class="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-lg transition-all font-medium shadow-lg"
          >
            🔄 Reload Page
          </button>
          <button
            on:click={dismiss}
            class="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-200 rounded-lg transition-colors font-medium"
          >
            ✕ Dismiss
          </button>
        </div>

        <!-- Help Text -->
        <p class="text-sm text-slate-500 text-center pt-2">
          If this error persists, please contact support or try again later.
        </p>
      </div>
    </div>
  </div>
{/if}
