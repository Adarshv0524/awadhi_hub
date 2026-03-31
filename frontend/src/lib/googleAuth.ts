export type GoogleAuthOptions = {
  next?: string;
};

export function initiateGoogleAuth(options: GoogleAuthOptions = {}): void {
  const clientId = import.meta.env.PUBLIC_GOOGLE_CLIENT_ID || import.meta.env.GOOGLE_CLIENT_ID;
  const runtimeOrigin = window.location.origin.replace(/\/$/, "");
  const apiBase = (import.meta.env.PUBLIC_API_BASE || runtimeOrigin)
    .replace(/\/$/, "")
    .replace(/\/api\/v1$/, "");

  const next = options.next && options.next.startsWith("/") ? options.next : "/";

  // If frontend Google client id is not configured, delegate to backend OAuth start endpoint.
  // This keeps login working with server-side configuration only.
  if (!clientId) {
    const loginUrl = new URL(`${apiBase}/api/v1/auth/oauth/google/login`);
    loginUrl.searchParams.set("next", next);
    window.location.href = loginUrl.toString();
    return;
  }

  const state = generateState();
  const packedState = `${state}.${next}`;

  // Mirror backend state-cookie behavior so callback validation succeeds.
  document.cookie = `oauth_google_state=${encodeURIComponent(state)}; Max-Age=600; Path=/; SameSite=Lax`;

  const redirectUri = `${apiBase}/api/v1/auth/oauth/google/callback`;
  const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
  authUrl.search = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid email profile",
    state: packedState,
    access_type: "online",
    prompt: "select_account",
  }).toString();

  window.location.href = authUrl.toString();
}

function generateState(): string {
  const bytes = new Uint8Array(18);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}
