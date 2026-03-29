<script lang="ts">
  export let dates: string[] = [];
  export let series: Record<string, number[]> = {};
  export let colors: Record<string, string> = {};
  export let width = 900;
  export let height = 320;

  const padTop = 18;
  const padRight = 16;
  const padBottom = 34;
  const padLeft = 44;

  $: keys = Object.keys(series);
  $: maxValue = Math.max(1, ...keys.flatMap((k) => series[k] || []).map((v) => Number(v || 0)));
  $: chartW = Math.max(1, width - padLeft - padRight);
  $: chartH = Math.max(1, height - padTop - padBottom);

  function xForIndex(index: number): number {
    if (dates.length <= 1) return padLeft;
    return padLeft + (index / (dates.length - 1)) * chartW;
  }

  function yForValue(value: number): number {
    return padTop + (1 - (Number(value || 0) / maxValue)) * chartH;
  }

  function pathFor(values: number[]): string {
    if (!values || values.length === 0) return "";
    return values
      .map((value, index) => `${index === 0 ? "M" : "L"}${xForIndex(index)} ${yForValue(value)}`)
      .join(" ");
  }

  function tickValues(): number[] {
    return [0, 0.25, 0.5, 0.75, 1].map((ratio) => Math.round(maxValue * ratio));
  }

  function labelDate(raw: string): string {
    try {
      const d = new Date(raw);
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch {
      return raw;
    }
  }
</script>

<div class="rounded-lg border border-slate-700 bg-slate-950/60 p-3">
  <svg viewBox={`0 0 ${width} ${height}`} class="h-auto w-full" role="img" aria-label="Growth trends time series chart">
    {#each tickValues() as tick}
      <line
        x1={padLeft}
        y1={yForValue(tick)}
        x2={padLeft + chartW}
        y2={yForValue(tick)}
        stroke="rgba(148, 163, 184, 0.25)"
        stroke-width="1"
      />
      <text
        x={padLeft - 8}
        y={yForValue(tick) + 4}
        text-anchor="end"
        fill="rgb(148, 163, 184)"
        font-size="10"
      >{tick}</text>
    {/each}

    <line x1={padLeft} y1={padTop + chartH} x2={padLeft + chartW} y2={padTop + chartH} stroke="rgba(148, 163, 184, 0.55)" stroke-width="1" />
    <line x1={padLeft} y1={padTop} x2={padLeft} y2={padTop + chartH} stroke="rgba(148, 163, 184, 0.55)" stroke-width="1" />

    {#each keys as key}
      {@const values = series[key] || []}
      {@const color = colors[key] || "#94a3b8"}
      <path d={pathFor(values)} fill="none" stroke={color} stroke-width="2.2" />
      {#if values.length > 0}
        <circle cx={xForIndex(values.length - 1)} cy={yForValue(values[values.length - 1])} r="3" fill={color} />
      {/if}
    {/each}

    {#if dates.length > 0}
      <text x={padLeft} y={height - 10} text-anchor="start" fill="rgb(148, 163, 184)" font-size="10">{labelDate(dates[0])}</text>
      <text x={padLeft + chartW / 2} y={height - 10} text-anchor="middle" fill="rgb(148, 163, 184)" font-size="10">{labelDate(dates[Math.floor(dates.length / 2)])}</text>
      <text x={padLeft + chartW} y={height - 10} text-anchor="end" fill="rgb(148, 163, 184)" font-size="10">{labelDate(dates[dates.length - 1])}</text>
    {/if}
  </svg>

  <div class="mt-3 flex flex-wrap gap-3 text-xs">
    {#each keys as key}
      <span class="inline-flex items-center gap-2 rounded border border-slate-700 px-2 py-1 text-slate-200">
        <span class="h-2.5 w-2.5 rounded-full" style={`background:${colors[key] || "#94a3b8"}`}></span>
        <span class="capitalize">{key}</span>
      </span>
    {/each}
  </div>
</div>
