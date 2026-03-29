<script lang="ts">
  export let as: "article" | "div" = "article";
  export let className = "";
  export let highlighted = false;
</script>

<svelte:element this={as} data-highlighted={highlighted ? "true" : "false"} class={`ui-card ${className}`.trim()}>
  <slot />
</svelte:element>
