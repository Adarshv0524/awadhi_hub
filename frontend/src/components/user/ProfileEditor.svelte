<script lang="ts">
  import { onMount } from "svelte";
  const API_BASE =
    import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

  let user: any = null;
  let username = "";
  let name = "";
  let bio = "";
  let email = "";
  let role = "";
  let emailVerified = false;
  let pendingEmail: string | null = null;
  let loading = true;
  let saving = false;
  let message = "";

  async function loadUser() {
    loading = true;
    message = "";
    try {
      const token = localStorage.getItem("awadhi_access_token");
      if (!token) throw new Error("Not authenticated");

      // Always fetch the freshest profile data so email is accurate on /me/edit.
      const r = await fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
      if (!r.ok) throw new Error("Unable to load user");
      user = await r.json();
      localStorage.setItem("awadhi_user_cache", JSON.stringify(user));

      username = user.username ?? "";
      name = user.name ?? "";
      bio = user.bio ?? "";
      email = user.email ?? "";
      role = user.role ?? "registered";
      emailVerified = Boolean(user.email_verified);
      pendingEmail = user.pending_email ?? null;
    } catch (e: any) {
      console.warn(e);
      // Fallback to cache if network call fails.
      const cached = localStorage.getItem("awadhi_user_cache");
      if (cached) {
        try {
          user = JSON.parse(cached);
          username = user.username ?? "";
          name = user.name ?? "";
          bio = user.bio ?? "";
          email = user.email ?? "";
          role = user.role ?? "registered";
          emailVerified = Boolean(user.email_verified);
          pendingEmail = user.pending_email ?? null;
          message = "Showing cached profile data.";
        } catch {
          message = "Unable to load profile.";
        }
      } else {
        message = "Unable to load profile.";
      }
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
      // PATCH /users/me to update own profile
      const resp = await fetch(`${API_BASE}/users/me`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ username, name, bio, email }),
      });
      if (!resp.ok) {
        const payload = await resp.json().catch(() => ({}));
        throw new Error(payload?.detail ?? `Save failed (${resp.status})`);
      }
      const updated = await resp.json();
      const mergedUser = {
        ...(user ?? {}),
        ...updated,
        email_verified: updated.email_verification_required ? false : emailVerified,
      };
      localStorage.setItem("awadhi_user_cache", JSON.stringify(mergedUser));
      user = mergedUser;
      emailVerified = Boolean(mergedUser.email_verified);
      pendingEmail = mergedUser.pending_email ?? null;
      if (updated?.email_verification_required && updated?.pending_email) {
        message = updated?.message ?? "Verification OTP sent to your new email.";
        const userId = updated?.id ?? user?.id;
        if (userId) {
          const q = new URLSearchParams({
            user_id: String(userId),
            email: String(updated.pending_email),
            mode: "change",
          }).toString();
          window.location.href = `/verify-email?${q}`;
          return;
        }
      }

      message = "Profile updated.";
      await loadUser();
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
  <div class="max-w-2xl bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
    {#if message}
      <p class="text-sm text-cyan-300 mb-4 font-medium">{message}</p>
    {/if}

    <div class="mb-5 rounded-lg border border-slate-700 bg-slate-900/70 p-4 text-sm text-slate-300">
      <div><span class="text-slate-400">Role:</span> <span class="capitalize">{role}</span></div>
      <div><span class="text-slate-400">Email status:</span> {emailVerified ? "Verified" : "Not verified"}</div>
      {#if pendingEmail}
        <div><span class="text-slate-400">Pending email:</span> {pendingEmail}</div>
      {/if}
    </div>

    <label class="block mb-4">
      <div class="text-sm font-semibold text-cyan-300 mb-2">Name</div>
      <input class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 transition-all" bind:value={name} placeholder="Your public display name" />
    </label>

    <label class="block mb-4">
      <div class="text-sm font-semibold text-blue-300 mb-2">Username</div>
      <input class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 transition-all" bind:value={username} />
    </label>

    <label class="block mb-4">
      <div class="text-sm font-semibold text-indigo-300 mb-2">Email</div>
      <input class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/50 transition-all" bind:value={email} />
    </label>

    <label class="block mb-4">
      <div class="text-sm font-semibold text-purple-300 mb-2">Bio</div>
      <textarea
        class="w-full min-h-28 bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-400/50 transition-all"
        bind:value={bio}
        maxlength="600"
        placeholder="Tell people a little about yourself..."
      ></textarea>
      <p class="mt-1 text-xs text-slate-500">{bio.length}/600</p>
    </label>

    <div class="mt-6 flex items-center gap-3">
      <button class="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white font-semibold px-6 py-2 rounded-lg shadow-lg transition-all" on:click={save} disabled={saving}>
        {saving ? "Saving…" : "Save changes"}
      </button>
      <a class="text-slate-400 hover:text-slate-300 underline" href="/forgot-password">Change password</a>
      <a class="text-slate-400 hover:text-slate-300 underline" href="/dashboard">Cancel</a>
    </div>
  </div>
{/if}
