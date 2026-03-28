export type GoogleAuthOptions = {
  next?: string;
};

export function initiateGoogleAuth(options: GoogleAuthOptions = {}): void {
  const clientId = import.meta.env.PUBLIC_GOOGLE_CLIENT_ID;
  const runtimeOrigin = window.location.origin.replace(/\/$/, "");
  const apiBase = (import.meta.env.PUBLIC_API_BASE || runtimeOrigin).replace(/\/$/, "");

  if (!clientId) {
    throw new Error("PUBLIC_GOOGLE_CLIENT_ID is not configured");
  }

  const next = options.next && options.next.startsWith("/") ? options.next : "/";
  const state = generateState();
  const packedState = `${state}.${next}`;

  // Mirror backend state-cookie behavior so callback validation succeeds.
  document.cookie = `oauth_google_state=${encodeURIComponent(state)}; Max-Age=600; Path=/; SameSite=Lax`;

  const redirectUri = `${apiBase}/auth/oauth/google/callback`;
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
