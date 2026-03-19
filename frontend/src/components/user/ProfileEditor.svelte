<script lang="ts">
  import { onMount } from "svelte";
  const API_BASE =
    import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

  let user: any = null;
  let username = "";
  let email = "";
  let loading = true;
  let saving = false;
  let message = "";

  async function loadUser() {
    loading = true;
    try {
      const cached = localStorage.getItem("awadhi_user_cache");
      if (cached) {
        user = JSON.parse(cached);
      } else {
        const token = localStorage.getItem("awadhi_access_token");
        if (!token) throw new Error("Not authenticated");
        const r = await fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
        if (!r.ok) throw new Error("Unable to load user");
        user = await r.json();
        localStorage.setItem("awadhi_user_cache", JSON.stringify(user));
      }
      username = user.username ?? "";
      email = user.email ?? "";
    } catch (e: any) {
      console.warn(e);
      message = "Unable to load profile.";
    } finally {
      loading = false;
    }
  }

  async function save() {
    saving = true;
    message = "";
    try {
      const token = localStorage.getItem("awadhi_access_token");
      if (!token) throw new Error("Not authenticated");
      // PATCH admin/users/{user_id}
      const resp = await fetch(`${API_BASE}/admin/users/${user.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ username, email }),
      });
      if (!resp.ok) {
        const payload = await resp.json().catch(() => ({}));
        throw new Error(payload?.detail ?? `Save failed (${resp.status})`);
      }
      const updated = await resp.json();
      localStorage.setItem("awadhi_user_cache", JSON.stringify(updated));
      message = "Profile updated.";
      // update page-level user display (header) by reloading
      window.location.reload();
    } catch (e: any) {
      console.warn(e);
      message = e?.message ?? "Save failed";
    } finally {
      saving = false;
    }
  }

  onMount(() => {
    if (typeof window === "undefined") return;
    loadUser();
  });
</script>

{#if loading}
  <p class="text-cyan-400">Loading…</p>
{:else}
  <div class="max-w-md bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-lg">
    {#if message}
      <p class="text-sm text-cyan-300 mb-4 font-medium">{message}</p>
    {/if}

    <label class="block mb-4">
      <div class="text-sm font-semibold text-blue-300 mb-2">Username</div>
      <input class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 transition-all" bind:value={username} />
    </label>

    <label class="block mb-4">
      <div class="text-sm font-semibold text-indigo-300 mb-2">Email</div>
      <input class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/50 transition-all" bind:value={email} />
    </label>

    <div class="mt-6 flex items-center gap-3">
      <button class="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white font-semibold px-6 py-2 rounded-lg shadow-lg transition-all" on:click={save} disabled={saving}>
        {saving ? "Saving…" : "Save changes"}
      </button>
      <a class="text-slate-400 hover:text-slate-300 underline" href="/dashboard">Cancel</a>
    </div>
  </div>
{/if}
