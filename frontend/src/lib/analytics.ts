// src/lib/analytics.ts
import { api } from "./api";

export type TopContentParams = {
  content_type?: string;
  limit?: number;
  start_date?: string;
  end_date?: string;
};

type InsightsParams = {
  view: string;
  start_date?: string;
  end_date?: string;
  content_type?: string;
  module?: string;
  action?: string;
  result?: string;
  limit?: number;
  bucket_minutes?: number;
};

async function fetchInsights(params: InsightsParams) {
  const qs = new URLSearchParams();
  qs.set("view", params.view);
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  if (params.content_type) qs.set("content_type", params.content_type);
  if (params.module) qs.set("module", params.module);
  if (params.action) qs.set("action", params.action);
  if (params.result) qs.set("result", params.result);
  if (typeof params.limit === "number") qs.set("limit", String(params.limit));
  if (typeof params.bucket_minutes === "number") qs.set("bucket_minutes", String(params.bucket_minutes));
  const payload = await api(`/api/v1/admin/analytics/insights?${qs.toString()}`);
  return payload?.data;
}

export async function fetchTopContent(params: TopContentParams = {}) {
  return fetchInsights({
    view: "top",
    content_type: params.content_type,
    limit: params.limit,
    start_date: params.start_date,
    end_date: params.end_date,
  });
}

export async function fetchAdminContentPerformance(params: TopContentParams = {}) {
  return fetchInsights({
    view: "top",
    content_type: params.content_type,
    limit: params.limit ?? 20,
    start_date: params.start_date,
    end_date: params.end_date,
  });
}

export async function fetchGrowth(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "growth", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchAdminContributorTrends(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "growth", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchDemand() {
  return fetchInsights({ view: "demand" });
}

export async function fetchAdminEngagementSummary(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "engagement-summary", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchSummary() {
  return api("/api/v1/analytics/summary");
}

export async function fetchAdminSummary() {
  return api("/api/v1/admin/analytics/summary");
}

export async function fetchActionThroughput(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "action-throughput", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchModerationCycleTime(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "moderation-cycle-time", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchRbacDenials(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "rbac-denials", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchAdminEvents(params: {
  start_date?: string;
  end_date?: string;
  module?: string;
  action?: string;
  result?: string;
  limit?: number;
} = {}) {
  return fetchInsights({
    view: "events",
    start_date: params.start_date,
    end_date: params.end_date,
    module: params.module,
    action: params.action,
    result: params.result,
    limit: params.limit ?? 250,
  });
}

export async function fetchActorResourceGraph3D(params: { start_date?: string; end_date?: string } = {}) {
  return fetchInsights({ view: "actor-resource-graph", start_date: params.start_date, end_date: params.end_date });
}

export async function fetchLatencySurface3D(params: { start_date?: string; end_date?: string; bucket_minutes?: number } = {}) {
  return fetchInsights({
    view: "latency-error-surface",
    start_date: params.start_date,
    end_date: params.end_date,
    bucket_minutes: params.bucket_minutes ?? 30,
  });
}

export async function scoreSettingsRisk(setting_key: string, old_value: unknown, new_value: unknown) {
  return api("/ai/settings-risk-score", {
    method: "POST",
    body: { setting_key, old_value, new_value },
  });
}
