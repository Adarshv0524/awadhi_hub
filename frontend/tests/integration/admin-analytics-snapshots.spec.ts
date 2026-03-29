import { expect, test } from "@playwright/test";

function setupAdminSession(page: import("@playwright/test").Page): Promise<void> {
  return page.addInitScript(() => {
    window.localStorage.setItem("awadhi_access_token", "test-admin-token");
  });
}

test.beforeEach(async ({ page }) => {
  await setupAdminSession(page);

  await page.route("**/api/v1/telemetry/auth-policy", async (route) => {
    await route.fulfill({ status: 202, body: "" });
  });

  await page.route("**/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ id: 1, username: "admin", email: "admin@example.com", role: "admin" }),
    });
  });

  await page.route("**/auth/refresh", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ access_token: "test-admin-token" }),
    });
  });
});

test("admin analytics key chart states snapshots", async ({ page }) => {
  await page.route("**/admin/analytics/v2/summary**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ today_approved: 7, pending_review: 3, total_approved: 240 }),
    });
  });

  await page.route("**/admin/analytics/v2/top**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { content_type: "doha", content_id: 1, title_or_text: "A", score: 10, views: 100, likes: 40, search_hits: 18 },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/growth**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        dates: ["2026-01-01", "2026-01-02", "2026-01-03"],
        series: { doha: [2, 3, 4], users: [1, 2, 2] },
      }),
    });
  });

  await page.route("**/admin/analytics/v2/demand**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ doha: { count: 20, percent: 66.7 }, idiom: { count: 10, percent: 33.3 } }),
    });
  });

  await page.route("**/admin/analytics/v2/action-throughput**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { module: "users", action: "view", events: 10, avg_latency_ms: 15.2 },
        { module: "moderation", action: "approve", events: 6, avg_latency_ms: 120.3 },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/moderation-cycle-time**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        start: "2026-01-01T00:00:00Z",
        end: "2026-01-31T23:59:59Z",
        count: 12,
        p50_ms: 72,
        p90_ms: 130,
        p95_ms: 182,
        p99_ms: 220,
        max_ms: 250,
      }),
    });
  });

  await page.route("**/admin/analytics/v2/rbac-denials**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { actor_role: "moderator", path: "/admin/users", denials: 8 },
        { actor_role: "registered", path: "/admin/settings", denials: 4 },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/events**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          event_id: "evt-10",
          event_ts_utc: "2026-01-03T10:00:00Z",
          actor_user_id: 1,
          actor_role: "admin",
          session_id: "sess-a",
          request_id: "req-a",
          module: "moderation",
          action: "approve",
          resource_type: "/moderation/submissions",
          resource_id: "44",
          result: "success",
          error_code: null,
          latency_ms: 88,
          client_meta: { method: "POST" },
        },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/3d/actor-resource-graph**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        nodes: [
          { id: "actor:1", category: "actor", label: "1", weight: 4 },
          { id: "resource:/admin/settings:1", category: "resource", label: "/admin/settings:1", weight: 2 },
        ],
        links: [{ source: "actor:1", target: "resource:/admin/settings:1", value: 2, last_seen: "2026-01-01T00:00:00Z" }],
      }),
    });
  });

  await page.route("**/admin/analytics/v2/3d/latency-error-surface**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { endpoint: "/admin/settings", bucket_ts: "2026-01-01T00:00:00Z", latency_ms: 40, error_rate: 3, density: 10 },
      ]),
    });
  });

  await page.route("**/admin/system_settings/rate_limits", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ key: "rate_limits", value: { login_per_hour: 20 } }) });
  });
  await page.route("**/health", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) });
  });
  await page.route("**/authors**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{ id: 1, slug: "kabir", name: "Kabir" }]) });
  });
  await page.route("**/admin/users**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{ id: 1, email: "admin@example.com", role: "admin" }]) });
  });
  await page.route("**/admin/system_settings", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{ key: "rate_limits", value: { login_per_hour: 20 } }]) });
  });
  await page.route("**/admin/audit_logs**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ total: 0, results: [] }) });
  });

  await page.goto("/admin/analytics", { waitUntil: "domcontentloaded" });
  const dashboard = page.getByTestId("operational-dashboard");
  await expect(dashboard).toBeVisible();
  await expect(dashboard.getByText("Linked Event Trail")).toBeVisible();

  await page.setViewportSize({ width: 1440, height: 1100 });
  await expect(dashboard).toHaveScreenshot("admin-analytics-operational-default.png", {
    animations: "disabled",
    caret: "hide",
    timeout: 15000,
  });

  await page.getByRole("button", { name: /Table View/i }).first().click();
  await expect(dashboard).toHaveScreenshot("admin-analytics-operational-table.png", {
    animations: "disabled",
    caret: "hide",
    timeout: 15000,
  });
});
