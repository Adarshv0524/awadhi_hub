<script lang="ts">
  export let values: number[] = [];
  export let width = 200;
  export let height = 50;
  export let color = "currentColor";
  export let fillOpacity = 0.1;

  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;

  function y(v: number) {
    return height - ((v - min) / range) * height;
  }

  const points = values
    .map((v, i) => `${(i / (values.length - 1)) * width},${y(v)}`)
    .join(" ");

  // Create area fill path (includes baseline)
  const areaPath = values.length > 0
    ? `M 0,${height} L ${points} L ${width},${height} Z`
    : "";

  // Stats for tooltip
  const total = values.reduce((sum, v) => sum + v, 0);
  const avg = values.length > 0 ? (total / values.length).toFixed(1) : "0";
  const trend = values.length >= 2 
    ? ((values[values.length - 1] - values[0]) / (values[0] || 1) * 100).toFixed(1)
    : "0";
</script>

<div class="inline-block group relative">
  <svg {width} {height} class="transition-opacity hover:opacity-80">
    <!-- Area fill -->
    {#if areaPath}
      <path
        d={areaPath}
        fill={color}
        fill-opacity={fillOpacity}
      />
    {/if}
    
    <!-- Line -->
    <polyline
      fill="none"
      stroke={color}
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      points={points}
    />
    
    <!-- Dots on hover -->
    {#each values as v, i}
      <circle
        cx={(i / (values.length - 1)) * width}
        cy={y(v)}
        r="3"
        fill={color}
        class="opacity-0 group-hover:opacity-100 transition-opacity"
      />
    {/each}
  </svg>
  
  <!-- Tooltip on hover -->
  <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-950 border border-slate-600 rounded shadow-lg text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
    <div class="text-slate-400">Max: <span class="text-cyan-400 font-mono">{max}</span></div>
    <div class="text-slate-400">Avg: <span class="text-blue-400 font-mono">{avg}</span></div>
    <div class="text-slate-400">Trend: <span class="text-green-400 font-mono">{trend}%</span></div>
  </div>
</div>
