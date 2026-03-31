// src/lib/api.ts
export const API_BASE =
  (import.meta.env.PUBLIC_API_BASE ||
    (import.meta.env.DEV ? "http://localhost:8000" : ""))
    .replace(/\/$/, "")
    .replace(/\/api\/v1$/, "");

export const API_V1_PREFIX = "/api/v1";

export function toApiV1Path(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized === API_V1_PREFIX || normalized.startsWith(`${API_V1_PREFIX}/`)) {
    return normalized;
  }
  return `${API_V1_PREFIX}${normalized}`;
}

if (!API_BASE) {
  console.warn(
    "[api] PUBLIC_API_BASE not set. API calls will fail in production."
  );
}

export class ApiError extends Error {
  status: number;
  payload?: unknown;
  constructor(status: number, message: string, payload?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

type ApiOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  // allow opting out of credentials for special cases
  credentials?: RequestCredentials;
  // Server-side auth token (for SSR)
  serverAuthToken?: string;
};

const loggedNetworkErrors = new Set<string>();

// Token refresh state management
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
}

async function refreshAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  
  const refreshToken = window.localStorage.getItem("awadhi_refresh_token");
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE}${toApiV1Path("/auth/refresh")}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Refresh token expired or invalid, logout user
      if (typeof window !== "undefined") {
        window.localStorage.removeItem("awadhi_access_token");
        window.localStorage.removeItem("awadhi_refresh_token");
        window.localStorage.removeItem("awadhi_user_cache");
      }
      return null;
    }

    const data = await response.json();
    const newAccessToken = data.access_token;
    
    if (typeof window !== "undefined") {
      window.localStorage.setItem("awadhi_access_token", newAccessToken);
    }
    
    return newAccessToken;
  } catch (error) {
    console.error("[api] Token refresh failed:", error);
    return null;
  }
}

function getClientAuthHeader(): Record<string, string> {
  // Only available in browser
  try {
    if (typeof window === "undefined") return {};
    const token = window.localStorage.getItem("awadhi_access_token");
    if (token) return { Authorization: `Bearer ${token}` };
  } catch (e) {
    // ignore
  }
  return {};
}

export async function api<T = any>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const { method = "GET", body, headers = {}, credentials, serverAuthToken } = options;

  const fetchOptions: RequestInit = {
    method,
    credentials: credentials ?? "include", // default: include for cookie auth on SSR
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...getClientAuthHeader(),
      // Server-side token takes precedence
      ...(serverAuthToken ? { Authorization: `Bearer ${serverAuthToken}` } : {}),
      ...headers,
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  };

  const normalizedPath = toApiV1Path(path);

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${normalizedPath}`, fetchOptions);
  } catch (networkError) {
    const url = `${API_BASE}${normalizedPath}`;
    const anyErr = networkError as any;
    const code: string | undefined = anyErr?.cause?.code ?? anyErr?.code;
    const key = `${code ?? "UNKNOWN"}|${API_BASE}`;

    let hint = "";
    if (code === "ECONNREFUSED") {
      hint = `Connection refused. The backend is likely not running at ${API_BASE} or the port is wrong.`;
    } else if (code === "ENOTFOUND") {
      hint = `Host not found. Check that PUBLIC_API_BASE is correct (currently ${API_BASE}).`;
    } else if (code === "ETIMEDOUT") {
      hint = `Connection timed out. The backend at ${API_BASE} may be slow/unreachable.`;
    }

    if (import.meta.env.DEV && !loggedNetworkErrors.has(key)) {
      loggedNetworkErrors.add(key);
      // Intentionally do NOT log the raw error object here.
      // Node/undici errors include a large stack trace that clutters `astro dev` output.
      // The hint + url are enough to diagnose (backend down / wrong port / wrong host).
      console.warn("[api] fetch failed", { url, path, code, hint });
    }

    throw new ApiError(0, hint || "Network error", { url, code });
  }

  const contentType = response.headers.get("content-type") || "";
  let payload: unknown = null;

  if (contentType.includes("application/json")) {
    try {
      payload = await response.json();
    } catch (e) {
      payload = null;
    }
  } else {
    // fallback to text
    try {
      payload = await response.text();
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    if (import.meta.env.DEV) {
      console.error("[api] Response error", { path, status: response.status, payload });
    }
    
    // Handle 401 Unauthorized - attempt token refresh
    if (response.status === 401 && typeof window !== "undefined") {
      const accessToken = window.localStorage.getItem("awadhi_access_token");
      
      // Only attempt refresh if we had a token (i.e., user was authenticated)
      if (accessToken) {
        if (!isRefreshing) {
          isRefreshing = true;
          const newToken = await refreshAccessToken();
          isRefreshing = false;
          
          if (newToken) {
            onRefreshed(newToken);
            
            // Retry the original request with new token
            const retryHeaders = {
              ...fetchOptions.headers,
              Authorization: `Bearer ${newToken}`,
            };
            
            const retryResponse = await fetch(`${API_BASE}${normalizedPath}`, {
              ...fetchOptions,
              headers: retryHeaders,
            });
            
            if (retryResponse.ok) {
              const retryPayload = await retryResponse.json().catch(() => null);
              return retryPayload as T;
            }
          } else {
            // Refresh failed, redirect to login
            window.location.href = "/login?session_expired=1";
            throw new ApiError(401, "Session expired. Please log in again.", payload);
          }
        } else {
          // Wait for the ongoing refresh to complete
          return new Promise((resolve, reject) => {
            subscribeTokenRefresh(async (newToken: string) => {
              const retryHeaders = {
                ...fetchOptions.headers,
                Authorization: `Bearer ${newToken}`,
              };
              
              try {
                const retryResponse = await fetch(`${API_BASE}${normalizedPath}`, {
                  ...fetchOptions,
                  headers: retryHeaders,
                });
                
                if (retryResponse.ok) {
                  const retryPayload = await retryResponse.json().catch(() => null);
                  resolve(retryPayload as T);
                } else {
                  reject(new ApiError(retryResponse.status, "Request failed after token refresh"));
                }
              } catch (error) {
                reject(error);
              }
            });
          });
        }
      }
    }
    
    const msg =
      typeof payload === "object" && payload !== null
        ? "API request failed"
        : String(payload || response.statusText);
    throw new ApiError(response.status, msg, payload);
  }

  return payload as T;
}
