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
  const path = `/analytics/top?${qs.toString()}`;
  return api(path);
}

export async function fetchGrowth(params: { start_date?: string; end_date?: string } = {}) {
  const qs = new URLSearchParams();
  if (params.start_date) qs.set("start_date", params.start_date);
  if (params.end_date) qs.set("end_date", params.end_date);
  const path = `/analytics/growth${qs.toString() ? `?${qs.toString()}` : ""}`;
  return api(path);
}

export async function fetchDemand() {
  return api("/analytics/demand");
}
