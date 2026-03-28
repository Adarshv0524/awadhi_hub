<script lang="ts">
  export let tone: "neutral" | "accent" | "positive" | "warning" = "neutral";
  export let className = "";
</script>

<span data-tone={tone === "neutral" ? undefined : tone} class={`ui-badge ${className}`.trim()}>
  <slot />
</span>
