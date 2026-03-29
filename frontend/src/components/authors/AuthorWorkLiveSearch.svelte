<script lang="ts">
  import { onMount } from "svelte";

  import { API_BASE } from "../../lib/api";
  import Button from "../ui/Button.svelte";

  type Author = {
    id: number;
    slug: string;
    name: string;
    short_bio?: string | null;
    language?: string | null;
  };

  type Work = {
    id: number;
    slug: string;
    title: string;
    work_type?: string | null;
    poetry_nodes_count?: number;
    author_slug: string;
    author_name: string;
  };

  export let initialAuthors: Author[] = [];

  let query = "";
  let loading = false;
  let fetchError = "";
  let authors: Author[] = [...initialAuthors];
  let works: Work[] = [];

  let debounceId: ReturnType<typeof setTimeout> | null = null;
  let activeController: AbortController | null = null;
  let requestVersion = 0;

  function scoreMatch(value: string, q: string): number {
    const a = value.toLowerCase();
    const b = q.toLowerCase();
    if (a === b) return 100;
    if (a.startsWith(b)) return 80;
    if (a.includes(b)) return 60;
    return 0;
  }

  async function fetchJson<T>(path: string, signal: AbortSignal): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  }

  function sortAuthorsByCloseness(items: Author[], q: string): Author[] {
    const queryText = q.trim().toLowerCase();
    if (!queryText) return items;

    return [...items].sort((left, right) => {
      const leftScore = scoreMatch(left.name, queryText) + scoreMatch(left.slug, queryText);
      const rightScore = scoreMatch(right.name, queryText) + scoreMatch(right.slug, queryText);
      if (leftScore !== rightScore) return rightScore - leftScore;
      return left.name.localeCompare(right.name);
    });
  }

  function sortWorksByCloseness(items: Work[], q: string): Work[] {
    const queryText = q.trim().toLowerCase();
    if (!queryText) return items;

    return [...items].sort((left, right) => {
      const leftScore =
        scoreMatch(left.title, queryText) +
        scoreMatch(left.author_name, queryText) +
        scoreMatch(left.slug, queryText);
      const rightScore =
        scoreMatch(right.title, queryText) +
        scoreMatch(right.author_name, queryText) +
        scoreMatch(right.slug, queryText);
      if (leftScore !== rightScore) return rightScore - leftScore;
      return left.title.localeCompare(right.title);
    });
  }

  async function performSearch() {
    const q = query.trim();
    fetchError = "";

    if (!q) {
      authors = [...initialAuthors];
      works = [];
      loading = false;
      activeController?.abort();
      return;
    }

    loading = true;
    activeController?.abort();
    activeController = new AbortController();
    const myVersion = ++requestVersion;

    const authorPath = `/authors?q=${encodeURIComponent(q)}&limit=40`;
    const workPath = `/authors/works/search?q=${encodeURIComponent(q)}&limit=40`;

    const settled = await Promise.allSettled([
      fetchJson<Author[]>(authorPath, activeController.signal),
      fetchJson<Work[]>(workPath, activeController.signal),
    ]);

    if (myVersion !== requestVersion || activeController.signal.aborted) return;

    const nextAuthors = settled[0].status === "fulfilled" ? settled[0].value : [];
    const nextWorks = settled[1].status === "fulfilled" ? settled[1].value : [];

    if (settled[0].status === "rejected" && settled[1].status === "rejected") {
      fetchError = "Live search is temporarily unavailable.";
    }

    authors = sortAuthorsByCloseness(nextAuthors, q);
    works = sortWorksByCloseness(nextWorks, q);
    loading = false;
  }

  function queueSearch() {
    if (debounceId) clearTimeout(debounceId);
    debounceId = setTimeout(() => {
      performSearch();
    }, 280);
  }

  function clearSearch() {
    query = "";
    fetchError = "";
    authors = [...initialAuthors];
    works = [];
  }

  onMount(() => {
    return () => {
      if (debounceId) clearTimeout(debounceId);
      activeController?.abort();
    };
  });

  $: queueSearch(), query;
</script>

<section class="mb-7 rounded-xl border border-slate-700 bg-slate-900/45 p-4 md:p-5">
  <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <div>
      <h2 class="text-lg font-semibold text-slate-100">Find Authors or Works</h2>
      <p class="text-sm text-slate-400">Results update live as you type, including closest author and work matches.</p>
    </div>
    {#if query.trim()}
      <Button type="button" size="sm" variant="ghost" on:click={clearSearch}>Clear</Button>
    {/if}
  </div>

  <label class="mt-4 block">
    <span class="sr-only">Search authors and works</span>
    <input
      type="search"
      bind:value={query}
      placeholder="Search by author name, slug, or work title"
      class="w-full rounded-lg border border-slate-600 bg-slate-950/70 px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:border-cyan-400 focus:outline-none"
      aria-label="Search authors and works"
      autocomplete="off"
    />
  </label>

  {#if loading}
    <p class="mt-3 text-sm text-slate-400" aria-live="polite">Searching...</p>
  {/if}

  {#if fetchError}
    <p class="mt-3 rounded-md border border-amber-400/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-200" role="status">
      {fetchError}
    </p>
  {/if}
</section>

{#if query.trim()}
  <section class="grid gap-6 lg:grid-cols-2" aria-live="polite">
    <div>
      <h3 class="mb-3 text-base font-semibold uppercase tracking-[0.15em] text-cyan-300">Authors ({authors.length})</h3>
      {#if authors.length === 0}
        <p class="rounded-lg border border-slate-700 bg-slate-900/35 p-4 text-sm text-slate-400">No author matches yet.</p>
      {:else}
        <div class="space-y-3">
          {#each authors as author}
            <a
              href={`/${author.slug}`}
              class="group block rounded-xl border border-slate-700 bg-slate-900/45 p-4 transition-all hover:-translate-y-0.5 hover:border-cyan-400/50 hover:bg-slate-800/60"
            >
              <p class="text-base font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">{author.name}</p>
              <p class="mt-1 text-xs uppercase tracking-[0.18em] text-slate-500">{author.language ?? "Awadhi"} poet</p>
              <p class="mt-2 text-sm text-slate-300 line-clamp-2">{author.short_bio || "Open profile to browse works and poetry."}</p>
            </a>
          {/each}
        </div>
      {/if}
    </div>

    <div>
      <h3 class="mb-3 text-base font-semibold uppercase tracking-[0.15em] text-indigo-300">Works ({works.length})</h3>
      {#if works.length === 0}
        <p class="rounded-lg border border-slate-700 bg-slate-900/35 p-4 text-sm text-slate-400">No work matches yet.</p>
      {:else}
        <div class="space-y-3">
          {#each works as work}
            <a
              href={`/${work.author_slug}/${work.slug}`}
              class="group block rounded-xl border border-slate-700 bg-slate-900/45 p-4 transition-all hover:-translate-y-0.5 hover:border-indigo-400/50 hover:bg-slate-800/60"
            >
              <p class="text-base font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors">{work.title}</p>
              <p class="mt-1 text-sm text-slate-400">by {work.author_name}</p>
              <p class="mt-2 text-xs uppercase tracking-[0.16em] text-slate-500">
                {work.work_type ?? "text"} · {work.poetry_nodes_count ?? 0} nodes
              </p>
            </a>
          {/each}
        </div>
      {/if}
    </div>
  </section>
{:else}
  <section class="grid gap-4 sm:grid-cols-2">
    {#each initialAuthors as author}
      <a
        href={`/${author.slug}`}
        class="group rounded-xl border border-slate-700 bg-slate-900/45 p-5 transition-all hover:-translate-y-0.5 hover:border-cyan-400/50 hover:bg-slate-800/60"
      >
        <h3 class="text-lg font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">{author.name}</h3>
        <p class="text-xs uppercase tracking-[0.18em] text-slate-400 mt-1">{author.language ?? "Awadhi"} poet</p>
        <p class="text-sm text-slate-300 mt-3 line-clamp-3">{author.short_bio || "Open profile to view works, chapters, and curated texts."}</p>
        <p class="text-sm text-cyan-300 mt-4">View profile →</p>
      </a>
    {/each}
  </section>
{/if}
