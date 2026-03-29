<script lang="ts">
  import { onMount } from "svelte";
  import { get } from "svelte/store";

  import { authSession, clearAuthSession, ensureAuthLoaded } from "../../lib/stores/authSession";

  // prefer the Vite/astro env var; fallback in DEV to localhost
  const API_BASE =
    import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

  export let minimal = false; // if true render only role (used in footer)
  export let mobile = false;

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
    return u.name || u.username || u.email || "Me";
  }

  // toggle dropdown
  function toggleDropdown() {
    dropdownOpen = !dropdownOpen;
  }

  function closeDropdown() {
    dropdownOpen = false;
  }

  // close on outside click
  function onDocumentClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.closest(".auth-status-root")) {
      dropdownOpen = false;
    }
  }

  function onDocumentKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
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
    document.addEventListener("keydown", onDocumentKeydown);

    return () => {
      unsubscribe();
      document.removeEventListener("click", onDocumentClick);
      document.removeEventListener("keydown", onDocumentKeydown);
    };
  });
</script>

<style>
  /* small local styles; tailwind exists but keep fallback */
  .username-btn { cursor: pointer; }
  .dropdown { min-width: 220px; }
  .mobile-auth-root {
    width: 100%;
  }

  .mobile-auth-root .username-btn {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .mobile-auth-root .dropdown {
    min-width: 0;
    width: 100%;
  }
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
      <div class={`auth-status-root ${mobile ? "mobile-auth-root" : "flex items-center gap-3"}`}>
        <div class={mobile ? "grid grid-cols-2 gap-2" : "flex items-center gap-3"}>
          <a href="/login" class="site-nav-link text-center">Login</a>
          <a href="/register" class="site-nav-link text-center">Register</a>
        </div>
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
      <div class={`auth-status-root relative z-layer-dropdown ${mobile ? "mobile-auth-root" : "flex items-center gap-4"}`}>
        <!-- username dropdown -->
        <div class={`relative ${mobile ? "w-full" : ""}`}>
          <button class="username-btn text-sm site-nav-link" on:click={toggleDropdown} aria-haspopup="true" aria-expanded={dropdownOpen} aria-controls="auth-user-menu">
            {displayName(user)}
            <span class="ml-2">▾</span>
          </button>

          {#if dropdownOpen}
            <div id="auth-user-menu" class={`auth-dropdown dropdown p-2 ${mobile ? "mt-2" : "absolute right-0 mt-2"}`}>
              <div class="text-sm text-fg mb-2">
                <strong>{displayName(user)}</strong><br />
                <span class="text-xs text-muted">{user.role || "user"}</span>
              </div>

              <div class="flex flex-col gap-2">
                <a class="auth-menu-link" href="/dashboard" on:click={closeDropdown}>Dashboard</a>
                <a class="auth-menu-link" href="/me/edit" on:click={closeDropdown}>Edit profile</a>
                {#if showRoleLinks}
                  <div class="border-t border-slate-700/60 my-1"></div>
                  <div class="text-xs text-muted uppercase tracking-wide px-2">Manage</div>
                  {#each roleLinks as link}
                    <a class="auth-menu-link" href={link.href} on:click={closeDropdown}>{link.label}</a>
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
