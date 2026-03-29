#!/usr/bin/env node

/**
 * Lightweight health monitor for Awadhi backend.
 *
 * Usage:
 *   HEALTH_URL=http://localhost:8000/health HEALTH_INTERVAL_MS=60000 node backend/scripts/health_monitor.mjs
 */

const healthUrl = process.env.HEALTH_URL || "http://localhost:8000/health";
const intervalMs = Number(process.env.HEALTH_INTERVAL_MS || 60000);
const timeoutMs = Number(process.env.HEALTH_TIMEOUT_MS || 5000);

if (!Number.isFinite(intervalMs) || intervalMs < 1000) {
  console.error("[health-monitor] HEALTH_INTERVAL_MS must be >= 1000");
  process.exit(1);
}

function nowIso() {
  return new Date().toISOString();
}

async function checkHealth() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(healthUrl, {
      method: "GET",
      signal: controller.signal,
      headers: {
        "Accept": "application/json",
      },
    });

    const bodyText = await response.text().catch(() => "");
    const ok = response.ok;

    if (ok) {
      console.log(`${nowIso()} [health-monitor] OK ${response.status} ${healthUrl}`);
      return;
    }

    console.error(`${nowIso()} [health-monitor] FAIL ${response.status} ${healthUrl} body=${bodyText.slice(0, 200)}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`${nowIso()} [health-monitor] ERROR ${healthUrl} ${message}`);
  } finally {
    clearTimeout(timeout);
  }
}

console.log(`${nowIso()} [health-monitor] starting interval=${intervalMs}ms url=${healthUrl}`);
void checkHealth();
setInterval(() => {
  void checkHealth();
}, intervalMs);
