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

  const adminLinks = [
    { href: "/admin", label: "Admin" },
    { href: "/moderation", label: "Moderation" },
  ];

  const moderatorLinks = [{ href: "/moderation", label: "Moderation" }];

  $: roleKey = String(user?.role || "").toLowerCase();
  $: roleLinks = roleKey === "admin" ? adminLinks : roleKey === "moderator" ? moderatorLinks : [];
  $: showRoleLinks = roleLinks.length > 0;

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
  .dropdown { min-width: 220px; }
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
        <a href="/login" class="site-nav-link">Login</a>
        <a href="/register" class="site-nav-link">Register</a>
      </div>
    {/if}
  {:else}
    <!-- logged in -->
    {#if minimal}
      <!-- footer-only: show role text with badge styling -->
      <div class="ui-badge" data-tone="accent">
        {user.role ? user.role.toUpperCase() : "USER"}
      </div>
    {:else}
      <div class="flex items-center gap-4 auth-status-root relative z-layer-dropdown">
        <!-- username dropdown -->
        <div class="relative">
          <button class="username-btn text-sm site-nav-link" on:click={toggleDropdown} aria-haspopup="true" aria-expanded={dropdownOpen}>
            {displayName(user)}
            <span class="ml-2">▾</span>
          </button>

          {#if dropdownOpen}
            <div class="absolute right-0 mt-2 auth-dropdown dropdown p-2">
              <div class="text-sm text-fg mb-2">
                <strong>{displayName(user)}</strong><br />
                <span class="text-xs text-muted">{user.role || "user"}</span>
              </div>

              <div class="flex flex-col gap-2">
                <a class="auth-menu-link" href="/dashboard">Dashboard</a>
                <a class="auth-menu-link" href="/me/edit">Edit profile</a>
                {#if showRoleLinks}
                  <div class="border-t border-slate-700/60 my-1"></div>
                  <div class="text-xs text-muted uppercase tracking-wide px-2">Manage</div>
                  {#each roleLinks as link}
                    <a class="auth-menu-link" href={link.href}>{link.label}</a>
                  {/each}
                {/if}
                <button on:click={logout} class="auth-menu-link danger text-left">Sign out</button>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  {/if}
{/if}
