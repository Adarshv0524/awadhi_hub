<script lang="ts">
  import { onMount } from "svelte";

  import { API_BASE } from "../../lib/api";
  import Badge from "../ui/Badge.svelte";
  import Button from "../ui/Button.svelte";
  import ContentCard from "../ui/ContentCard.svelte";

  type ContentFilter = "all" | "poetry" | "doha" | "dictionary" | "idiom" | "article";
  type SortFilter = "relevance" | "recent";

  type PoetryType = {
    poetry_type: string;
    display_name: string;
    is_active?: boolean;
  };

  type DohaItem = {
    id: number;
    main_text: string;
    meaning?: string;
  };

  type PoetryItem = {
    id: number;
    poetry_type: string;
    sequence_no: number;
    chapter_path: string;
    main_text: string;
    meaning?: string;
  };

  type DictionaryItem = {
    id: number;
    lemma_devanagari?: string;
    lemma_roman?: string;
  };

  type IdiomItem = {
    id: number;
    text_devanagari?: string;
    text?: string;
    meaning?: string;
  };

  type ArticleItem = {
    id: number;
    title: string;
    excerpt?: string;
  };

  export let initialQuery = "";
  export let initialType: ContentFilter = "all";
  export let initialSort: SortFilter = "relevance";
  export let initialAuthor = "";
  export let initialWork = "";
  export let initialPoetryType = "all";

  let query = initialQuery;
  let contentFilter: ContentFilter = initialType;
  let sortBy: SortFilter = initialSort;
  let authorFilter = initialAuthor;
  let workFilter = initialWork;
  let poetryType = initialPoetryType;

  let poetryTypes: PoetryType[] = [];

  let dohas: DohaItem[] = [];
  let poetry: PoetryItem[] = [];
  let dictionary: DictionaryItem[] = [];
  let idioms: IdiomItem[] = [];
  let articles: ArticleItem[] = [];

  let loading = false;
  let hasSearched = false;
  let errors: string[] = [];
  let isMounted = false;

  let activeController: AbortController | null = null;
  let debounceId: ReturnType<typeof setTimeout> | null = null;
  let searchVersion = 0;

  const labels: Record<ContentFilter, string> = {
    all: "All",
    poetry: "Poetry",
    doha: "Doha",
    dictionary: "Dictionary",
    idiom: "Idioms",
    article: "Articles",
  };

  const sections = ["poetry", "doha", "dictionary", "idiom", "article"] as const;

  const shouldFetch = (name: typeof sections[number]) => contentFilter === "all" || contentFilter === name;

  const totalResults =
    poetry.length + dohas.length + dictionary.length + idioms.length + articles.length;

  function clearResults() {
    dohas = [];
    poetry = [];
    dictionary = [];
    idioms = [];
    articles = [];
    errors = [];
  }

  function updateUrl() {
    if (typeof window === "undefined") return;

    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (contentFilter !== "all") params.set("type", contentFilter);
    if (sortBy !== "relevance") params.set("sort", sortBy);
    if (authorFilter.trim()) params.set("author", authorFilter.trim());
    if (workFilter.trim()) params.set("work", workFilter.trim());
    if (poetryType !== "all" && (contentFilter === "all" || contentFilter === "poetry")) {
      params.set("poetry_type", poetryType);
    }

    const nextPath = `/search${params.toString() ? `?${params.toString()}` : ""}`;
    history.replaceState({}, "", nextPath);
  }

  async function fetchJson<T>(path: string, signal: AbortSignal): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "GET",
      credentials: "include",
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return (await response.json()) as T;
  }

  async function performSearch() {
    const cleanQuery = query.trim();
    updateUrl();

    if (!cleanQuery) {
      hasSearched = false;
      loading = false;
      clearResults();
      return;
    }

    hasSearched = true;
    loading = true;
    errors = [];

    activeController?.abort();
    activeController = new AbortController();
    const signal = activeController.signal;
    const myVersion = ++searchVersion;

    const sharedParams = new URLSearchParams();
    sharedParams.set("q", cleanQuery);
    sharedParams.set("limit", "20");
    sharedParams.set("sort", sortBy);
    if (authorFilter.trim()) sharedParams.set("author", authorFilter.trim());
    if (workFilter.trim()) sharedParams.set("work", workFilter.trim());

    const jobs: Array<{ key: typeof sections[number]; path: string }> = [];

    if (shouldFetch("doha")) {
      jobs.push({ key: "doha", path: `/search?${sharedParams.toString()}` });
    }

    if (shouldFetch("poetry")) {
      const poetryParams = new URLSearchParams(sharedParams);
      if (poetryType !== "all") poetryParams.set("poetry_type", poetryType);
      jobs.push({ key: "poetry", path: `/api/v1/poetry/search?${poetryParams.toString()}` });
    }

    if (shouldFetch("dictionary")) {
      jobs.push({ key: "dictionary", path: `/dictionary?q=${encodeURIComponent(cleanQuery)}&limit=20` });
    }

    if (shouldFetch("idiom")) {
      jobs.push({ key: "idiom", path: `/idioms?q=${encodeURIComponent(cleanQuery)}&limit=20` });
    }

    if (shouldFetch("article")) {
      jobs.push({ key: "article", path: `/articles?q=${encodeURIComponent(cleanQuery)}&limit=20` });
    }

    const settled = await Promise.allSettled(
      jobs.map(async (job) => ({ key: job.key, data: await fetchJson<any>(job.path, signal) }))
    );

    if (myVersion !== searchVersion || signal.aborted) {
      return;
    }

    clearResults();

    for (const result of settled) {
      if (result.status !== "fulfilled") {
        const reason = String(result.reason || "Request failed");
        if (!reason.includes("AbortError")) {
          // Do not expose raw query/error payloads in client logs or UI.
          errors = [...errors, "One or more sections failed to load."];
        }
        continue;
      }

      const { key, data } = result.value;
      if (key === "doha") dohas = Array.isArray(data?.results) ? data.results : [];
      if (key === "poetry") poetry = Array.isArray(data?.results) ? data.results : [];
      if (key === "dictionary") dictionary = Array.isArray(data) ? data : [];
      if (key === "idiom") idioms = Array.isArray(data) ? data : [];
      if (key === "article") articles = Array.isArray(data) ? data : [];
    }

    loading = false;
  }

  function queueSearch() {
    if (!isMounted) return;
    if (debounceId) clearTimeout(debounceId);
    debounceId = setTimeout(() => {
      performSearch();
    }, 320);
  }

  function applyFilter(type: ContentFilter) {
    contentFilter = type;
    queueSearch();
  }

  function clearAuthorFilter() {
    authorFilter = "";
    queueSearch();
  }

  function clearWorkFilter() {
    workFilter = "";
    queueSearch();
  }

  function onSubmit(event: Event) {
    event.preventDefault();
    if (debounceId) clearTimeout(debounceId);
    performSearch();
  }

  async function loadPoetryTypes() {
    const controller = new AbortController();
    try {
      const list = await fetchJson<PoetryType[]>(`/api/v1/poetry/types`, controller.signal);
      poetryTypes = Array.isArray(list) ? list.filter((item) => item.is_active !== false) : [];
    } catch {
      poetryTypes = [];
    }
  }

  onMount(() => {
    isMounted = true;

    (async () => {
      await loadPoetryTypes();
      if (query.trim()) {
        await performSearch();
      }
    })();

    return () => {
      isMounted = false;
      if (debounceId) clearTimeout(debounceId);
      activeController?.abort();
    };
  });

  $: queueSearch(), query;
  $: queueSearch(), authorFilter;
  $: queueSearch(), workFilter;
  $: queueSearch(), sortBy;
  $: queueSearch(), poetryType;
</script>

<section class="mx-auto max-w-5xl fade-rise">
  <div class="glass-panel p-5 md:p-7">
    <h1 class="mb-2 text-center text-3xl md:text-4xl font-bold">Search Awadhi Corpus</h1>
    <p class="text-muted mx-auto mb-6 max-w-2xl text-center text-sm md:text-base">
      Explore doha, poetry forms, dictionary entries, idioms, and articles from one place.
    </p>

    <form on:submit={onSubmit} class="space-y-4" aria-label="Search form">
      <div class="grid gap-3 sm:grid-cols-[1fr_auto]">
        <label>
          <span class="sr-only">Search query</span>
          <input
            type="search"
            bind:value={query}
            placeholder="Search by phrase, author, work, or motif"
            aria-label="Search query"
          />
        </label>
        <Button type="submit" variant="primary">Search</Button>
      </div>

      <div class="grid gap-3 md:grid-cols-2">
        <label>
          <span>Author filter</span>
          <input
            type="text"
            bind:value={authorFilter}
            placeholder="e.g. tulsidas"
            aria-label="Author filter"
          />
        </label>
        <label>
          <span>Work filter</span>
          <input
            type="text"
            bind:value={workFilter}
            placeholder="e.g. ramcharitmanas"
            aria-label="Work filter"
          />
        </label>
      </div>

      <div class="flex flex-wrap items-center gap-2 pt-1">
        <span class="text-muted mr-1 text-xs uppercase tracking-wide">Type</span>
        {#each Object.entries(labels) as [key, label]}
          <Button
            type="button"
            size="sm"
            variant={contentFilter === key ? "primary" : "ghost"}
            on:click={() => applyFilter(key as ContentFilter)}
            aria-pressed={contentFilter === key}
          >
            {label}
          </Button>
        {/each}
      </div>

      <div class="grid gap-3 md:grid-cols-2">
        <label>
          <span>Sort by</span>
          <select bind:value={sortBy} aria-label="Sort order">
            <option value="relevance">Relevance</option>
            <option value="recent">Recent</option>
          </select>
        </label>

        <label>
          <span>Poetry form</span>
          <select
            bind:value={poetryType}
            disabled={contentFilter !== "all" && contentFilter !== "poetry"}
            aria-label="Poetry type filter"
          >
            <option value="all">All poetry forms</option>
            {#each poetryTypes as form}
              <option value={form.poetry_type}>{form.display_name}</option>
            {/each}
          </select>
        </label>
      </div>

      {#if authorFilter || workFilter}
        <div class="flex flex-wrap gap-2 pt-1">
          {#if authorFilter}
            <Badge tone="accent">
              Author: {authorFilter}
              <button type="button" class="ml-1 text-xs" on:click={clearAuthorFilter} aria-label="Clear author filter">x</button>
            </Badge>
          {/if}
          {#if workFilter}
            <Badge tone="positive">
              Work: {workFilter}
              <button type="button" class="ml-1 text-xs" on:click={clearWorkFilter} aria-label="Clear work filter">x</button>
            </Badge>
          {/if}
        </div>
      {/if}
    </form>
  </div>

  <div class="mt-5 space-y-5" aria-live="polite" aria-busy={loading}>
    {#if loading}
      <div class="surface-shell p-5">
        <div class="skeleton mb-3 h-4 w-40 rounded"></div>
        <div class="skeleton mb-2 h-16 rounded"></div>
        <div class="skeleton mb-2 h-16 rounded"></div>
        <div class="skeleton h-16 rounded"></div>
      </div>
    {:else if hasSearched}
      <div class="surface-shell p-4 md:p-5">
        <p class="text-sm text-slate-200">
          Found <strong>{totalResults}</strong> result{totalResults !== 1 ? "s" : ""}
          {#if query.trim()}
            for <strong>"{query.trim()}"</strong>
          {/if}
        </p>
        {#if errors.length > 0}
          <p class="mt-2 text-sm text-amber-200">Some sections could not be loaded. You can retry by pressing Search.</p>
        {/if}
      </div>

      {#if shouldFetch("poetry") && poetry.length > 0}
        <section class="surface-shell p-4 md:p-5">
          <h2 class="mb-3 text-2xl">Poetry Forms ({poetry.length})</h2>
          <div class="space-y-3">
            {#each poetry as item}
              <ContentCard>
                <a href={`/${item.chapter_path}`} class="mb-2 block text-lg font-semibold hover:underline">{item.main_text}</a>
                <div class="mb-2 flex flex-wrap gap-2">
                  <Badge tone="positive">{item.poetry_type}</Badge>
                  <Badge>Sequence {item.sequence_no}</Badge>
                </div>
                {#if item.meaning}
                  <p class="text-sm text-muted">{item.meaning}</p>
                {/if}
              </ContentCard>
            {/each}
          </div>
        </section>
      {/if}

      {#if shouldFetch("doha") && dohas.length > 0}
        <section class="surface-shell p-4 md:p-5">
          <h2 class="mb-3 text-2xl">Doha ({dohas.length})</h2>
          <div class="space-y-3">
            {#each dohas as item}
              <ContentCard>
                <a href={`/doha/${item.id}`} class="mb-2 block text-lg font-semibold hover:underline">{item.main_text}</a>
                {#if item.meaning}
                  <p class="text-sm text-muted">{item.meaning}</p>
                {/if}
              </ContentCard>
            {/each}
          </div>
        </section>
      {/if}

      {#if shouldFetch("dictionary") && dictionary.length > 0}
        <section class="surface-shell p-4 md:p-5">
          <h2 class="mb-3 text-2xl">Dictionary ({dictionary.length})</h2>
          <div class="space-y-3">
            {#each dictionary as item}
              <ContentCard>
                <a href={`/dictionary/${item.id}`} class="mb-1 block text-lg font-semibold hover:underline">
                  {item.lemma_devanagari || "Untitled entry"}
                </a>
                {#if item.lemma_roman}
                  <p class="text-sm italic text-muted">{item.lemma_roman}</p>
                {/if}
              </ContentCard>
            {/each}
          </div>
        </section>
      {/if}

      {#if shouldFetch("idiom") && idioms.length > 0}
        <section class="surface-shell p-4 md:p-5">
          <h2 class="mb-3 text-2xl">Idioms ({idioms.length})</h2>
          <div class="space-y-3">
            {#each idioms as item}
              <ContentCard>
                <a href={`/idioms/${item.id}`} class="mb-1 block text-lg font-semibold hover:underline">
                  {item.text_devanagari || item.text || "Untitled idiom"}
                </a>
                {#if item.meaning}
                  <p class="text-sm text-muted">{item.meaning.slice(0, 150)}{item.meaning.length > 150 ? "..." : ""}</p>
                {/if}
              </ContentCard>
            {/each}
          </div>
        </section>
      {/if}

      {#if shouldFetch("article") && articles.length > 0}
        <section class="surface-shell p-4 md:p-5">
          <h2 class="mb-3 text-2xl">Articles ({articles.length})</h2>
          <div class="space-y-3">
            {#each articles as item}
              <ContentCard>
                <a href={`/articles/${item.id}`} class="mb-1 block text-lg font-semibold hover:underline">{item.title}</a>
                {#if item.excerpt}
                  <p class="text-sm text-muted">{item.excerpt.slice(0, 180)}{item.excerpt.length > 180 ? "..." : ""}</p>
                {/if}
              </ContentCard>
            {/each}
          </div>
        </section>
      {/if}

      {#if totalResults === 0}
        <div class="surface-shell p-8 text-center">
          <h2 class="mb-2 text-2xl">No results found</h2>
          <p class="text-muted">Try a shorter phrase, broadening type filters, or removing author/work filters.</p>
        </div>
      {/if}
    {:else}
      <div class="surface-shell p-8 text-center">
        <h2 class="mb-2 text-2xl">Start with a search query</h2>
        <p class="text-muted">Results update as you type. The latest request always wins, and older requests are cancelled.</p>
      </div>
    {/if}
  </div>
</section>
