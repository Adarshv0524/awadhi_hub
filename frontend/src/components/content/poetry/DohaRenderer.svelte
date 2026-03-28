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

<article class="rounded-xl border border-emerald-400/30 bg-emerald-500/5 p-4 md:p-5" aria-labelledby={`poetry-${poetryNode.id}`}>
  <header class="mb-3 flex items-center justify-between gap-3">
    <span class="rounded-full border border-emerald-300/40 bg-emerald-400/10 px-3 py-1 text-xs font-medium uppercase tracking-wide text-emerald-200">
      Doha
    </span>
    <span class="text-xs text-slate-400">#{poetryNode.sequence_no}</span>
  </header>

  <h2 id={`poetry-${poetryNode.id}`} class="sr-only">Doha {poetryNode.sequence_no}</h2>

  <p class="whitespace-pre-wrap text-lg leading-relaxed text-slate-100">{poetryNode.main_text}</p>

  {#if poetryNode.meaning}
    <p class="mt-3 border-l-2 border-emerald-300/30 pl-3 text-sm text-slate-300">{poetryNode.meaning}</p>
  {/if}
</article>
