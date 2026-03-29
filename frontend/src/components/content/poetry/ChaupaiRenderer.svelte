<script lang="ts">
  export let poetryNode: {
    id: number;
    poetry_type: string;
    sequence_no: number;
    main_text: string;
    text_devanagari?: string | null;
    text_romanized?: string | null;
    meaning?: string | null;
  };
  export let mode: "default" | "chapter" = "default";

  $: lines = String(poetryNode.main_text || "")
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
</script>

<article
  class={mode === "chapter" ? "py-1" : "rounded-xl border border-amber-400/35 bg-gradient-to-br from-amber-500/10 via-slate-900 to-orange-500/10 p-4 md:p-5"}
  aria-labelledby={`poetry-${poetryNode.id}`}
>
  {#if mode !== "chapter"}
  <header class="mb-3 flex items-center justify-between gap-3">
    <span class="rounded-full border border-amber-300/40 bg-amber-400/10 px-3 py-1 text-xs font-medium uppercase tracking-wide text-amber-200">
      Chaupai
    </span>
    <span class="text-xs text-slate-400">#{poetryNode.sequence_no}</span>
  </header>
  {/if}

  <h2 id={`poetry-${poetryNode.id}`} class="sr-only">Chaupai {poetryNode.sequence_no}</h2>

  <div class={mode === "chapter" ? "space-y-1 text-[1.16rem] leading-[1.75] text-slate-100" : "space-y-1.5 text-lg leading-relaxed text-slate-100"}>
    {#if lines.length > 0}
      {#each lines as line}
        <p>{line}</p>
      {/each}
    {:else}
      <p>{poetryNode.main_text}</p>
    {/if}
  </div>

  {#if poetryNode.meaning}
    <p class={mode === "chapter" ? "mt-1.5 text-[0.94rem] leading-6 text-slate-400" : "mt-3 border-l-2 border-amber-300/30 pl-3 text-sm text-slate-300"}>{poetryNode.meaning}</p>
  {/if}
</article>
