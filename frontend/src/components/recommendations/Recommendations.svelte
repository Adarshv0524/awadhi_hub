<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  export let content_type: string;
  export let content_id: number;
  export let limit: number = 5;

  let items: any[] = [];
  let loading = true;
  let error = "";

  onMount(async () => {
    loading = true;
    error = "";
    try {
      const response = await api(`/recommendations/${content_type}/${content_id}?limit=${limit}`);
      
      // Normalize response (handle array or object with results)
      let rawItems = Array.isArray(response) ? response : response?.results || response?.items || [];
      
      // Filter and map items
      items = rawItems
        .filter((item: any) => item && (item.id || item.content_id))
        .map((item: any) => ({
          id: item.content_id || item.id,
          type: item.content_type || content_type,
          title: getTitle(item),
          snippet: getSnippet(item),
          url: getUrl(item),
          score: item.score || 0,
        }))
        .filter((item: any) => item.url); // Only items with valid URLs
      
    } catch (e: any) {
      error = e?.message || "Failed to load recommendations";
      console.error("[Recommendations] Error:", e);
      items = [];
    } finally {
      loading = false;
    }
  });

  function getTitle(item: any): string {
    // Priority order for title extraction
    if (item.title_or_text) return item.title_or_text;
    if (item.title) return item.title;
    if (item.lemma_devanagari) {
      return item.lemma_devanagari + (item.lemma_roman ? ` (${item.lemma_roman})` : "");
    }
    if (item.text_devanagari) return item.text_devanagari;
    if (item.main_text) {
      // For doha, show first line only
      const firstLine = item.main_text.split(/\r?\n/)[0]?.trim();
      return firstLine || item.main_text.slice(0, 80);
    }
    if (item.text) return item.text.slice(0, 80);
    
    const type = item.content_type || content_type;
    const id = item.content_id || item.id;
    return `${type.charAt(0).toUpperCase() + type.slice(1)} #${id}`;
  }

  function getSnippet(item: any): string {
    // Extract meaningful snippet
    if (item.meaning) return item.meaning.slice(0, 160);
    if (item.excerpt) return item.excerpt.slice(0, 160);
    if (item.body) return item.body.slice(0, 160);
    if (item.snippet) return item.snippet.slice(0, 160);
    
    // For doha, show second line if available
    if (item.main_text) {
      const lines = item.main_text.split(/\r?\n/).filter((l: string) => l.trim());
      if (lines.length > 1) return lines.slice(1).join(" ").slice(0, 160);
    }
    
    return "";
  }

  function getUrl(item: any): string {
    const type = (item.content_type || content_type).toLowerCase();
    const id = item.content_id || item.id;
    
    if (!id) return "";
    
    // Map content types to routes
    const typeMap: Record<string, string> = {
      doha: "doha",
      dohas: "doha",
      dictionary: "dictionary",
      idiom: "idioms",
      idioms: "idioms",
      article: "articles",
      articles: "articles",
    };
    
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
      doha: "Related Dohas",
      dictionary: "Related Words",
      idiom: "Related Idioms",
      article: "Related Articles",
    };
    return headings[content_type.toLowerCase()] || "Related Content";
  }
</script>

{#if !loading && !error && items.length > 0}
  <section class="mt-8 bg-slate-800 border border-slate-700 rounded-lg p-6" aria-labelledby="recommendations-heading">
    <h3 id="recommendations-heading" class="text-xl font-semibold text-{getTypeColor(content_type)}-400 mb-4 flex items-center gap-2">
      <span class="text-2xl">💡</span>
      {getHeading()}
    </h3>
    
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

