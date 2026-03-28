import { writable } from "svelte/store";

import { fetchMe } from "../auth";

export type AuthSessionState = {
  loading: boolean;
  user: any | null;
  error: string;
};

const initialState: AuthSessionState = {
  loading: true,
  user: null,
  error: "",
};

const sessionStore = writable<AuthSessionState>(initialState);
let inflightLoad: Promise<void> | null = null;

export const authSession = {
  subscribe: sessionStore.subscribe,
};

export async function ensureAuthLoaded(force = false): Promise<void> {
  if (inflightLoad && !force) {
    return inflightLoad;
  }

  inflightLoad = (async () => {
    sessionStore.update((prev) => ({ ...prev, loading: true, error: "" }));
    try {
      const me = await fetchMe(force);
      sessionStore.set({ loading: false, user: me, error: "" });
    } catch {
      sessionStore.set({ loading: false, user: null, error: "Unable to load session." });
    } finally {
      inflightLoad = null;
    }
  })();

  return inflightLoad;
}

export function clearAuthSession(): void {
  sessionStore.set({ loading: false, user: null, error: "" });
}
