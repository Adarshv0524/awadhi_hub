<script lang="ts">
  export let type: "button" | "submit" | "reset" = "button";
  export let variant: "primary" | "ghost" | "outline" = "ghost";
  export let size: "sm" | "md" = "md";
  export let disabled = false;
  export let className = "";
</script>

<button
  {...$$restProps}
  {type}
  {disabled}
  data-variant={variant}
  data-size={size}
  data-disabled={disabled ? "true" : "false"}
  class={`ui-button ${className}`.trim()}
  on:click
  on:keydown
>
  <slot />
</button>
