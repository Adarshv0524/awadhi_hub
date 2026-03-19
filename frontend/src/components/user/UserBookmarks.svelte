<!-- src/components/user/UserBookmarks.svelte -->
<script>
  import { onMount } from "svelte";
  import { api } from "../../lib/api";
  export let userId; // numeric

  let loading = true;
  let bookmarks = [];
  let error = null;
  
  // Helper to convert singular content_type to plural route
  function getContentRoute(contentType) {
    const routes = {
      'idiom': 'idioms',
      'article': 'articles',
      'dictionary': 'dictionary',
      'doha': 'doha'
    };
    return routes[contentType] || contentType;
  }

  async function load() {
    try {
      loading = true;
      const res = await api(`/interactions/users/${userId}/bookmarks?limit=50`);
      bookmarks = res;
    } catch (e) {
      error = e?.message ?? String(e);
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

{#if loading}
  <div>Loading bookmarks…</div>
{:else if error}
  <div class="text-sm text-red-600">Error: {error}</div>
{:else if bookmarks.length === 0}
  <div class="text-sm text-stone-600">No bookmarks yet.</div>
{:else}
  <ul>
    {#each bookmarks as b}
      <li class="py-2 border-b">
        <a class="underline" href={`/${getContentRoute(b.content_type)}/${b.content_id}`}>
          {b.title_or_text ?? `${b.content_type} #${b.content_id}`}
        </a>
        <div class="text-xs text-stone-600">Saved at: {new Date(b.created_at ?? Date.now()).toLocaleString()}</div>
      </li>
    {/each}
  </ul>
{/if}
