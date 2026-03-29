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

test("users page loads data and performs role update", async ({ page }) => {
  let patchBody: Record<string, unknown> | null = null;

  await page.route(/https?:\/\/(localhost|127\.0\.0\.1):8000\/admin\/users(\?.*)?$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 1,
          username: "user_one",
          email: "user1@example.com",
          role: "registered",
          permissions: 0,
          permission_scopes: {},
          created_at: "2026-01-01T00:00:00Z",
          is_active: true,
          is_banned: false,
        },
      ]),
    });
  });

  await page.route(/https?:\/\/(localhost|127\.0\.0\.1):8000\/admin\/users\/1$/, async (route) => {
    patchBody = route.request().postDataJSON() as Record<string, unknown>;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        username: "user_one",
        email: "user1@example.com",
        role: patchBody?.role ?? "moderator",
        permissions: 0,
        permission_scopes: {},
        created_at: "2026-01-01T00:00:00Z",
        is_active: true,
        is_banned: false,
      }),
    });
  });

  await page.goto("/admin/users", { waitUntil: "domcontentloaded" });

  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Users" })).toBeVisible();
  await expect(page.getByText("user1@example.com")).toBeVisible();

  await page.locator("#role-1").selectOption("moderator");
  await expect.poll(() => patchBody?.role as string | undefined).toBe("moderator");
});

test("audit page loads and shows log detail dialog", async ({ page }) => {
  await page.route("**/admin/audit_logs**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        total: 1,
        results: [
          {
            id: 1,
            actor_user_id: 1,
            action: "setting:update",
            resource_type: "system_setting",
            resource_id: 7,
            before: { value: "old" },
            after: { value: "new" },
            metadata: { source: "test" },
            created_at: "2026-01-01T10:00:00Z",
          },
        ],
      }),
    });
  });

  await page.route("**/admin/audit_logs/1", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        actor_user_id: 1,
        action: "setting:update",
        resource_type: "system_setting",
        resource_id: 7,
        before: { value: "old" },
        after: { value: "new" },
        metadata: { source: "test" },
        created_at: "2026-01-01T10:00:00Z",
      }),
    });
  });

  await page.goto("/admin/audit", { waitUntil: "domcontentloaded" });

  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Audit Logs" })).toBeVisible();
  await expect(page.getByText("setting:update")).toBeVisible();

  await page.getByRole("button", { name: "View Details" }).click();
  await expect(page.getByRole("heading", { name: "Audit Details" })).toBeVisible();
  await expect(page.getByText("setting:update").nth(1)).toBeVisible();
});

test("settings page loads and submits setting update", async ({ page }) => {
  let updateValue: unknown = null;

  await page.route("**/admin/system_settings", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([{ key: "site_name", value: "Awadhi New" }]),
    });
  });

  await page.route("**/admin/system_settings/site_name", async (route) => {
    updateValue = (route.request().postDataJSON() as { value: unknown }).value;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ key: "site_name", value: updateValue }),
    });
  });

  await page.goto("/admin/settings", { waitUntil: "domcontentloaded" });

  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "System Settings" })).toBeVisible();
  await expect(page.getByText("site_name")).toBeVisible();

  const row = page.locator("tr", { hasText: "site_name" });
  await row.getByRole("button", { name: "Edit" }).click();
  await row.locator("textarea").fill('"Awadhi QA"');
  await row.getByRole("button", { name: "Save" }).click();

  await expect.poll(() => updateValue).toBe("Awadhi QA");
});

test("hierarchy page loads and drills into works and chapters", async ({ page }) => {
  await page.route("**/authors?limit=100", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: 11, slug: "kabir", name: "Kabir", language: "aw", short_bio: "Poet" },
      ]),
    });
  });

  await page.route("**/authors/kabir/works?limit=50", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: 21, slug: "bijak", title: "Bijak", author_id: 11, description: null },
      ]),
    });
  });

  await page.route("**/authors/kabir/works/bijak/chapters?limit=200", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: 31, slug: "doha-1", title: "Doha One", work_id: 21, number: 1 },
      ]),
    });
  });

  await page.goto("/admin/hierarchy", { waitUntil: "domcontentloaded" });

  await expect(page.getByRole("heading", { name: "Content Hierarchy" })).toBeVisible();
  await expect(page.getByText("Kabir (kabir)")).toBeVisible();

  await page.getByRole("button", { name: "View Works" }).click();
  await expect(page.getByText("Works for Kabir")).toBeVisible();

  await page.getByRole("button", { name: "View Chapters" }).click();
  await expect(page.getByText("Ch 1: Doha One (doha-1)")).toBeVisible();
});

test("analytics page renders v2 dashboard data and avoids deprecated endpoints", async ({ page }) => {
  const deprecatedHits: string[] = [];
  let summaryHits = 0;
  let topHits = 0;
  let demandHits = 0;
  let growthHits = 0;
  let throughputHits = 0;
  let cycleHits = 0;
  let denialHits = 0;
  let eventsHits = 0;
  let graph3dHits = 0;
  let surface3dHits = 0;

  await page.route("**/analytics/top**", async (route) => {
    deprecatedHits.push(route.request().url());
    await route.fulfill({ status: 500, body: "deprecated endpoint should not be called" });
  });
  await page.route("**/analytics/growth**", async (route) => {
    deprecatedHits.push(route.request().url());
    await route.fulfill({ status: 500, body: "deprecated endpoint should not be called" });
  });
  await page.route("**/analytics/demand**", async (route) => {
    deprecatedHits.push(route.request().url());
    await route.fulfill({ status: 500, body: "deprecated endpoint should not be called" });
  });
  await page.route("**/admin/analytics/content-performance**", async (route) => {
    deprecatedHits.push(route.request().url());
    await route.fulfill({ status: 500, body: "deprecated endpoint should not be called" });
  });
  await page.route("**/admin/analytics/contributor-trends**", async (route) => {
    deprecatedHits.push(route.request().url());
    await route.fulfill({ status: 500, body: "deprecated endpoint should not be called" });
  });

  await page.route("**/admin/analytics/v2/summary**", async (route) => {
    summaryHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ today_approved: 5, pending_review: 2, total_approved: 100 }),
    });
  });

  await page.route("**/admin/analytics/v2/top**", async (route) => {
    topHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          content_type: "doha",
          content_id: 1,
          title_or_text: "Sample Doha",
          score: 12.4,
          views: 100,
          likes: 11,
          search_hits: 9,
        },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/demand**", async (route) => {
    demandHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        doha: { count: 20, percent: 66.7 },
        idiom: { count: 10, percent: 33.3 },
      }),
    });
  });

  await page.route("**/admin/analytics/v2/growth**", async (route) => {
    growthHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        dates: ["2026-01-01", "2026-01-02"],
        series: { doha: [2, 3], users: [1, 1] },
      }),
    });
  });

  await page.route("**/admin/analytics/v2/action-throughput**", async (route) => {
    throughputHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { module: "users", action: "view", events: 12, avg_latency_ms: 10.5 },
        { module: "moderation", action: "approve", events: 4, avg_latency_ms: 120.5 },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/moderation-cycle-time**", async (route) => {
    cycleHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        start: "2026-01-01T00:00:00Z",
        end: "2026-01-31T23:59:59Z",
        count: 9,
        p50_ms: 80,
        p90_ms: 140,
        p95_ms: 190,
        p99_ms: 210,
        max_ms: 230,
      }),
    });
  });

  await page.route("**/admin/analytics/v2/rbac-denials**", async (route) => {
    denialHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { actor_role: "moderator", path: "/admin/users", denials: 5 },
        { actor_role: "registered", path: "/admin/settings", denials: 3 },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/events**", async (route) => {
    eventsHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          event_id: "evt-1",
          event_ts_utc: "2026-01-02T10:00:00Z",
          actor_user_id: 1,
          actor_role: "admin",
          session_id: "sess-1",
          request_id: "req-1",
          module: "users",
          action: "view",
          resource_type: "/admin/users",
          resource_id: "1",
          result: "success",
          error_code: null,
          latency_ms: 12,
          client_meta: { method: "GET" },
        },
      ]),
    });
  });

  await page.route("**/admin/analytics/v2/3d/actor-resource-graph**", async (route) => {
    graph3dHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        nodes: [
          { id: "actor:1", category: "actor", label: "1", weight: 5 },
          { id: "resource:/admin/users:1", category: "resource", label: "/admin/users:1", weight: 3 },
        ],
        links: [{ source: "actor:1", target: "resource:/admin/users:1", value: 3, last_seen: "2026-01-01T00:00:00Z" }],
      }),
    });
  });

  await page.route("**/admin/analytics/v2/3d/latency-error-surface**", async (route) => {
    surface3dHits += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { endpoint: "/admin/users", bucket_ts: "2026-01-01T00:00:00Z", latency_ms: 12.3, error_rate: 0.0, density: 8 },
      ]),
    });
  });

  await page.route("**/admin/system_settings/rate_limits", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ key: "rate_limits", value: { login_per_hour: 20 } }),
    });
  });

  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" }),
    });
  });

  await page.route("**/authors**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([{ id: 1, slug: "kabir", name: "Kabir" }]),
    });
  });

  await page.route("**/admin/users**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([{ id: 1, email: "admin@example.com", role: "admin" }]),
    });
  });

  await page.route("**/admin/system_settings", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([{ key: "rate_limits", value: { login_per_hour: 20 } }]),
    });
  });

  await page.route("**/admin/audit_logs**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ total: 1, results: [] }),
    });
  });

  await page.goto("/admin/analytics", { waitUntil: "domcontentloaded" });

  await expect(page.locator("#admin-main-content").getByRole("heading", { name: "Analytics Dashboard" })).toBeVisible();
  await expect(page.getByText("Global Platform Summary")).toBeVisible();
  await expect(page.getByTestId("operational-dashboard")).toBeVisible();

  await page.getByRole("button", { name: "Table View" }).click();
  await expect(page.getByText("doha").first()).toBeVisible();

  await expect.poll(() => summaryHits).toBeGreaterThan(0);
  await expect.poll(() => topHits).toBeGreaterThan(0);
  await expect.poll(() => demandHits).toBeGreaterThan(0);
  await expect.poll(() => growthHits).toBeGreaterThan(0);
  await expect.poll(() => throughputHits).toBeGreaterThan(0);
  await expect.poll(() => cycleHits).toBeGreaterThan(0);
  await expect.poll(() => denialHits).toBeGreaterThan(0);
  await expect.poll(() => eventsHits).toBeGreaterThan(0);
  await expect.poll(() => graph3dHits).toBeGreaterThan(0);
  await expect.poll(() => surface3dHits).toBeGreaterThan(0);
  await expect(deprecatedHits).toEqual([]);
});
