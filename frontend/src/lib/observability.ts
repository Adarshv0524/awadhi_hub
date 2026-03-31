import { api } from "./api";

export type AdminSloSummary = {
  window_minutes: number;
  total_events: number;
  success_events: number;
  failed_events: number;
  error_rate: number;
  action_success_rate: number;
  latency_ms: {
    p50: number;
    p95: number;
    max: number;
  };
  top_failure_classes: Array<{ failure_class: string; count: number }>;
  generated_at: string;
};

export async function fetchAdminSloSummary(windowMinutes = 60): Promise<AdminSloSummary> {
  return api<AdminSloSummary>(`/telemetry/admin-observability/slo?window_minutes=${windowMinutes}`);
}
