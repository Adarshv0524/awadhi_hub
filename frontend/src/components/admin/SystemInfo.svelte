<!-- src/components/admin/SystemInfo.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  let rateLimits: any = null;
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      rateLimits = await api("/admin/system_settings/rate_limits");
      loading = false;
    } catch (e: any) {
      console.error("[SystemInfo] Failed to load rate limits", e);
      error = e?.message || "Failed to load system info";
      loading = false;
    }
  });
</script>

<div class="admin-panel p-4">
  <div class="flex items-center justify-between mb-3">
    <h3 class="font-semibold text-slate-200">System Rate Limits</h3>
  </div>

  {#if loading}
    <p class="text-sm text-slate-500">Loading system settings...</p>
  {:else if error}
    <p class="text-sm admin-state-bad">{error}</p>
  {:else if rateLimits}
    <div class="bg-slate-900 rounded p-3 overflow-x-auto">
      <pre class="text-xs text-slate-300 font-mono">{JSON.stringify(rateLimits.value, null, 2)}</pre>
    </div>
  {:else}
    <p class="text-sm text-slate-500">No rate limit configuration found.</p>
  {/if}
</div>
