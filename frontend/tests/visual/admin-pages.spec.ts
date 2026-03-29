import { test, expect } from "@playwright/test";

const adminPages = [
  { path: "/admin", name: "admin-dashboard" },
  { path: "/admin/users", name: "admin-users" },
  { path: "/admin/hierarchy", name: "admin-hierarchy" },
  { path: "/admin/settings", name: "admin-settings" },
  { path: "/admin/audit", name: "admin-audit" },
  { path: "/admin/analytics", name: "admin-analytics" },
];

for (const pageCase of adminPages) {
  test(`visual snapshot ${pageCase.name}`, async ({ page }) => {
    await page.goto(pageCase.path, { waitUntil: "domcontentloaded" });
    await page.setViewportSize({ width: 1440, height: 900 });
    await expect(page).toHaveScreenshot(`${pageCase.name}.png`, {
      fullPage: true,
      animations: "disabled",
      caret: "hide",
    });
  });
}
