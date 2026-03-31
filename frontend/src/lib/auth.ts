import { ApiError, api } from "./api";
import type { AuthUser } from "./schemas";

const ACCESS_KEY = "awadhi_access_token";
const REFRESH_KEY = "awadhi_refresh_token";
const USER_CACHE_KEY = "awadhi_user_cache";

export const API_BASE = (import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : ""))
  .replace(/\/$/, "")
  .replace(/\/api\/v1$/, "");

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function isLoggedIn(): boolean {
  return !!getAccessToken();
}

export async function fetchMe(force = false): Promise<AuthUser | null> {
  if (typeof window === "undefined") return null;

  if (!force) {
    const cached = localStorage.getItem(USER_CACHE_KEY);
    if (cached) return JSON.parse(cached);
  }

  try {
    const me = await api<AuthUser>("/auth/me");
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(me));
    return me;
  } catch (e) {
    if (e instanceof ApiError && (e.status === 401 || e.status === 403 || e.status === 404)) {
      clearAuth();
    }
    return null;
  }
}

// Alias for fetchMe
export const getMe = fetchMe;

export function clearAuth() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_CACHE_KEY);
}

export async function login(email: string, password: string) {
  const res = await api<{ access_token: string; refresh_token: string }>(
    "/auth/login",
    {
      method: "POST",
      body: { email, password },
    }
  );

  localStorage.setItem(ACCESS_KEY, res.access_token);
  localStorage.setItem(REFRESH_KEY, res.refresh_token);

  // immediately fetch role
  await fetchMe(true);
}

export async function logout() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (refresh) {
    try {
      await api("/auth/logout", {
        method: "POST",
        body: { refresh_token: refresh },
      });
    } catch {}
  }
  clearAuth();
}

/**
 * Logout helper: posts refresh token to API logout, clears local storage,
 * and navigates to home. Returns true if API responded ok (or was unreachable).
 */
export async function logoutAndRedirect(redirect = "/") {
  try {
    const refresh = typeof window !== "undefined" ? window.localStorage.getItem("awadhi_refresh_token") : null;
    if (refresh) {
      await fetch(`${API_BASE}/api/v1/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      }).catch(()=>{/* ignore network errors */});
    }
  } catch (err) {
    // swallow — logging is optional
    console.warn("logout error", err);
  } finally {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem("awadhi_access_token");
      window.localStorage.removeItem("awadhi_refresh_token");
      window.localStorage.removeItem("awadhi_user_cache");
      window.location.href = redirect;
    }
  }
}

/* ---- Role helpers ---- */

export async function isModerator(): Promise<boolean> {
  const me = await fetchMe();
  return me?.role === "moderator" || me?.role === "admin";
}

export async function isAdmin(): Promise<boolean> {
  const me = await fetchMe();
  return me?.role === "admin";
}
