<script lang="ts">
  import { onMount } from "svelte";
  import { get } from "svelte/store";

  import { authSession, clearAuthSession, ensureAuthLoaded } from "../../lib/stores/authSession";

  // prefer the Vite/astro env var; fallback in DEV to localhost
  const API_BASE =
    import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

  export let minimal = false; // if true render only role (used in footer)

  export let user: any = null;
  let loading = true;
  let dropdownOpen = false;
  let errorMsg = "";

  function clearAuthCache() {
    try {
      localStorage.removeItem("awadhi_access_token");
      localStorage.removeItem("awadhi_refresh_token");
      localStorage.removeItem("awadhi_user_cache");
    } catch (e) {
      // ignore
    }
  }

  async function logout() {
    // call backend logout with refresh token (best effort)
    const refresh_token = localStorage.getItem("awadhi_refresh_token");
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token }),
      });
    } catch (e) {
      // swallow network error - we'll still clear local cache
      console.warn("[AuthStatus] logout network error", e);
    } finally {
      clearAuthCache();
      clearAuthSession();
      // make sure other parts of the app re-check
      user = null;
      // redirect to home
      window.location.href = "/";
    }
  }

  function syncFromStore() {
    const state = get(authSession);
    loading = state.loading;
    user = state.user;
    errorMsg = state.error;
  }

  function displayName(u: any) {
    if (!u) return "";
    return u.username || u.email || "Me";
  }

  // toggle dropdown
  function toggleDropdown() {
    dropdownOpen = !dropdownOpen;
  }

  // close on outside click
  function onDocumentClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.closest(".auth-status-root")) {
      dropdownOpen = false;
    }
  }

  onMount(() => {
    // always run client-only
    if (typeof window === "undefined") return;

    const unsubscribe = authSession.subscribe((state) => {
      loading = state.loading;
      user = state.user;
      errorMsg = state.error;
    });

    syncFromStore();
    ensureAuthLoaded();
    document.addEventListener("click", onDocumentClick);

    return () => {
      unsubscribe();
      document.removeEventListener("click", onDocumentClick);
    };
  });
</script>

<style>
  /* small local styles; tailwind exists but keep fallback */
  .username-btn { cursor: pointer; }
  .dropdown { min-width: 180px; }
</style>

{#if loading}
  <!-- while loading show nothing (keeps SSR markup identical) -->
  <span class="sr-only">loading auth</span>
{:else}
  {#if !user}
    <!-- not logged in -->
    {#if minimal}
      <span></span>
    {:else}
      <div class="flex items-center gap-3 auth-status-root">
        <a href="/login" class="hover:underline">Login</a>
        <a href="/register" class="hover:underline">Register</a>
      </div>
    {/if}
  {:else}
    <!-- logged in -->
    {#if minimal}
      <!-- footer-only: show role text with badge styling -->
      <div class="text-xs font-bold px-3 py-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg">
        {user.role ? user.role.toUpperCase() : "USER"}
      </div>
    {:else}
      <div class="flex items-center gap-4 auth-status-root">
        <!-- role-based quick links -->
        <nav class="hidden md:flex items-center gap-3" aria-label="role links">
          {#if user.role === "moderator" || user.role === "admin"}
            <a href="/moderation" class="hover:underline">Moderation</a>
          {/if}
          {#if user.role === "admin"}
            <a href="/admin" class="hover:underline">Admin</a>
          {/if}
          <a href="/dashboard" class="hover:underline">Dashboard</a>
        </nav>

        <!-- username dropdown -->
        <div class="relative">
          <button class="username-btn text-sm" on:click={toggleDropdown} aria-haspopup="true" aria-expanded={dropdownOpen}>
            {displayName(user)}
            <span class="ml-2">▾</span>
          </button>

          {#if dropdownOpen}
            <div class="absolute right-0 mt-2 bg-white border shadow dropdown z-50 p-2 rounded">
              <div class="text-sm text-stone-700 mb-2">
                <strong>{displayName(user)}</strong><br />
                <span class="text-xs text-stone-500">{user.role || "user"}</span>
              </div>

              <div class="flex flex-col gap-2">
                <a class="hover:underline" href="/dashboard">Dashboard</a>
                <a class="hover:underline" href="/me/edit">Edit profile</a>
                <button on:click={logout} class="text-left hover:underline">Sign out</button>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  {/if}
{/if}
