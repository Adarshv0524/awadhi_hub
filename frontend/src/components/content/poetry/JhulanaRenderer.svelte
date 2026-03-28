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
</script>

<article class="rounded-xl border border-sky-400/30 bg-sky-500/5 p-4 md:p-5" aria-labelledby={`poetry-${poetryNode.id}`}>
  <header class="mb-3 flex items-center justify-between gap-3">
    <span class="rounded-full border border-sky-300/40 bg-sky-400/10 px-3 py-1 text-xs font-medium uppercase tracking-wide text-sky-200">
      Jhulana
    </span>
    <span class="text-xs text-slate-400">#{poetryNode.sequence_no}</span>
  </header>

  <h2 id={`poetry-${poetryNode.id}`} class="sr-only">Jhulana {poetryNode.sequence_no}</h2>

  <p class="whitespace-pre-wrap text-lg leading-relaxed text-slate-100">{poetryNode.main_text}</p>

  {#if poetryNode.meaning}
    <p class="mt-3 border-l-2 border-sky-300/30 pl-3 text-sm text-slate-300">{poetryNode.meaning}</p>
  {/if}
</article>
