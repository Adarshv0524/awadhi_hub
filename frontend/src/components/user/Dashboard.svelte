<script lang="ts">
  import { onMount } from "svelte";
  const API_BASE =
    import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

  let loading = true;
  let user: any = null;
  let submissions: any[] = [];
  let bookmarks: any[] = [];
  let error = "";
  
  // Helper to convert singular content_type to plural route
  function getContentRoute(contentType: string): string {
    const routes: Record<string, string> = {
      'idiom': 'idioms',
      'article': 'articles',
      'dictionary': 'dictionary',
      'doha': 'poetry'
    };
    return routes[contentType] || contentType;
  }

  async function load() {
    loading = true;
    error = "";
    try {
      const token = localStorage.getItem("awadhi_access_token");
      if (!token) throw new Error("Not authenticated");

      // Prefer fresh profile data so dashboard reflects recent edits.
      const r = await fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
      if (r.ok) {
        user = await r.json();
        localStorage.setItem("awadhi_user_cache", JSON.stringify(user));
      } else {
        const cached = localStorage.getItem("awadhi_user_cache");
        if (!cached) throw new Error("Unable to get user");
        user = JSON.parse(cached);
      }

      // load my submissions
      if (token) {
        const s = await fetch(`${API_BASE}/submissions/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (s.ok) submissions = await s.json();
        // load bookmarks if endpoint present
        const b = await fetch(`${API_BASE}/interactions/users/${user.id}/bookmarks`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (b.ok) {
          const bData = await b.json();
          // Backend returns {count, results: [...]}
          bookmarks = bData.results || bData || [];
        }
      }
    } catch (e: any) {
      console.warn("[Dashboard] error", e);
      error = e?.message ?? "Unable to load dashboard";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (typeof window === "undefined") return;
    load();
  });

  function formatDate(s: string | undefined) {
    if (!s) return "";
    try {
      const d = new Date(s);
      return d.toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" });
    } catch {
      return s;
    }
  }
</script>

{#if loading}
  <p class="text-cyan-400">Loading your dashboard…</p>
{:else if error}
  <p class="text-red-400 font-semibold">{error}</p>
{:else}
  <section class="mb-6 bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
    <h2 class="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Profile</h2>
    <div class="text-sm text-slate-300 mt-3 space-y-1">
      <p><strong class="text-cyan-300">{user.name || user.username || user.email}</strong></p>
      {#if user.name && user.username}
        <p class="text-slate-400">@{user.username}</p>
      {/if}
      {#if user.bio}
        <p class="text-slate-300 mt-2 leading-relaxed">{user.bio}</p>
      {/if}
      <p class="text-blue-300">{user.email}</p>
      <p class="text-indigo-300">Role: <span class="font-semibold">{user.role}</span></p>
      <p class="text-purple-300">Joined: {formatDate(user.created_at ?? user.joined_at ?? user.created)}</p>
      <p class="mt-3"><a href="/me/edit" class="text-cyan-400 hover:text-cyan-300 underline font-medium">Edit profile</a></p>
    </div>
  </section>

  <section class="mb-6 bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">My submissions</h2>
      {#if submissions.length > 0}
        <a href="/submissions" class="text-sm text-cyan-400 hover:text-cyan-300 underline font-medium">View all →</a>
      {/if}
    </div>
    {#if submissions.length === 0}
      <p class="text-sm text-slate-400 mt-3">No submissions yet.</p>
    {:else}
      <ul class="mt-3 space-y-3">
        {#each submissions.slice(0, 5) as s}
          <li class="border border-slate-600 bg-slate-900 p-4 rounded-lg hover:border-blue-500 transition-colors">
            <div class="text-sm">
              <strong class="text-blue-300">{s.content_type}</strong> <span class="text-slate-500">—</span> <span class="text-indigo-300">{s.status}</span>
            </div>
            <div class="text-xs text-slate-400 mt-2">
              {s.main_text?.slice(0, 200) || "(no text)"}...
            </div>
            <div class="mt-3 text-xs">
              <a href={`/submissions/${s.id}`} class="text-cyan-400 hover:text-cyan-300 underline font-medium">Open</a>
            </div>
          </li>
        {/each}
      </ul>
      {#if submissions.length > 5}
        <p class="text-xs text-slate-500 mt-4 text-center">
          Showing 5 of {submissions.length} submissions. <a href="/submissions" class="text-cyan-400 hover:text-cyan-300 underline font-medium">View all</a>
        </p>
      {/if}
    {/if}
  </section>

  <section class="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
    <h2 class="text-lg font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">Bookmarks</h2>
    {#if bookmarks.length === 0}
      <p class="text-sm text-slate-400 mt-3">No bookmarks yet.</p>
    {:else}
      <ul class="mt-3 space-y-3">
        {#each bookmarks as b}
          <li class="border border-slate-600 bg-slate-900 p-3 rounded-lg hover:border-purple-500 transition-colors">
            <a class="text-cyan-400 hover:text-cyan-300 font-medium text-sm" href={`/${getContentRoute(b.content_type)}/${b.content_id}`}>
              {b.content_type} #{b.content_id}
            </a>
            <div class="text-xs text-slate-500 mt-1">
              Bookmarked: {formatDate(b.created_at)}
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  </section>
{/if}
