<script lang="ts">
  import { onMount } from "svelte";
  import * as echarts from "echarts";
  import {
    fetchActionThroughput,
    fetchAdminEvents,
    fetchModerationCycleTime,
    fetchRbacDenials,
  } from "../../lib/analytics";

  type EventRow = {
    event_id: string;
    event_ts_utc: string;
    actor_user_id: number | null;
    actor_role: string;
    module: string;
    action: string;
    resource_type: string | null;
    resource_id: string | null;
    result: string;
    error_code: string | null;
    latency_ms: number | null;
  };

  let loading = false;
  let error: string | null = null;
  let startDate = "";
  let endDate = "";

  let throughput: Array<{ module: string; action: string; events: number; avg_latency_ms: number }> = [];
  let rbacDenials: Array<{ actor_role: string; path: string; denials: number }> = [];
  let moderationLatency = { p50_ms: 0, p90_ms: 0, p95_ms: 0, p99_ms: 0, max_ms: 0, count: 0 };
  let events: EventRow[] = [];
  let selectedDay: string | null = null;
  let selectedModule = "";
  let activeWindowLabel = "Last 30 days";
  let autoExpandedWindow = false;

  let roleAreaHost: HTMLDivElement;
  let rbacHeatmapHost: HTMLDivElement;
  let moderationControlHost: HTMLDivElement;

  let roleAreaChart: echarts.ECharts | null = null;
  let rbacHeatmapChart: echarts.ECharts | null = null;
  let moderationControlChart: echarts.ECharts | null = null;

  function dayFromISO(ts: string) {
    return (ts || "").slice(0, 10);
  }

  function getParams() {
    return {
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };
  }

  async function load() {
    loading = true;
    error = null;
    selectedDay = null;
    autoExpandedWindow = false;

    try {
      const [throughputRes, denialsRes, cycleRes, eventsRes] = await Promise.all([
        fetchActionThroughput(getParams()),
        fetchRbacDenials(getParams()),
        fetchModerationCycleTime(getParams()),
        fetchAdminEvents({ ...getParams(), module: selectedModule || undefined, limit: 500 }),
      ]);

      throughput = Array.isArray(throughputRes) ? throughputRes : [];
      rbacDenials = Array.isArray(denialsRes) ? denialsRes : [];
      moderationLatency = cycleRes || moderationLatency;
      events = Array.isArray(eventsRes) ? eventsRes : [];

      if (!events.length && !selectedModule) {
        const end = new Date();
        const start = new Date(end);
        start.setUTCDate(end.getUTCDate() - 180);
        const widerParams = {
          start_date: start.toISOString().slice(0, 10),
          end_date: end.toISOString().slice(0, 10),
        };

        const [throughputWide, denialsWide, cycleWide, eventsWide] = await Promise.all([
          fetchActionThroughput(widerParams),
          fetchRbacDenials(widerParams),
          fetchModerationCycleTime(widerParams),
          fetchAdminEvents({ ...widerParams, limit: 800 }),
        ]);

        if (Array.isArray(eventsWide) && eventsWide.length) {
          throughput = Array.isArray(throughputWide) ? throughputWide : throughput;
          rbacDenials = Array.isArray(denialsWide) ? denialsWide : rbacDenials;
          moderationLatency = cycleWide || moderationLatency;
          events = eventsWide;
          autoExpandedWindow = true;
          activeWindowLabel = "Auto-expanded to last 180 days";
        } else {
          activeWindowLabel = "No telemetry events in selected period";
        }
      } else {
        activeWindowLabel = "Selected date range";
      }

      drawCharts();
    } catch (e: any) {
      console.error("[OperationalDashboard] load error", e);
      error = e?.message || "Failed to load operational analytics";
    } finally {
      loading = false;
    }
  }

  function weeklyRoleSeries() {
    const weekRoleCounts = new Map<string, Map<string, number>>();
    for (const row of events) {
      const d = new Date(row.event_ts_utc);
      if (Number.isNaN(d.getTime())) continue;
      const weekStart = new Date(d);
      weekStart.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7));
      const weekKey = weekStart.toISOString().slice(0, 10);
      if (!weekRoleCounts.has(weekKey)) weekRoleCounts.set(weekKey, new Map());
      const roleMap = weekRoleCounts.get(weekKey)!;
      roleMap.set(row.actor_role || "unknown", (roleMap.get(row.actor_role || "unknown") || 0) + 1);
    }

    const weeks = Array.from(weekRoleCounts.keys()).sort();
    const roles = Array.from(new Set(events.map((e) => e.actor_role || "unknown"))).sort();

    return {
      weeks,
      roles,
      series: roles.map((role) => ({
        name: role,
        type: "line",
        stack: "roles",
        areaStyle: {},
        smooth: true,
        data: weeks.map((w) => weekRoleCounts.get(w)?.get(role) || 0),
      })),
    };
  }

  function drawCharts() {
    if (!roleAreaChart && roleAreaHost) roleAreaChart = echarts.init(roleAreaHost);
    if (!rbacHeatmapChart && rbacHeatmapHost) rbacHeatmapChart = echarts.init(rbacHeatmapHost);
    if (!moderationControlChart && moderationControlHost) moderationControlChart = echarts.init(moderationControlHost);

    const roleData = weeklyRoleSeries();
    roleAreaChart?.setOption({
      animation: false,
      backgroundColor: "transparent",
      tooltip: { trigger: "axis" },
      legend: { textStyle: { color: "#cbd5e1" } },
      xAxis: { type: "category", data: roleData.weeks, axisLabel: { color: "#94a3b8" } },
      yAxis: { type: "value", axisLabel: { color: "#94a3b8" } },
      series: roleData.series,
      grid: { left: 36, right: 12, top: 24, bottom: 24 },
    });

    const roles = Array.from(new Set(rbacDenials.map((r) => r.actor_role))).sort();
    const paths = Array.from(new Set(rbacDenials.map((r) => r.path))).sort();
    const heatData = rbacDenials.map((row) => [paths.indexOf(row.path), roles.indexOf(row.actor_role), row.denials]);
    rbacHeatmapChart?.setOption({
      animation: false,
      tooltip: { position: "top" },
      xAxis: { type: "category", data: paths, axisLabel: { color: "#94a3b8", rotate: 30 } },
      yAxis: { type: "category", data: roles, axisLabel: { color: "#94a3b8" } },
      visualMap: {
        min: 0,
        max: Math.max(1, ...rbacDenials.map((r) => r.denials)),
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 0,
        inRange: { color: ["#0f172a", "#f59e0b", "#ef4444"] },
        textStyle: { color: "#cbd5e1" },
      },
      series: [{ type: "heatmap", data: heatData, label: { show: true, color: "#e2e8f0" } }],
      grid: { left: 72, right: 18, top: 16, bottom: 60 },
    });

    const moderationEvents = events.filter((e) => e.module === "moderation");
    const dayMap = new Map<string, { submitted: number; pending: number; approved: number; rejected: number; avgLatency: number; n: number }>();
    for (const e of moderationEvents) {
      const day = dayFromISO(e.event_ts_utc);
      if (!dayMap.has(day)) dayMap.set(day, { submitted: 0, pending: 0, approved: 0, rejected: 0, avgLatency: 0, n: 0 });
      const v = dayMap.get(day)!;
      v.submitted += 1;
      if (e.action === "view") v.pending += 1;
      if (e.action === "approve") v.approved += 1;
      if (e.action === "reject") v.rejected += 1;
      if (typeof e.latency_ms === "number") {
        v.avgLatency += e.latency_ms;
        v.n += 1;
      }
    }

    const days = Array.from(dayMap.keys()).sort();
    const avgLatency = days.map((d) => {
      const v = dayMap.get(d)!;
      return v.n ? Number((v.avgLatency / v.n).toFixed(2)) : 0;
    });

    moderationControlChart?.off("click");
    moderationControlChart?.setOption({
      animation: false,
      tooltip: { trigger: "axis" },
      legend: { textStyle: { color: "#cbd5e1" } },
      xAxis: { type: "category", data: days, axisLabel: { color: "#94a3b8" } },
      yAxis: [{ type: "value", axisLabel: { color: "#94a3b8" } }, { type: "value", axisLabel: { color: "#94a3b8" } }],
      series: [
        { name: "Submitted", type: "bar", data: days.map((d) => dayMap.get(d)?.submitted || 0) },
        { name: "Pending", type: "bar", data: days.map((d) => dayMap.get(d)?.pending || 0) },
        { name: "Approved", type: "bar", data: days.map((d) => dayMap.get(d)?.approved || 0) },
        { name: "Rejected", type: "bar", data: days.map((d) => dayMap.get(d)?.rejected || 0) },
        { name: "Latency", type: "line", yAxisIndex: 1, data: avgLatency, smooth: true },
      ],
      grid: { left: 40, right: 36, top: 20, bottom: 24 },
    });

    moderationControlChart?.on("click", (params: any) => {
      if (params?.name) selectedDay = String(params.name);
    });
  }

  function filteredEvents() {
    let out = events;
    if (selectedModule) out = out.filter((e) => e.module === selectedModule);
    if (selectedDay) out = out.filter((e) => dayFromISO(e.event_ts_utc) === selectedDay);
    return out;
  }

  function hasOperationalData() {
    return events.length > 0 || throughput.length > 0 || rbacDenials.length > 0;
  }

  onMount(() => {
    const now = new Date();
    const start = new Date(now);
    start.setUTCDate(now.getUTCDate() - 30);
    startDate = start.toISOString().slice(0, 10);
    endDate = now.toISOString().slice(0, 10);
    load();

    const onResize = () => {
      roleAreaChart?.resize();
      rbacHeatmapChart?.resize();
      moderationControlChart?.resize();
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      roleAreaChart?.dispose();
      rbacHeatmapChart?.dispose();
      moderationControlChart?.dispose();
    };
  });
</script>

<section class="admin-panel p-6" data-testid="operational-dashboard">
  <div class="flex flex-col lg:flex-row lg:items-end gap-3 mb-5">
    <div class="flex gap-2">
      <input type="date" bind:value={startDate} class="admin-input" aria-label="Start date" />
      <input type="date" bind:value={endDate} class="admin-input" aria-label="End date" />
    </div>
    <select bind:value={selectedModule} class="admin-input" aria-label="Module filter">
      <option value="">All modules</option>
      <option value="users">users</option>
      <option value="settings">settings</option>
      <option value="hierarchy">hierarchy</option>
      <option value="audit">audit</option>
      <option value="moderation">moderation</option>
      <option value="analytics">analytics</option>
    </select>
    <button class="admin-btn admin-btn-primary" title={activeWindowLabel} on:click={load}>Refresh</button>
  </div>

  {#if loading}
    <p class="text-slate-300">Loading operational dashboard...</p>
  {:else if error}
    <p class="text-rose-300">{error}</p>
  {:else if !hasOperationalData()}
    <div class="rounded-lg border border-slate-700 bg-slate-900/55 p-4 text-sm text-slate-300">
      <p class="font-semibold text-slate-100">Operational telemetry is currently sparse.</p>
      <p class="mt-1">No event trail was found for the selected filters. Try widening date range, clearing module filter, or generating baseline traffic in admin routes.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
      <div class="admin-kpi"><div class="admin-kpi-label">Moderation p95</div><div class="admin-kpi-value">{moderationLatency.p95_ms.toFixed(2)} ms</div></div>
      <div class="admin-kpi"><div class="admin-kpi-label">Moderation p99</div><div class="admin-kpi-value">{moderationLatency.p99_ms.toFixed(2)} ms</div></div>
      <div class="admin-kpi"><div class="admin-kpi-label">Cycle samples</div><div class="admin-kpi-value">{moderationLatency.count}</div></div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <div class="admin-panel p-4">
        <h3 class="text-slate-200 font-semibold mb-2">Users Role Distribution by Week</h3>
        <div bind:this={roleAreaHost} style="height:320px"></div>
      </div>
      <div class="admin-panel p-4">
        <h3 class="text-slate-200 font-semibold mb-2">RBAC Denials Heatmap (endpoint vs role)</h3>
        <div bind:this={rbacHeatmapHost} style="height:320px"></div>
      </div>
    </div>

    <div class="admin-panel p-4 mt-4">
      <h3 class="text-slate-200 font-semibold mb-2">Moderation Funnel + Latency Control</h3>
      <p class="text-xs text-slate-400 mb-3">Click any day bar/point to brush linked event details.</p>
      <div bind:this={moderationControlHost} style="height:320px"></div>
    </div>

    <div class="admin-panel p-4 mt-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-slate-200 font-semibold">Linked Event Trail</h3>
        {#if selectedDay}
          <button class="admin-btn" on:click={() => (selectedDay = null)}>Clear day filter ({selectedDay})</button>
        {/if}
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-slate-400 border-b border-slate-700">
              <th class="py-2 pr-2">Time</th>
              <th class="py-2 pr-2">Module</th>
              <th class="py-2 pr-2">Action</th>
              <th class="py-2 pr-2">Role</th>
              <th class="py-2 pr-2">Result</th>
              <th class="py-2 pr-2">Error</th>
              <th class="py-2 pr-2">Latency</th>
              <th class="py-2 pr-2">Resource</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredEvents().slice(0, 120) as row}
              <tr class="border-b border-slate-800 text-slate-200">
                <td class="py-2 pr-2">{row.event_ts_utc?.replace("T", " ").slice(0, 19)}</td>
                <td class="py-2 pr-2">{row.module}</td>
                <td class="py-2 pr-2">{row.action}</td>
                <td class="py-2 pr-2">{row.actor_role}</td>
                <td class="py-2 pr-2">{row.result}</td>
                <td class="py-2 pr-2">{row.error_code || "-"}</td>
                <td class="py-2 pr-2">{row.latency_ms ?? "-"}</td>
                <td class="py-2 pr-2">{row.resource_type || "-"}:{row.resource_id || "-"}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</section>

<style>
  .admin-input {
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    padding: 0.5rem 0.65rem;
  }
</style>
