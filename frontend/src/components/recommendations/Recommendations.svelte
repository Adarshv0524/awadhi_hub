<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  export let content_type: string;
  export let content_id: number;
  export let limit: number = 5;

  let items: any[] = [];
  let loading = true;
  let error = "";

  function safeText(value: unknown, max = 160): string {
    if (typeof value !== "string") return "";
    const normalized = value.trim();
    if (!normalized) return "";
    return normalized.length > max ? `${normalized.slice(0, max)}...` : normalized;
  }

  async function fetchRecommendations(signal: AbortSignal): Promise<any[]> {
    return api(`/recommendations/${content_type}/${content_id}?limit=${limit}`, {
      method: "GET",
      signal,
    });
  }

  onMount(() => {
    let active = true;
    const controller = new AbortController();

    (async () => {
      loading = true;
      error = "";
      try {
        const response: any = await fetchRecommendations(controller.signal);

        // Normalize response (handle array or object with results)
        const rawItems = Array.isArray(response) ? response : response?.results || response?.items || [];

        const normalized = rawItems
          .filter((item: any) => item && (item.id || item.content_id))
          .map((item: any) => ({
            id: item.content_id || item.id,
            type: safeText(item.content_type || content_type, 50) || content_type,
            title: getTitle(item),
            snippet: getSnippet(item),
            url: getUrl(item),
            score: Number(item.score || 0),
          }))
          .filter((item: any) => item.url);

        if (!active || controller.signal.aborted) return;
        items = normalized;
      } catch (e: any) {
        if (!active || controller.signal.aborted) return;
        error = e?.message || "Failed to load recommendations";
        console.error("[Recommendations] Error:", e);
        items = [];
      } finally {
        if (!active || controller.signal.aborted) return;
        loading = false;
      }
    })();

    return () => {
      active = false;
      controller.abort();
    };
  });

  function getTitle(item: any): string {
    // Priority order for title extraction
    if (item.title_or_text) return item.title_or_text;
    if (item.title) return item.title;
    if (item.lemma_devanagari) {
      const devanagari = safeText(item.lemma_devanagari, 120);
      const roman = safeText(item.lemma_roman, 60);
      return devanagari + (roman ? ` (${roman})` : "");
    }
    if (item.text_devanagari) return safeText(item.text_devanagari, 120);
    if (item.main_text) {
      // For doha, show first line only
      const mainText = safeText(item.main_text, 220);
      const firstLine = mainText.split(/\r?\n/)[0]?.trim();
      return firstLine || safeText(mainText, 80);
    }
    if (item.text) return safeText(item.text, 80);
    
    const type = item.content_type || content_type;
    const id = item.content_id || item.id;
    return `${type.charAt(0).toUpperCase() + type.slice(1)} #${id}`;
  }

  function getSnippet(item: any): string {
    // Extract meaningful snippet
    if (item.meaning) return safeText(item.meaning, 160);
    if (item.excerpt) return safeText(item.excerpt, 160);
    if (item.body) return safeText(item.body, 160);
    if (item.snippet) return safeText(item.snippet, 160);
    
    // For doha, show second line if available
    if (item.main_text) {
      const normalized = safeText(item.main_text, 500);
      const lines = normalized.split(/\r?\n/).filter((l: string) => l.trim());
      if (lines.length > 1) return safeText(lines.slice(1).join(" "), 160);
    }
    
    return "";
  }

  function getUrl(item: any): string {
    const type = (item.content_type || content_type).toLowerCase();
    const id = item.content_id || item.id;
    
    if (!id) return "";
    
    // Map content types to routes
    const poetryTypes = new Set(["poetry", "poetry_node", "doha", "chaupai", "sorath", "jhulana", "savaiya", "ghanakshari", "chappay", "other_poetry"]);
    const typeMap: Record<string, string> = {
      dictionary: "dictionary",
      idiom: "idioms",
      idioms: "idioms",
      article: "articles",
      articles: "articles",
    };

    if (poetryTypes.has(type)) return `/poetry/${id}`;
    const route = typeMap[type];
    return route ? `/${route}/${id}` : "";
  }

  function getTypeColor(type: string): string {
    const colors: Record<string, string> = {
      doha: "cyan",
      dictionary: "blue",
      idiom: "purple",
      article: "pink",
    };
    return colors[type.toLowerCase()] || "indigo";
  }

  function getHeading(): string {
    const headings: Record<string, string> = {
      doha: "Related Poetry",
      poetry: "Related Poetry",
      dictionary: "Related Words",
      idiom: "Related Idioms",
      article: "Related Articles",
    };
    return headings[content_type.toLowerCase()] || "Related Content";
  }

  function getSubtitle(): string {
    const subtitles: Record<string, string> = {
      doha: "Continue reading across adjacent verse and themes.",
      poetry: "Continue reading across adjacent verse and themes.",
      dictionary: "Expand your vocabulary with connected lexical entries.",
      idiom: "Explore neighboring idioms and proverb usage.",
      article: "Discover adjacent long-form articles and references.",
    };
    return subtitles[content_type.toLowerCase()] || "Discover connected content across modules.";
  }
</script>

{#if !loading && !error && items.length > 0}
  <section class="mt-8 bg-slate-800 border border-slate-700 rounded-lg p-6" aria-labelledby="recommendations-heading">
    <h3 id="recommendations-heading" class="text-xl font-semibold text-slate-100 mb-1 flex items-center gap-2">
      <span class="text-2xl">💡</span>
      Related Content
    </h3>
    <p class="mb-4 text-sm text-slate-400">{getSubtitle()}</p>
    
    <div class="grid grid-cols-1 gap-3">
      {#each items as item}
        <article class="group bg-slate-900/50 border border-slate-700 rounded-lg p-4 hover:border-{getTypeColor(item.type)}-500 hover:bg-slate-900 transition-all">
          <a href={item.url} class="block space-y-2">
            <div class="flex items-start justify-between gap-3">
              <h4 class="text-base font-medium text-{getTypeColor(item.type)}-400 group-hover:text-{getTypeColor(item.type)}-300 transition-colors line-clamp-2">
                {item.title}
              </h4>
              <span class="text-xs px-2 py-1 bg-{getTypeColor(item.type)}-900/40 text-{getTypeColor(item.type)}-300 rounded capitalize shrink-0">
                {item.type}
              </span>
            </div>
            
            {#if item.snippet}
              <p class="text-sm text-slate-400 line-clamp-2 leading-relaxed">
                {item.snippet}
              </p>
            {/if}
            
            {#if item.score > 0}
              <div class="flex items-center gap-2 text-xs text-slate-600">
                <span>Relevance:</span>
                <div class="flex-1 max-w-24 bg-slate-700 rounded-full h-1.5 overflow-hidden">
                  <div 
                    class="bg-{getTypeColor(item.type)}-500 h-full rounded-full transition-all"
                    style="width: {Math.min(item.score * 10, 100)}%"
                  ></div>
                </div>
                <span class="font-mono">{(item.score * 100).toFixed(0)}%</span>
              </div>
            {/if}
          </a>
        </article>
      {/each}
    </div>
  </section>
{:else if loading}
  <div class="mt-8 text-center py-6">
    <div class="inline-flex items-center gap-2 text-slate-500 text-sm">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Loading recommendations...
    </div>
  </div>
{:else if error}
  <div class="mt-8 bg-red-900/20 border border-red-700/50 rounded-lg p-4 text-center">
    <p class="text-red-400 text-sm">{error}</p>
  </div>
{/if}

