<!-- src/components/user/MySubmissions.svelte -->
<script>
  import { onMount } from "svelte";
  import { api, ApiError } from "../../lib/api";

  let loading = true;
  let error = null;
  let user = null;
  let submissions = [];

  async function load() {
    loading = true;
    error = null;
    try {
      // /auth/me returns user info
      user = await api("/auth/me");
      // fetch user's submissions (client side)
      submissions = await api("/submissions/me?limit=100");
    } catch (e) {
      if (e instanceof ApiError) {
        // friendly message for UI
        error = e.message || "Unable to load data from API.";
      } else {
        error = String(e);
      }
    } finally {
      loading = false;
    }
  }

  onMount(load);
</script>

{#if loading}
  <div>Loading…</div>
{:else}
  {#if error}
    <div class="text-red-600">Error: {error}</div>
  {:else}
    <section class="mb-6 p-4 border rounded" id="me-profile">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
        <div>
          <div class="text-lg font-medium">@{user?.username ?? user?.email}</div>
          <div class="text-sm text-stone-600">Role: {user?.role ?? "registered"}</div>
        </div>
        <div class="text-sm text-stone-500">
          Joined: {user?.created_at ? new Date(user.created_at).toLocaleString() : "—"}
        </div>
      </div>

      <div class="mt-3 flex gap-2">
        <a href="/submit" class="px-3 py-2 rounded border hover:bg-stone-50">Create Submission</a>
        <a href="/submissions" class="px-3 py-2 rounded border hover:bg-stone-50">My Submissions</a>
        <a href="/profile/edit" class="px-3 py-2 rounded border hover:bg-stone-50">Edit Profile</a>
        {#if user?.role === "moderator" || user?.role === "admin"}
          <a href="/moderation" class="px-3 py-2 rounded border hover:bg-stone-50">Moderation Queue</a>
        {/if}
        {#if user?.role === "admin"}
          <a href="/admin" class="px-3 py-2 rounded border hover:bg-stone-50">Admin</a>
        {/if}
      </div>
    </section>

    <section class="p-4 border rounded">
      <h2 class="font-semibold mb-2">Your submissions</h2>

      {#if submissions.length === 0}
        <div class="text-sm text-stone-600">You have no submissions yet.</div>
      {:else}
        <ul>
          {#each submissions as s}
            <li class="py-2 border-b flex justify-between items-center">
              <div>
                <div class="font-medium">
                  {(s.content_type || "submission")} {s.main_text ? ` — ${String(s.main_text).slice(0,80)}` : ""}
                </div>
                <div class="text-xs text-stone-600">Status: {s.status} • Visibility: {s.visibility}</div>
              </div>
              <div class="flex gap-2">
                <a class="text-sm underline" href={`/submissions/${s.id}`}>View</a>
                <a class="text-sm underline" href={`/submissions/${s.id}`}>Edit</a>
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  {/if}
{/if}
