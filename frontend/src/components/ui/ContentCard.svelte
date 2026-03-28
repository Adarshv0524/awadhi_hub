<script lang="ts">
  export let as: "article" | "div" = "article";
  export let className = "";
  export let highlighted = false;
</script>

<svelte:element this={as} class={`ui-card ${highlighted ? "ring-1 ring-cyan-400/45" : ""} ${className}`.trim()}>
  <slot />
</svelte:element>
