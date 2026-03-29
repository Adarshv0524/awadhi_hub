<script lang="ts">
  import { onMount } from "svelte";
  import * as echarts from "echarts";
  import { fetchActorResourceGraph3D, fetchLatencySurface3D, fetchAdminEvents } from "../../lib/analytics";

  let loading = false;
  let error: string | null = null;
  let startDate = "";
  let endDate = "";

  let forceHost: HTMLDivElement;
  let surfaceHost: HTMLDivElement;
  let forceChart: echarts.ECharts | null = null;
  let surfaceChart: echarts.ECharts | null = null;
  let derivedFromEvents = false;

  function params() {
    return { start_date: startDate || undefined, end_date: endDate || undefined };
  }

  function deriveGraphFromEvents(events: any[]) {
    const nodeMap = new Map<string, { id: string; category: string; label: string; weight: number }>();
    const edgeMap = new Map<string, { source: string; target: string; value: number; last_seen: string | null }>();

    for (const evt of events) {
      const actorId = evt?.actor_user_id ?? "unknown";
      const resourceType = evt?.resource_type || evt?.client_meta?.path || "unknown-resource";
      const resourceId = evt?.resource_id || "-";
      const ts = evt?.event_ts_utc || null;

      const actorNodeId = `actor:${actorId}`;
      const resourceNodeId = `resource:${resourceType}:${resourceId}`;

      if (!nodeMap.has(actorNodeId)) {
        nodeMap.set(actorNodeId, { id: actorNodeId, category: "actor", label: String(actorId), weight: 0 });
      }
      if (!nodeMap.has(resourceNodeId)) {
        nodeMap.set(resourceNodeId, {
          id: resourceNodeId,
          category: "resource",
          label: `${resourceType}:${resourceId}`,
          weight: 0,
        });
      }

      nodeMap.get(actorNodeId)!.weight += 1;
      nodeMap.get(resourceNodeId)!.weight += 1;

      const edgeKey = `${actorNodeId}->${resourceNodeId}`;
      if (!edgeMap.has(edgeKey)) {
        edgeMap.set(edgeKey, { source: actorNodeId, target: resourceNodeId, value: 0, last_seen: ts });
      }
      const edge = edgeMap.get(edgeKey)!;
      edge.value += 1;
      edge.last_seen = ts || edge.last_seen;
    }

    return {
      nodes: Array.from(nodeMap.values()),
      links: Array.from(edgeMap.values()),
    };
  }

  function deriveSurfaceFromEvents(events: any[]) {
    const buckets = new Map<string, { endpoint: string; bucket_ts: string; latency_ms_sum: number; samples: number; failures: number }>();
    for (const evt of events) {
      const endpoint = evt?.resource_type || evt?.client_meta?.path || "unknown-endpoint";
      const ts = evt?.event_ts_utc ? new Date(evt.event_ts_utc) : new Date();
      ts.setUTCMinutes(0, 0, 0);
      const bucketTs = ts.toISOString();
      const key = `${endpoint}|${bucketTs}`;
      if (!buckets.has(key)) {
        buckets.set(key, { endpoint, bucket_ts: bucketTs, latency_ms_sum: 0, samples: 0, failures: 0 });
      }
      const bucket = buckets.get(key)!;
      const latency = typeof evt?.latency_ms === "number" ? evt.latency_ms : 0;
      bucket.latency_ms_sum += latency;
      bucket.samples += 1;
      if (evt?.result && String(evt.result).toLowerCase() !== "success") {
        bucket.failures += 1;
      }
    }

    return Array.from(buckets.values()).map((b) => {
      const sampleCount = Math.max(1, b.samples);
      return {
        endpoint: b.endpoint,
        bucket_ts: b.bucket_ts,
        latency_ms: Number((b.latency_ms_sum / sampleCount).toFixed(2)),
        error_rate: Number(((b.failures / sampleCount) * 100).toFixed(2)),
        density: b.samples,
      };
    });
  }

  async function load() {
    loading = true;
    error = null;
    derivedFromEvents = false;
    try {
      let [graph, surface] = await Promise.all([
        fetchActorResourceGraph3D(params()),
        fetchLatencySurface3D({ ...params(), bucket_minutes: 30 }),
      ]);

      const graphEmpty = !Array.isArray(graph?.nodes) || graph.nodes.length === 0;
      const surfaceEmpty = !Array.isArray(surface) || surface.length === 0;

      if (graphEmpty || surfaceEmpty) {
        const events = await fetchAdminEvents({ ...params(), limit: 800 });
        if (Array.isArray(events) && events.length) {
          derivedFromEvents = true;
          if (graphEmpty) graph = deriveGraphFromEvents(events);
          if (surfaceEmpty) surface = deriveSurfaceFromEvents(events);
        }
      }

      if (!forceChart && forceHost) forceChart = echarts.init(forceHost);
      if (!surfaceChart && surfaceHost) surfaceChart = echarts.init(surfaceHost);

      const categories = [
        { name: "actor" },
        { name: "resource" },
      ];

      forceChart?.setOption({
        animation: false,
        tooltip: {},
        legend: [{ data: categories.map((c) => c.name), textStyle: { color: "#cbd5e1" } }],
        series: [
          {
            type: "graphGL",
            layout: "forceAtlas2",
            forceAtlas2: {
              steps: 1,
              stopThreshold: 1,
              jitterTolerence: 10,
              edgeWeightInfluence: 1,
              gravity: 1,
              scaling: 2,
            },
            roam: true,
            categories,
            data: (graph?.nodes || []).map((n: any) => ({
              id: n.id,
              name: n.label,
              value: n.weight,
              symbolSize: Math.max(4, Math.min(22, Number(n.weight || 1))),
              category: n.category === "resource" ? 1 : 0,
            })),
            edges: (graph?.links || []).map((e: any) => ({ source: e.source, target: e.target, value: e.value })),
            lineStyle: { color: "rgba(148,163,184,0.35)", width: 1 },
            itemStyle: {
              color: (p: any) => (p.data.category === 0 ? "#38bdf8" : "#f59e0b"),
            },
            emphasis: { label: { show: true, color: "#f8fafc" } },
          },
        ],
      });

      const endpoints = Array.from(new Set((surface || []).map((r: any) => r.endpoint)));
      const buckets = Array.from(new Set((surface || []).map((r: any) => r.bucket_ts))).sort();
      const data = (surface || []).map((r: any) => [
        endpoints.indexOf(r.endpoint),
        buckets.indexOf(r.bucket_ts),
        Number(r.error_rate || 0),
      ]);

      surfaceChart?.setOption({
        animation: false,
        tooltip: {},
        visualMap: {
          max: 100,
          min: 0,
          calculable: true,
          inRange: { color: ["#0f172a", "#22d3ee", "#f97316", "#ef4444"] },
          textStyle: { color: "#e2e8f0" },
        },
        xAxis3D: { type: "category", data: endpoints, axisLabel: { color: "#94a3b8", rotate: 28 } },
        yAxis3D: { type: "category", data: buckets, axisLabel: { color: "#94a3b8" } },
        zAxis3D: { type: "value", name: "error_rate", axisLabel: { color: "#94a3b8" } },
        grid3D: {
          boxWidth: 180,
          boxDepth: 100,
          light: { main: { intensity: 1.2, shadow: true }, ambient: { intensity: 0.45 } },
          viewControl: { projection: "perspective", autoRotate: false },
          environment: "auto",
        },
        series: [
          {
            type: "surface",
            wireframe: { show: true },
            data,
          },
        ],
      });
    } catch (e: any) {
      console.error("[Investigation3D] load error", e);
      error = e?.message || "Failed to load 3D investigation views";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    // echarts-gl touches browser globals, so load it only after hydration.
    void import("echarts-gl").then(() => {
      const now = new Date();
      const start = new Date(now);
      start.setUTCDate(now.getUTCDate() - 14);
      startDate = start.toISOString().slice(0, 10);
      endDate = now.toISOString().slice(0, 10);
      load();
    }).catch((e) => {
      console.error("[Investigation3D] failed to load echarts-gl", e);
      error = "Failed to initialize 3D charting";
    });

    const onResize = () => {
      forceChart?.resize();
      surfaceChart?.resize();
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      forceChart?.dispose();
      surfaceChart?.dispose();
    };
  });
</script>

<section class="admin-panel p-6" data-testid="investigation-3d">
  <div class="flex flex-col lg:flex-row lg:items-end gap-3 mb-4">
    <div class="flex gap-2">
      <input type="date" class="admin-input" bind:value={startDate} aria-label="3D start date" />
      <input type="date" class="admin-input" bind:value={endDate} aria-label="3D end date" />
    </div>
    <button class="admin-btn admin-btn-primary" on:click={load}>Refresh 3D Views</button>
  </div>

  {#if derivedFromEvents}
    <p class="mb-3 rounded-md border border-amber-500/35 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
      3D endpoints returned sparse payloads. Displaying derived 3D projections from event trail for continuity.
    </p>
  {/if}

  <p class="text-xs text-slate-400 mb-3">
    3D is intentionally used only for dense investigation views: actor-resource anomaly graph and latency/error landscape.
  </p>

  {#if loading}
    <p class="text-slate-300">Loading 3D investigative views...</p>
  {:else if error}
    <p class="text-rose-300">{error}</p>
  {:else}
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <div class="admin-panel p-3">
        <h3 class="text-slate-200 font-semibold mb-2">3D Force Graph: Actor-Resource Interactions</h3>
        <div bind:this={forceHost} style="height:460px"></div>
      </div>
      <div class="admin-panel p-3">
        <h3 class="text-slate-200 font-semibold mb-2">3D Surface: Latency/Error Density by Endpoint and Time</h3>
        <div bind:this={surfaceHost} style="height:460px"></div>
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
    padding: 0.45rem 0.6rem;
  }
</style>
