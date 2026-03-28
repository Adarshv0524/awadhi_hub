<script lang="ts">
  import Badge from "../../ui/Badge.svelte";
  import Button from "../../ui/Button.svelte";

  export let previous: { id: number; poetry_type: string; sequence_no: number } | null = null;
  export let next: { id: number; poetry_type: string; sequence_no: number } | null = null;

  export let canGoPrevious = false;
  export let canGoNext = false;

  export let onPrevious: () => void;
  export let onNext: () => void;

  function onNavKeydown(event: KeyboardEvent, action: () => void, enabled: boolean) {
    if (!enabled) return;
    if (event.key === "Enter" || event.key === " " || event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      action();
    }
  }

  const formatType = (value?: string) => {
    if (!value) return "Unknown";
    return value
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };
</script>

<nav aria-label="Poetry reader navigation" class="glass-panel mt-8 p-4 md:p-5">
  <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <Button
      type="button"
      size="sm"
      variant="outline"
      className="justify-center disabled:cursor-not-allowed disabled:opacity-50"
      on:click={onPrevious}
      on:keydown={(event) => onNavKeydown(event, onPrevious, canGoPrevious)}
      disabled={!canGoPrevious}
      aria-label="Go to previous poetry item"
    >
      <span aria-hidden="true">←</span>
      <span>Previous</span>
    </Button>

    <div class="flex flex-wrap items-center justify-center gap-2 text-xs md:text-sm">
      <Badge>
        Previous: {previous ? `${formatType(previous.poetry_type)} ←` : "Start of chapter"}
      </Badge>
      <Badge tone="accent">
        Next: {next ? `${formatType(next.poetry_type)} →` : "End of chapter"}
      </Badge>
    </div>

    <Button
      type="button"
      size="sm"
      variant="outline"
      className="justify-center disabled:cursor-not-allowed disabled:opacity-50"
      on:click={onNext}
      on:keydown={(event) => onNavKeydown(event, onNext, canGoNext)}
      disabled={!canGoNext}
      aria-label="Go to next poetry item"
    >
      <span>Next</span>
      <span aria-hidden="true">→</span>
    </Button>
  </div>
</nav>
