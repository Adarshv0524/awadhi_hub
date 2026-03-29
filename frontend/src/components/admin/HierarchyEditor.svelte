<script>
  export let apiBase = "";
  import { onMount } from "svelte";
  let authors = [];
  let works = [];
  let chapters = [];
  let error = "";
  let activeAuthorId = null;

  function getAuthHeader() {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("awadhi_access_token") : null;
      return token ? { Authorization: `Bearer ${token}` } : {};
    } catch {
      return {};
    }
  }

  let newAuthor = { slug: "", name: "", language: "", short_bio: "" };
  let newWork = { author_id: null, slug: "", title: "", description: "" };
  let newChapter = { work_id: null, slug: "", title: "", number: 1 };
  let selectedAuthorForWorks = null; // track which author's works are shown
  let selectedWorkForChapters = null; // track which work's chapters are shown
  
  // Edit states
  let editingAuthor = null;
  let editingWork = null;
  let editingChapter = null;

  async function loadAuthors() {
    error = "";
    try {
      // Use public endpoint for listing (backend max limit is 100)
      const res = await fetch(`${apiBase}/authors?limit=100`, { headers: { ...getAuthHeader() }});
      if (!res.ok) {
        const errText = await res.text().catch(() => res.statusText);
        throw new Error(`Failed to load authors: ${res.status} ${errText}`);
      }
      authors = await res.json();
      if (import.meta.env.DEV) console.log("[HierarchyEditor] Loaded authors:", authors.length);
    } catch (e) {
      error = String(e);
      console.error("[HierarchyEditor] loadAuthors error:", e);
    }
  }

  async function loadWorks(authorSlug) {
    activeAuthorId = authorSlug;
    works = [];
    chapters = [];
    try {
      // Use public endpoint /authors/{slug}/works for listing (backend max limit is 50)
      const res = await fetch(`${apiBase}/authors/${authorSlug}/works?limit=50`, { headers: { ...getAuthHeader() }});
      if (!res.ok) throw new Error("Failed to load works");
      works = await res.json();
    } catch (e) { error = String(e); }
  }

  async function createAuthor() {
    try {
      const res = await fetch(`${apiBase}/admin/hierarchy/authors`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify(newAuthor)
      });
      if (!res.ok) throw new Error("Create failed");
      await loadAuthors();
      newAuthor = { slug: "", name: "", language: "", short_bio: "" };
    } catch (e) { alert("Create author failed: " + e); }
  }

  async function createWork() {
    if (!newWork.author_id) { alert("Pick an author first"); return; }
    try {
      const res = await fetch(`${apiBase}/admin/hierarchy/authors/${newWork.author_id}/works`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({ slug: newWork.slug, title: newWork.title, description: newWork.description })
      });
      if (!res.ok) throw new Error("Create work failed");
      // Reload works for the selected author (need to find slug from authors array)
      const author = authors.find(a => a.id === newWork.author_id);
      if (author) await loadWorks(author.slug);
      newWork = { author_id: null, slug: "", title: "", description: "" };
    } catch (e) { alert(e); }
  }

  async function createChapter() {
    if (!newChapter.work_id) { alert("Pick a work first"); return; }
    try {
      const res = await fetch(`${apiBase}/admin/hierarchy/works/${newChapter.work_id}/chapters`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({ slug: newChapter.slug, title: newChapter.title, number: newChapter.number })
      });
      if (!res.ok) throw new Error("Create chapter failed");
      // reload chapters (need author+work slugs from state)
      if (selectedAuthorForWorks && selectedWorkForChapters) {
        const author = authors.find(a => a.id === selectedAuthorForWorks);
        const work = works.find(w => w.id === newChapter.work_id);
        if (author && work) await loadChapters(author.slug, work.slug);
      }
      newChapter = { work_id: null, slug: "", title: "", number: 1 };
    } catch (e) { alert(e); }
  }

  async function loadChapters(authorSlug, workSlug) {
    chapters = [];
    try {
      // Use public endpoint /authors/{author}/works/{work}/chapters for listing
      const res = await fetch(`${apiBase}/authors/${authorSlug}/works/${workSlug}/chapters?limit=200`, { headers: { ...getAuthHeader() }});
      if (!res.ok) throw new Error("Failed to load chapters");
      chapters = await res.json();
    } catch (e) { error = String(e); }
  }

  async function updateAuthor(authorId) {
    if (!editingAuthor) return;
    const previousAuthors = [...authors];
    const patch = { ...editingAuthor };
    authors = authors.map((a) => (a.id === authorId ? { ...a, ...patch } : a));
    editingAuthor = null;
    try {
      const res = await fetch(`${apiBase}/admin/hierarchy/authors/${authorId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify(patch)
      });
      if (!res.ok) throw new Error("Update failed");
      const updated = await res.json();
      authors = authors.map((a) => (a.id === authorId ? { ...a, ...updated } : a));
    } catch (e) {
      authors = previousAuthors;
      alert("Update author failed: " + e);
    }
  }

  async function updateWork(workId) {
    if (!editingWork) return;
    const previousWorks = [...works];
    const patch = { ...editingWork };
    works = works.map((w) => (w.id === workId ? { ...w, ...patch } : w));
    editingWork = null;
    try {
      const res = await fetch(`${apiBase}/admin/hierarchy/works/${workId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify(patch)
      });
      if (!res.ok) throw new Error("Update failed");
      const updated = await res.json();
      works = works.map((w) => (w.id === workId ? { ...w, ...updated } : w));
    } catch (e) {
      works = previousWorks;
      alert("Update work failed: " + e);
    }
  }

  async function updateChapter(chapterId) {
    if (!editingChapter) return;
    const previousChapters = [...chapters];
    const patch = { ...editingChapter };
    chapters = chapters.map((c) => (c.id === chapterId ? { ...c, ...patch } : c));
    editingChapter = null;
    try {
      const res = await fetch(`${apiBase}/admin/hierarchy/chapters/${chapterId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify(patch)
      });
      if (!res.ok) throw new Error("Update failed");
      const updated = await res.json();
      chapters = chapters.map((c) => (c.id === chapterId ? { ...c, ...updated } : c));
    } catch (e) {
      chapters = previousChapters;
      alert("Update chapter failed: " + e);
    }
  }

  onMount(loadAuthors);
</script>

{#if error}<p class="admin-state-bad">{error}</p>{/if}

<section class="grid gap-4 md:grid-cols-3">
  <div class="admin-panel p-3">
    <h3 class="font-semibold">Create Author</h3>
    <input placeholder="slug" bind:value={newAuthor.slug} class="w-full mt-2 p-2 border rounded" />
    <input placeholder="name" bind:value={newAuthor.name} class="w-full mt-2 p-2 border rounded" />
    <input placeholder="language (optional)" bind:value={newAuthor.language} class="w-full mt-2 p-2 border rounded" />
    <input placeholder="short bio (optional)" bind:value={newAuthor.short_bio} class="w-full mt-2 p-2 border rounded" />
    <button class="mt-3 admin-btn admin-btn-primary" on:click={createAuthor}>Create</button>
  </div>

  <div class="admin-panel p-3">
    <h3 class="font-semibold">Create Work</h3>
    <select bind:value={newWork.author_id} class="w-full p-2 border rounded mt-2">
      <option value={null}>Pick author</option>
      {#each authors as a}
        <option value={a.id}>{a.name}</option>
      {/each}
    </select>
    <input placeholder="slug" bind:value={newWork.slug} class="w-full mt-2 p-2 border rounded" />
    <input placeholder="title" bind:value={newWork.title} class="w-full mt-2 p-2 border rounded" />
    <input placeholder="description (optional)" bind:value={newWork.description} class="w-full mt-2 p-2 border rounded" />
    <button class="mt-3 admin-btn admin-btn-primary" on:click={createWork}>Create</button>
  </div>

  <div class="admin-panel p-3">
    <h3 class="font-semibold">Create Chapter</h3>
    <select bind:value={newChapter.work_id} class="w-full p-2 border rounded mt-2" on:change={() => loadChapters(newChapter.work_id)}>
      <option value={null}>Pick work</option>
      {#each works as w}
        <option value={w.id}>{w.title ?? w.slug}</option>
      {/each}
    </select>
    <input placeholder="slug" bind:value={newChapter.slug} class="w-full mt-2 p-2 border rounded" />
    <input placeholder="title" bind:value={newChapter.title} class="w-full mt-2 p-2 border rounded" />
    <input type="number" placeholder="number" bind:value={newChapter.number} class="w-full mt-2 p-2 border rounded" />
    <button class="mt-3 admin-btn admin-btn-primary" on:click={createChapter}>Create</button>
  </div>
</section>

<section class="mt-6">
  <h4 class="font-semibold mb-3">Authors</h4>
  <ul class="space-y-2">
    {#each authors as a}
      <li class="admin-panel p-3">
        <div class="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-start">
          <div class="flex-1">
            {#if editingAuthor?.id === a.id}
              <input bind:value={editingAuthor.name} class="w-full p-2 border rounded mb-2" placeholder="Name" />
              <input bind:value={editingAuthor.slug} class="w-full p-2 border rounded mb-2" placeholder="Slug" />
              <input bind:value={editingAuthor.language} class="w-full p-2 border rounded mb-2" placeholder="Language" />
              <input bind:value={editingAuthor.short_bio} class="w-full p-2 border rounded" placeholder="Short bio" />
            {:else}
              <div class="font-medium text-lg">{a.name} <span class="text-sm text-slate-400">({a.slug})</span></div>
              {#if a.short_bio}<div class="text-sm text-slate-300 mt-1">{a.short_bio}</div>{/if}
              {#if a.language}<div class="text-xs text-slate-400 mt-1">Language: {a.language}</div>{/if}
            {/if}
          </div>
          <div class="flex flex-wrap gap-2">
            {#if editingAuthor?.id === a.id}
              <button on:click={() => updateAuthor(a.id)} class="admin-btn admin-btn-primary">Save</button>
              <button on:click={() => editingAuthor = null} class="admin-btn">Cancel</button>
            {:else}
              <button on:click={() => editingAuthor = { ...a }} class="admin-btn">Edit</button>
              <button on:click={() => { selectedAuthorForWorks = a.id; loadWorks(a.slug); }} class="admin-btn">
                View Works
              </button>
            {/if}
          </div>
        </div>
        
        {#if selectedAuthorForWorks === a.id && works.length > 0}
          <div class="mt-4 ml-4 pl-4 border-l-2">
            <h5 class="text-sm font-semibold mb-2">Works for {a.name}</h5>
            <ul class="space-y-2">
              {#each works as w}
                <li class="p-2 bg-slate-900/55 rounded border border-slate-700">
                  <div class="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-start">
                    <div class="flex-1">
                      {#if editingWork?.id === w.id}
                        <input bind:value={editingWork.title} class="w-full p-2 border rounded mb-2" placeholder="Title" />
                        <input bind:value={editingWork.slug} class="w-full p-2 border rounded mb-2" placeholder="Slug" />
                        <input bind:value={editingWork.description} class="w-full p-2 border rounded" placeholder="Description" />
                      {:else}
                        <div class="font-medium">{w.title} <span class="text-xs text-slate-400">({w.slug})</span></div>
                        {#if w.description}<div class="text-xs text-slate-300 mt-1">{w.description}</div>{/if}
                      {/if}
                    </div>
                    <div class="flex flex-wrap gap-2">
                      {#if editingWork?.id === w.id}
                        <button on:click={() => updateWork(w.id)} class="admin-btn admin-btn-primary">Save</button>
                        <button on:click={() => editingWork = null} class="admin-btn">Cancel</button>
                      {:else}
                        <button on:click={() => editingWork = { ...w }} class="admin-btn">Edit</button>
                        <button on:click={() => { selectedWorkForChapters = w.id; loadChapters(a.slug, w.slug); }} class="admin-btn">
                          View Chapters
                        </button>
                      {/if}
                    </div>
                  </div>
                  
                  {#if selectedWorkForChapters === w.id && chapters.length > 0}
                    <div class="mt-3 ml-3 pl-3 border-l">
                      <h6 class="text-xs font-semibold mb-2">Chapters for {w.title}</h6>
                      <ul class="space-y-1">
                        {#each chapters as c}
                          <li class="text-xs p-2 bg-slate-900/75 border border-slate-700 rounded">
                            {#if editingChapter?.id === c.id}
                              <div class="space-y-2">
                                <input bind:value={editingChapter.title} class="w-full p-1 border rounded text-xs" placeholder="Title" />
                                <input bind:value={editingChapter.slug} class="w-full p-1 border rounded text-xs" placeholder="Slug" />
                                <input type="number" bind:value={editingChapter.number} class="w-full p-1 border rounded text-xs" placeholder="Number" />
                                <div class="flex gap-2 mt-2">
                                  <button on:click={() => updateChapter(c.id)} class="admin-btn admin-btn-primary">Save</button>
                                  <button on:click={() => editingChapter = null} class="admin-btn">Cancel</button>
                                </div>
                              </div>
                            {:else}
                              <div class="flex flex-col gap-2 sm:flex-row sm:justify-between sm:items-center">
                                <div>
                                  <span class="font-medium">Ch {c.number}:</span> {c.title} <span class="text-slate-400">({c.slug})</span>
                                </div>
                                <button on:click={() => editingChapter = { ...c }} class="admin-btn">Edit</button>
                              </div>
                            {/if}
                          </li>
                        {/each}
                      </ul>
                    </div>
                  {/if}
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </li>
    {/each}
  </ul>
</section>
