// src/lib/admin.ts
// Centralized admin API wrapper
import { z } from "zod";

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

async function requestJson<T>(
  path: string,
  init: RequestInit = {},
  apiBaseOverride?: string,
): Promise<T> {
  const base = resolveApiBase(apiBaseOverride);
  if (!base) {
    throw new Error("Admin API base URL is not configured. Set PUBLIC_API_BASE.");
  }

  try {
    const res = await fetchWithLocalFallback(`${base}${path}`, init);
    if (!res.ok) {
      throw new Error(`Request failed (${res.status}) for ${path}`);
    }
    return (await res.json()) as T;
  } catch (e: any) {
    if (e?.message === "Failed to fetch") {
      const fallback = localFallbackBase(base);
      const tried = fallback ? `${base} and ${fallback}` : base;
      throw new Error(`Failed to connect to backend at ${tried}. Check backend server and CORS settings.`);
    }
    throw e;
  }
}

async function requestNoContent(path: string, init: RequestInit = {}, apiBaseOverride?: string): Promise<void> {
  const base = resolveApiBase(apiBaseOverride);
  if (!base) {
    throw new Error("Admin API base URL is not configured. Set PUBLIC_API_BASE.");
  }

  try {
    const res = await fetchWithLocalFallback(`${base}${path}`, init);
    if (!res.ok) {
      throw new Error(`Request failed (${res.status}) for ${path}`);
    }
  } catch (e: any) {
    if (e?.message === "Failed to fetch") {
      const fallback = localFallbackBase(base);
      const tried = fallback ? `${base} and ${fallback}` : base;
      throw new Error(`Failed to connect to backend at ${tried}. Check backend server and CORS settings.`);
    }
    throw e;
  }
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
  actor_user_id: number | null;
  action: string;
  resource_type: string | null;
  resource_id: number | null;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
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
  number: number;
}

export interface PaginatedResponse<T> {
  total: number;
  results: T[];
}

const adminUserSchema = z.object({
  id: z.number(),
  username: z.string().nullable(),
  email: z.string(),
  role: z.string(),
  permissions: z.number(),
  permission_scopes: z.record(z.unknown()).nullable().optional(),
  created_at: z.string(),
  is_active: z.boolean(),
  is_banned: z.boolean().optional(),
});

const auditLogSchema = z.object({
  id: z.number(),
  actor_user_id: z.number().nullable(),
  action: z.string(),
  resource_type: z.string().nullable(),
  resource_id: z.number().nullable(),
  before: z.record(z.unknown()).nullable(),
  after: z.record(z.unknown()).nullable(),
  metadata: z.record(z.unknown()).nullable(),
  created_at: z.string(),
});

const paginatedAuditLogsSchema = z.object({
  total: z.number(),
  results: z.array(auditLogSchema),
});

const chapterSchema = z.object({
  id: z.number(),
  slug: z.string(),
  title: z.string(),
  work_id: z.number(),
  number: z.number(),
});

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

export interface ModerationTriageRecommendation {
  submission_id: number;
  content_type: string;
  confidence: number;
  rationale_snippets: string[];
  recommendation: string;
  recommendation_id: string;
  explainability: Record<string, unknown>;
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
    const payload = await res.json();
    return z.array(adminUserSchema).parse(payload) as AdminUser[];
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
  await updateUser(userId, { role });
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
  await adminUserSchema.parseAsync(await res.json());
}

export async function deactivateUser(userId: number): Promise<void> {
  // Deactivation is represented by the canonical PATCH /admin/users/{id} contract.
  await updateUser(userId, { is_active: false });
}

// Audit Logs
export async function getAuditLogs(limit = 50, offset = 0): Promise<PaginatedResponse<AuditLog>> {
  const payload = await requestJson<unknown>(`/admin/audit_logs?limit=${limit}&offset=${offset}`, {
    headers: getAuthHeader(),
  });
  return paginatedAuditLogsSchema.parse(payload) as PaginatedResponse<AuditLog>;
}

export async function getAuditLogById(id: number): Promise<AuditLog> {
  const payload = await requestJson<unknown>(`/admin/audit_logs/${id}`, {
    headers: getAuthHeader(),
  });
  return auditLogSchema.parse(payload) as AuditLog;
}

// System Settings
export async function getSettings(): Promise<Setting[]> {
  return requestJson<Setting[]>(`/admin/system_settings`, {
    headers: getAuthHeader(),
  });
}

export async function updateSetting(key: string, value: any): Promise<void> {
  await requestNoContent(`/admin/system_settings/${key}`, {
    method: "PUT",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
}

export async function deleteSetting(key: string): Promise<void> {
  await requestNoContent(`/admin/system_settings/${key}`, {
    method: "DELETE",
    headers: getAuthHeader(),
  });
}

// Hierarchy Management
export async function getAuthors(limit = 100): Promise<Author[]> {
  return requestJson<Author[]>(`/authors?limit=${limit}`, {
    headers: getAuthHeader(),
  });
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
  return requestJson<Work[]>(`/authors/${authorSlug}/works?limit=${limit}`, {
    headers: getAuthHeader(),
  });
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
  const payload = await requestJson<unknown>(`/authors/${authorSlug}/works/${workSlug}/chapters?limit=${limit}`, {
    headers: getAuthHeader(),
  });
  return z.array(chapterSchema).parse(payload) as Chapter[];
}

export async function createChapter(workId: number, data: { slug: string; title: string; number: number }): Promise<Chapter> {
  const res = await fetch(`${API_BASE}/admin/hierarchy/works/${workId}/chapters`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create chapter: ${res.status}`);
  const payload = await res.json();
  return chapterSchema.parse(payload) as Chapter;
}

// Moderation Queue
export async function getModerationQueue(status?: string, limit = 50, offset = 0): Promise<ModerationSubmission[]> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (status) params.append("status", status);

  return requestJson<ModerationSubmission[]>(`/moderation/submissions?${params}`, {
    headers: getAuthHeader(),
  });
}

export async function getModerationSubmissionDetail(submissionId: number): Promise<any> {
  return requestJson<any>(`/moderation/submissions/${submissionId}`, {
    headers: getAuthHeader(),
  });
}

export async function approveSubmission(submissionId: number, note?: string, guideline_version?: string): Promise<void> {
  const body = {
    note,
    guideline_version,
    approved_by_human: true,
  };
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
    body: JSON.stringify({ note: reason, approved_by_human: true }),
  });
  if (!res.ok) throw new Error(`Failed to reject submission: ${res.status}`);
}

export async function approveSubmissionWithModelDecision(
  submissionId: number,
  payload: {
    note?: string;
    guideline_version?: string;
    approved_by_human: boolean;
    model_recommendation_id?: string;
    model_confidence?: number;
    model_rationale_snippets?: string[];
  },
): Promise<void> {
  const res = await fetch(`${API_BASE}/moderation/submissions/${submissionId}/approve`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to approve submission: ${res.status}`);
}

export async function rejectSubmissionWithModelDecision(
  submissionId: number,
  payload: {
    note: string;
    approved_by_human: boolean;
    model_recommendation_id?: string;
    model_confidence?: number;
    model_rationale_snippets?: string[];
  },
): Promise<void> {
  const res = await fetch(`${API_BASE}/moderation/submissions/${submissionId}/reject`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to reject submission: ${res.status}`);
}

export async function getModerationTriage(limit = 50): Promise<ModerationTriageRecommendation[]> {
  return requestJson<ModerationTriageRecommendation[]>(`/api/v1/ai/moderation-triage?limit=${limit}`, {
    headers: getAuthHeader(),
  });
}

export async function logModelDecision(payload: {
  recommendation_id: string;
  use_case: string;
  human_decision: string;
  rationale: string;
  reversible: boolean;
  approved_by_human: boolean;
  explainability_payload?: Record<string, unknown>;
}): Promise<void> {
  await requestNoContent(`/api/v1/ai/model-decision`, {
    method: "POST",
    headers: { ...getAuthHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// Auth Check
export async function getCurrentUser(): Promise<{ id: number; username: string; email: string; role: string } | null> {
  try {
    return await requestJson<{ id: number; username: string; email: string; role: string }>(`/auth/me`, {
      headers: getAuthHeader(),
    });
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
