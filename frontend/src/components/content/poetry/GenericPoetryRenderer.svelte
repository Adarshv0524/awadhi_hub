<script lang="ts">
  type MediaType = "image" | "audio";

  export let poetryNode: {
    id: number;
    poetry_type: string;
    sequence_no: number;
    main_text: string;
    prosody_metadata?: Record<string, unknown> | null;
    text_devanagari?: string | null;
    text_romanized?: string | null;
    meaning?: string | null;
  };
  export let mode: "default" | "chapter" = "default";

  type SafeMedia = {
    type: MediaType;
    url: string;
    altText: string;
  };

  function sanitizeMediaUrl(value: unknown): string | null {
    if (typeof value !== "string") return null;
    const candidate = value.trim();
    if (!candidate) return null;

    try {
      const parsed = new URL(candidate, typeof window !== "undefined" ? window.location.origin : "http://localhost");
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        return null;
      }
      return parsed.toString();
    } catch {
      return null;
    }
  }

  function parseSafeMedia(node: typeof poetryNode): SafeMedia | null {
    const metadata = node?.prosody_metadata;
    if (!metadata || typeof metadata !== "object") return null;

    const media = (metadata as Record<string, unknown>).media;
    if (!media || typeof media !== "object") return null;

    const mediaObj = media as Record<string, unknown>;
    const mediaType = mediaObj.type;
    if (mediaType !== "image" && mediaType !== "audio") return null;

    const url = sanitizeMediaUrl(mediaObj.url);
    if (!url) return null;

    const altTextRaw = typeof mediaObj.alt_text === "string" ? mediaObj.alt_text.trim() : "";
    const altText = altTextRaw || "Poetry media";

    return {
      type: mediaType,
      url,
      altText,
    };
  }

  $: safeMedia = parseSafeMedia(poetryNode);
</script>

<article
  class={mode === "chapter" ? "py-1" : "rounded-xl border border-slate-500/40 bg-slate-800/30 p-4 md:p-5"}
  aria-labelledby={`poetry-${poetryNode.id}`}
>
  {#if mode !== "chapter"}
  <header class="mb-3 flex items-center justify-between gap-3">
    <span class="rounded-full border border-slate-400/40 bg-slate-500/10 px-3 py-1 text-xs font-medium uppercase tracking-wide text-slate-200">
      {poetryNode.poetry_type || "other_poetry"}
    </span>
    <span class="text-xs text-slate-400">#{poetryNode.sequence_no}</span>
  </header>
  {/if}

  <h2 id={`poetry-${poetryNode.id}`} class="sr-only">Poetry item {poetryNode.sequence_no}</h2>

  <p class={mode === "chapter" ? "whitespace-pre-wrap text-[1.14rem] leading-[1.72] text-slate-100" : "whitespace-pre-wrap text-lg leading-relaxed text-slate-100"}>{poetryNode.main_text}</p>

  {#if safeMedia?.type === "image"}
    <figure class="mt-4 overflow-hidden rounded-lg border border-slate-500/30 bg-slate-900/40">
      <img
        src={safeMedia.url}
        alt={safeMedia.altText}
        loading="lazy"
        class="h-auto max-h-[26rem] w-full object-contain"
      />
    </figure>
  {:else if safeMedia?.type === "audio"}
    <div class="mt-4 rounded-lg border border-slate-500/30 bg-slate-900/40 p-3">
      <audio controls preload="none" class="w-full" aria-label={safeMedia.altText}>
        <source src={safeMedia.url} />
        Your browser does not support the audio element.
      </audio>
    </div>
  {/if}

  {#if poetryNode.meaning}
    <p class={mode === "chapter" ? "mt-1.5 text-[0.94rem] leading-6 text-slate-400" : "mt-3 border-l-2 border-slate-400/30 pl-3 text-sm text-slate-300"}>{poetryNode.meaning}</p>
  {/if}

  {#if mode !== "chapter"}
    <p class="mt-3 text-xs text-slate-400">Fallback renderer active for unknown type. The reader remains stable.</p>
  {/if}
</article>
