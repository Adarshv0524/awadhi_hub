// src/lib/analytics.ts
import { api } from "./api";

export type TopContentParams = {
  content_type?: string;
  limit?: number;
  start_date?: string;
  end_date?: string;
};

export async function fetchTopContent(params: TopContentParams = {}) {
  const qs = new URLSearchParams();
  if (params.content_type) qs.set("content_type", params.content_type);
  if (params.limit) qs.set("limit", String(params.limit));
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  const path = `/admin/analytics/v2/top?${qs.toString()}`;
  return api(path);
}

export async function fetchAdminContentPerformance(params: TopContentParams = {}) {
  const qs = new URLSearchParams();
  if (params.content_type) qs.set("content_type", params.content_type);
  qs.set("limit", String(params.limit ?? 20));
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  return api(`/admin/analytics/v2/top?${qs.toString()}`);
}

export async function fetchGrowth(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  const query = qs.toString();
  const path = `/admin/analytics/v2/growth${query ? `?${query}` : ""}`;
  return api(path);
}

export async function fetchAdminContributorTrends(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  const path = `/admin/analytics/v2/growth${qs.toString() ? `?${qs.toString()}` : ""}`;
  return api(path);
}

export async function fetchDemand() {
  return api("/admin/analytics/v2/demand");
}

export async function fetchSummary() {
  return api("/admin/analytics/v2/summary");
}

export async function fetchAdminSummary() {
  return api("/admin/analytics/v2/summary");
}

export async function fetchActionThroughput(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  return api(`/admin/analytics/v2/action-throughput${qs.toString() ? `?${qs.toString()}` : ""}`);
}

export async function fetchModerationCycleTime(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  return api(`/admin/analytics/v2/moderation-cycle-time${qs.toString() ? `?${qs.toString()}` : ""}`);
}

export async function fetchRbacDenials(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  return api(`/admin/analytics/v2/rbac-denials${qs.toString() ? `?${qs.toString()}` : ""}`);
}

export async function fetchAdminEvents(params: {
  start_date?: string;
  end_date?: string;
  module?: string;
  action?: string;
  result?: string;
  limit?: number;
} = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  if (params.module) qs.set("module", params.module);
  if (params.action) qs.set("action", params.action);
  if (params.result) qs.set("result", params.result);
  qs.set("limit", String(params.limit ?? 250));
  return api(`/admin/analytics/v2/events?${qs.toString()}`);
}

export async function fetchActorResourceGraph3D(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  return api(`/admin/analytics/v2/3d/actor-resource-graph${qs.toString() ? `?${qs.toString()}` : ""}`);
}

export async function fetchLatencySurface3D(params: { start_date?: string; end_date?: string; bucket_minutes?: number } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  qs.set("bucket_minutes", String(params.bucket_minutes ?? 30));
  return api(`/admin/analytics/v2/3d/latency-error-surface?${qs.toString()}`);
}

export async function scoreSettingsRisk(setting_key: string, old_value: unknown, new_value: unknown) {
  return api("/api/v1/ai/settings-risk-score", {
    method: "POST",
    body: { setting_key, old_value, new_value },
  });
}
