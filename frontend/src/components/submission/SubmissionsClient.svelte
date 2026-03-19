<script lang="ts">
  import { onMount } from "svelte";
  import { listMySubmissions } from "../../lib/submissions";

  let items: any[] = [];
  let loading = true;
  let error = "";

  async function load() {
    try {
      items = await listMySubmissions();
    } catch (e: any) {
      error = e.message || "Failed to load submissions";
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

{#if loading}
  <p>Loading…</p>
{:else if error}
  <p class="text-red-600">{error}</p>
{:else if items.length === 0}
  <p class="text-stone-600">You haven’t submitted anything yet.</p>
{:else}
  <ul class="space-y-3">
    {#each items as s}
      <li class="border p-3 rounded">
        <div class="font-medium">
          {s.content_type} #{s.id}
        </div>
        <div class="text-sm text-stone-600">
          Status: {s.status} • {new Date(s.created_at).toLocaleString()}
        </div>
      </li>
    {/each}
  </ul>
{/if}
