import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("awadhi_access_token", "smoke-admin-token");
  });

  await page.route("**/api/v1/telemetry/auth-policy", async (route) => {
    await route.fulfill({ status: 202, body: "" });
  });

  await page.route("http://localhost:8000/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ id: 1, username: "admin", email: "admin@example.com", role: "admin" }),
    });
  });

  await page.route("http://localhost:8000/auth/refresh", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ access_token: "smoke-admin-token" }),
    });
  });

  await page.route("http://localhost:8000/admin/users**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });
  await page.route("http://localhost:8000/admin/system_settings**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });
  await page.route("http://localhost:8000/admin/audit_logs**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ total: 0, results: [] }) });
  });
  await page.route("http://localhost:8000/authors**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });
  await page.route("http://localhost:8000/admin/analytics/v2/summary**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ today_approved: 0, pending_review: 0, total_approved: 0 }),
    });
  });
  await page.route("http://localhost:8000/admin/analytics/v2/top**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });
  await page.route("http://localhost:8000/admin/analytics/v2/growth**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ dates: [], series: {} }) });
  });
  await page.route("http://localhost:8000/admin/analytics/v2/demand**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
  });
  await page.route("http://localhost:8000/health", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) });
  });

  await page.route("http://localhost:8000/api/v1/telemetry/admin-observability/slo**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        window_minutes: 60,
        total_events: 0,
        success_events: 0,
        failed_events: 0,
        error_rate: 0,
        action_success_rate: 100,
        latency_ms: { p50: 0, p95: 0, max: 0 },
        top_failure_classes: [],
        generated_at: new Date().toISOString(),
      }),
    });
  });
});

test("admin smoke modules load", async ({ page }) => {
  await page.goto("/admin", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Admin Console" })).toBeVisible();

  await page.goto("/admin/users", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Users" })).toBeVisible();

  await page.goto("/admin/settings", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "System Settings" })).toBeVisible();

  await page.goto("/admin/audit", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Audit Logs" })).toBeVisible();

  await page.goto("/admin/hierarchy", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Content Hierarchy" })).toBeVisible();

  await page.goto("/admin/analytics", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Analytics Dashboard" })).toBeVisible();
});
