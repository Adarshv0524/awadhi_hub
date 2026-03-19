// src/lib/admin.ts
// Centralized admin API wrapper

const API_BASE = import.meta.env.PUBLIC_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

function resolveApiBase(override?: string): string {
  return (override && override.trim()) || API_BASE;
}

function localFallbackBase(base: string): string | null {
  if (base.includes("127.0.0.1")) return base.replace("127.0.0.1", "localhost");
  if (base.includes("localhost")) return base.replace("localhost", "127.0.0.1");
  return null;
}

async function fetchWithLocalFallback(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch (e: any) {
    const failedToFetch = e?.message === "Failed to fetch";
    if (!failedToFetch) throw e;

    const fallbackUrl = url.includes("127.0.0.1")
      ? url.replace("127.0.0.1", "localhost")
      : url.includes("localhost")
      ? url.replace("localhost", "127.0.0.1")
      : null;

    if (!fallbackUrl) throw e;
    return await fetch(fallbackUrl, init);
  }
}

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("awadhi_access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  role: string;
  permissions: number;
  permission_scopes?: any;
  created_at: string;
  is_active: boolean;
  is_banned?: boolean;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  username: string | null;
  action: string;
  resource_type: string | null;
  resource_id: number | null;
  details: any;
  ip_address: string | null;
  created_at: string;
}

export interface Setting {
  key: string;
  value: any;
  description: string | null;
}

export interface Author {
  id: number;
  slug: string;
  name: string;
  language: string | null;
  short_bio: string | null;
}

export interface Work {
  id: number;
  slug: string;
  title: string;
  author_id: number;
  description: string | null;
}

export interface Chapter {
  id: number;
  slug: string;
  title: string;
  work_id: number;
  order_num: number;
}

export interface PaginatedResponse<T> {
  total: number;
  results: T[];
}

export interface ModerationSubmission {
  id: number;
  content_type: string;
  title: string;
  status: string;
  submitted_by_id: number;
  submitted_by_username: string;
  assigned_to_id: number | null;
  assigned_to_username: string | null;
  created_at: string;
}

// User Management
export async function getUsers(limit = 100, offset = 0, apiBaseOverride?: string): Promise<AdminUser[]> {
  const base = resolveApiBase(apiBaseOverride);
  if (!base) {
    throw new Error("Admin API base URL is not configured. Set PUBLIC_API_BASE.");
  }

  try {
    const res = await fetchWithLocalFallback(`${base}/admin/users?limit=${limit}&offset=${offset}`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) throw new Error(`Failed to fetch users: ${res.status}`);
    return res.json();
  } catch (e: any) {
    if (e?.message === "Failed to fetch") {
      const fallback = localFallbackBase(base);
      const tried = fallback ? `${base} and ${fallback}` : base;
      throw new Error(`Failed to connect to backend at ${tried}. Check backend server and CORS settings.`);
    }
    throw e;
  }
}

export async function updateUserRole(userId: number, role: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/users/${userId}/role`, {
    method: "PATCH",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
  if (!res.ok) throw new Error(`Failed to update role: ${res.status}`);
}

export async function updateUser(userId: number, data: {
  role?: string;
  permissions?: number;
  permission_scopes?: any;
  is_active?: boolean;
  is_banned?: boolean;
}, apiBaseOverride?: string): Promise<void> {
  const base = resolveApiBase(apiBaseOverride);
  if (!base) {
    throw new Error("Admin API base URL is not configured. Set PUBLIC_API_BASE.");
  }

  const res = await fetchWithLocalFallback(`${base}/admin/users/${userId}`, {
    method: "PATCH",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update user: ${res.status}`);
}

export async function deactivateUser(userId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/users/${userId}/deactivate`, {
    method: "POST",
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to deactivate user: ${res.status}`);
}

// Audit Logs
export async function getAuditLogs(limit = 50, offset = 0): Promise<PaginatedResponse<AuditLog>> {
  const res = await fetch(`${API_BASE}/admin/audit_logs?limit=${limit}&offset=${offset}`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to fetch audit logs: ${res.status}`);
  return res.json();
}

export async function exportAuditLogsCSV(): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/audit-logs/export-csv`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to export audit logs: ${res.status}`);
  
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// System Settings
export async function getSettings(): Promise<Setting[]> {
  const res = await fetch(`${API_BASE}/admin/system_settings`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to fetch settings: ${res.status}`);
  return res.json();
}

export async function updateSetting(key: string, value: any): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/system_settings/${key}`, {
    method: "PUT",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
  if (!res.ok) throw new Error(`Failed to update setting: ${res.status}`);
}

export async function deleteSetting(key: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/system_settings/${key}`, {
    method: "DELETE",
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to delete setting: ${res.status}`);
}

// Hierarchy Management
export async function getAuthors(limit = 100): Promise<Author[]> {
  const res = await fetch(`${API_BASE}/authors?limit=${limit}`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to fetch authors: ${res.status}`);
  return res.json();
}

export async function createAuthor(data: { slug: string; name: string; language?: string; short_bio?: string }): Promise<Author> {
  const res = await fetch(`${API_BASE}/admin/hierarchy/authors`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create author: ${res.status}`);
  return res.json();
}

export async function getWorks(authorSlug: string, limit = 50): Promise<Work[]> {
  const res = await fetch(`${API_BASE}/authors/${authorSlug}/works?limit=${limit}`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to fetch works: ${res.status}`);
  return res.json();
}

export async function createWork(authorId: number, data: { slug: string; title: string; description?: string }): Promise<Work> {
  const res = await fetch(`${API_BASE}/admin/hierarchy/authors/${authorId}/works`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create work: ${res.status}`);
  return res.json();
}

export async function getChapters(authorSlug: string, workSlug: string, limit = 200): Promise<Chapter[]> {
  const res = await fetch(`${API_BASE}/authors/${authorSlug}/works/${workSlug}/chapters?limit=${limit}`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to fetch chapters: ${res.status}`);
  return res.json();
}

export async function createChapter(workId: number, data: { slug: string; title: string; order_num: number }): Promise<Chapter> {
  const res = await fetch(`${API_BASE}/admin/hierarchy/works/${workId}/chapters`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create chapter: ${res.status}`);
  return res.json();
}

// Moderation Queue
export async function getModerationQueue(status?: string, limit = 50, offset = 0): Promise<ModerationSubmission[]> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (status) params.append("status", status);
  
  const res = await fetch(`${API_BASE}/moderation/submissions?${params}`, {
    headers: getAuthHeader(),
  });
  if (!res.ok) throw new Error(`Failed to fetch moderation queue: ${res.status}`);
  return res.json();
}

export async function approveSubmission(submissionId: number, note?: string, guideline_version?: string): Promise<void> {
  const body = { note, guideline_version };
  const res = await fetch(`${API_BASE}/moderation/submissions/${submissionId}/approve`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Failed to approve submission: ${res.status}`);
}

export async function rejectSubmission(submissionId: number, reason: string): Promise<void> {
  const res = await fetch(`${API_BASE}/moderation/submissions/${submissionId}/reject`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify({ note: reason }),
  });
  if (!res.ok) throw new Error(`Failed to reject submission: ${res.status}`);
}

// Auth Check
export async function getCurrentUser(): Promise<{ id: number; username: string; email: string; role: string } | null> {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export function hasMinRole(userRole: string, requiredRole: string): boolean {
  const roleRanks: Record<string, number> = {
    guest: 0,
    registered: 1,
    moderator: 2,
    senior_moderator: 3,
    admin: 4,
  };
  return (roleRanks[userRole] || 0) >= (roleRanks[requiredRole] || 999);
}
