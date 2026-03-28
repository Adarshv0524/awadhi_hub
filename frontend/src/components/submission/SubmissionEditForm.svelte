<!-- src/components/submission/SubmissionEditForm.svelte -->
<script lang="ts">
  import { onMount } from "svelte";

  export let submissionId: string;
  export let apiBase: string = "";

  type Author = { id: number; slug: string; name: string };
  type Work = { id: number; slug: string; title: string };
  type Chapter = { id: number; slug: string; title: string };

  let authors: Author[] = [];
  let works: Work[] = [];
  let chapters: Chapter[] = [];

  let user: any = null;
  let submission: any = null;
  let loading = true;
  let expectedVersion: number = 0;

  let content_type = "doha";
  
  // Common fields
  let main_text = "";
  let meaning = "";
  
  // Dictionary-specific
  let lemma_devanagari = "";
  let lemma_roman = "";
  
  // Idiom-specific
  let idiom_text_roman = "";
  let usage_example = "";
  
  // Article-specific
  let title = "";
  let content = "";
  let excerpt = "";
  
  // Metadata
  let is_classical = false;
  let selected_author_slug = "";
  let free_author_name = "";
  let selected_work_slug = "";
  let selected_chapter_slug = "";
  let number_in_chapter: number | null = null;
  let external_refs = "";
  let visibility = "private";

  let submitting = false;
  let message = "";
  let error = "";

  function parseExternalReferences(raw: unknown): Record<string, any> {
    if (!raw) return {};
    if (typeof raw === "object") return raw as Record<string, any>;
    if (typeof raw !== "string") return {};
    try {
      const parsed = JSON.parse(raw);
      return typeof parsed === "object" && parsed !== null ? parsed : {};
    } catch {
      return {};
    }
  }

  function getAuthHeader() {
    if (typeof window === "undefined") return {};
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function loadSubmission() {
    loading = true;
    error = "";
    try {
      const res = await fetch(`${apiBase}/submissions/${submissionId}`, {
        headers: getAuthHeader()
      });
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (!res.ok) throw new Error("Failed to load submission");
      submission = await res.json();
      expectedVersion = submission.version || 0;

      // Populate form fields
      content_type = submission.content_type;
      main_text = submission.main_text || "";
      meaning = submission.meaning || "";
      lemma_devanagari = submission.lemma_devanagari || "";
      lemma_roman = submission.lemma_roman || "";
      usage_example = submission.usage_example || "";
      const submissionExternalReferences = parseExternalReferences(submission.external_references);
      idiom_text_roman = String(submissionExternalReferences.text_roman || "");
      title = submission.title || "";
      content = submission.content || "";
      excerpt = submission.excerpt || "";
      is_classical = submission.is_classical || false;
      selected_author_slug = submission.author_slug || "";
      free_author_name = submission.free_author_name || "";
      selected_work_slug = submission.work_slug || "";
      selected_chapter_slug = submission.chapter_slug || "";
      number_in_chapter = submission.number_in_chapter;
      external_refs = submission.external_references
        ? JSON.stringify(submission.external_references, null, 2)
        : "";
      visibility = submission.visibility || "private";

      if (submission.author_slug) {
        await loadWorks(submission.author_slug);
        if (submission.work_slug) {
          await loadChapters(submission.author_slug, submission.work_slug);
        }
      }
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load submission";
    } finally {
      loading = false;
    }
  }

  async function loadAuthors() {
    try {
      const res = await fetch(`${apiBase}/authors`);
      if (!res.ok) throw new Error("Failed to load authors");
      authors = await res.json();
    } catch (e) {
      console.error("Failed to load authors:", e);
    }
  }

  async function loadWorks(authorSlug: string) {
    works = [];
    chapters = [];
    selected_work_slug = "";
    selected_chapter_slug = "";
    if (!authorSlug) return;
    
    try {
      const res = await fetch(`${apiBase}/authors/${authorSlug}/works`);
      if (!res.ok) throw new Error("Failed to load works");
      works = await res.json();
    } catch (e) {
      console.error("Failed to load works:", e);
    }
  }

  async function loadChapters(authorSlug: string, workSlug: string) {
    chapters = [];
    selected_chapter_slug = "";
    if (!workSlug || !authorSlug) return;
    
    try {
      const res = await fetch(`${apiBase}/authors/${authorSlug}/works/${workSlug}/chapters`);
      if (!res.ok) throw new Error("Failed to load chapters");
      chapters = await res.json();
    } catch (e) {
      console.error("Failed to load chapters:", e);
    }
  }

  async function updateSubmission() {
    submitting = true;
    message = "";
    error = "";

    const parsedExternalReferences = parseExternalReferences(external_refs);
    const payload: any = {
      content_type,
      main_text: main_text.trim(),
      meaning: meaning.trim(),
      is_classical,
      visibility,
      expected_version: expectedVersion,
    };

    if (content_type === "dictionary") {
      payload.lemma_devanagari = lemma_devanagari.trim();
      payload.lemma_roman = lemma_roman.trim();
    } else if (content_type === "idiom") {
      if (!idiom_text_roman.trim()) {
        error = "Romanized Text is required for idiom updates.";
        submitting = false;
        return;
      }
      payload.usage_example = usage_example.trim();
      payload.external_references = {
        ...parsedExternalReferences,
        text_devanagari: main_text.trim() || null,
        text_roman: idiom_text_roman.trim(),
        meaning: meaning.trim() || null,
        examples: usage_example.trim() ? [usage_example.trim()] : null,
      };
    } else if (content_type === "article") {
      payload.title = title.trim();
      payload.content = content.trim();
      payload.excerpt = excerpt.trim();
    }

    if (selected_author_slug) {
      payload.author_slug = selected_author_slug;
      payload.free_author_name = null;
    } else if (free_author_name.trim()) {
      payload.free_author_name = free_author_name.trim();
      payload.author_slug = null;
    }

    if (selected_work_slug) payload.work_slug = selected_work_slug;
    if (selected_chapter_slug) payload.chapter_slug = selected_chapter_slug;
    if (number_in_chapter !== null && number_in_chapter > 0) {
      payload.number_in_chapter = number_in_chapter;
    }
    if (content_type !== "idiom" && external_refs.trim()) {
      payload.external_references = parsedExternalReferences;
    }

    try {
      const res = await fetch(`${apiBase}/submissions/${submissionId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeader()
        },
        body: JSON.stringify(payload)
      });

      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }

      if (res.status === 409) {
        error = "Version conflict. Someone else may have edited this submission. Please refresh and try again.";
        submitting = false;
        return;
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Update failed");
      }

      const updated = await res.json();
      expectedVersion = updated.version || expectedVersion + 1;
      message = "Submission updated successfully!";
      
      setTimeout(() => {
        window.location.href = `/submissions/${submissionId}`;
      }, 1500);
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error";
    } finally {
      submitting = false;
    }
  }

  onMount(async () => {
    const userStr = localStorage.getItem("user");
    if (userStr) user = JSON.parse(userStr);
    if (!user) {
      window.location.href = "/login";
      return;
    }
    await loadAuthors();
    await loadSubmission();
  });
</script>

{#if loading}
  <div class="flex items-center justify-center py-12">
    <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
  </div>
{:else if error && !submission}
  <div class="bg-red-50 border border-red-200 text-red-800 p-4 rounded">
    {error}
  </div>
{:else}
  <form on:submit|preventDefault={updateSubmission} class="space-y-6">
    <div class="bg-blue-50 border border-blue-200 text-blue-800 p-4 rounded">
      <strong>Edit Mode:</strong> You are editing an existing submission. Changes will update the submission with optimistic locking.
    </div>

    {#if message}
      <div class="bg-green-50 border border-green-200 text-green-800 p-4 rounded">
        {message}
      </div>
    {/if}

    {#if error}
      <div class="bg-red-50 border border-red-200 text-red-800 p-4 rounded">
        {error}
      </div>
    {/if}

    <div>
      <label class="block font-medium mb-2">Content Type</label>
      <select bind:value={content_type} class="w-full p-2 border rounded" disabled>
        <option value="doha">Doha</option>
        <option value="dictionary">Dictionary Entry</option>
        <option value="idiom">Idiom/Saying</option>
        <option value="article">Article</option>
      </select>
      <p class="text-sm text-stone-600 mt-1">Content type cannot be changed when editing</p>
    </div>

    {#if content_type === "dictionary"}
      <div>
        <label class="block font-medium mb-2">Lemma (Devanagari) *</label>
        <input type="text" bind:value={lemma_devanagari} required class="w-full p-2 border rounded" placeholder="शब्द" />
      </div>
      <div>
        <label class="block font-medium mb-2">Lemma (Roman)</label>
        <input type="text" bind:value={lemma_roman} class="w-full p-2 border rounded" placeholder="shabd" />
      </div>
    {:else if content_type === "article"}
      <div>
        <label class="block font-medium mb-2">Title *</label>
        <input type="text" bind:value={title} required class="w-full p-2 border rounded" placeholder="Article title" />
      </div>
      <div>
        <label class="block font-medium mb-2">Excerpt</label>
        <textarea bind:value={excerpt} rows="3" class="w-full p-2 border rounded" placeholder="Brief summary"></textarea>
      </div>
    {/if}

    <div>
      <label class="block font-medium mb-2">Main Text *</label>
      <textarea bind:value={main_text} required rows="4" class="w-full p-2 border rounded" placeholder="Enter main text"></textarea>
    </div>

    <div>
      <label class="block font-medium mb-2">Meaning / Translation *</label>
      <textarea bind:value={meaning} required rows="4" class="w-full p-2 border rounded" placeholder="Enter meaning"></textarea>
    </div>

    {#if content_type === "idiom"}
      <div>
        <label for="idiom-text-roman" class="block font-medium mb-2">Romanized Text *</label>
        <input
          id="idiom-text-roman"
          type="text"
          bind:value={idiom_text_roman}
          required
          class="w-full p-2 border rounded"
          placeholder="e.g., andhon mein kana raja"
        />
      </div>
      <div>
        <label class="block font-medium mb-2">Usage Example</label>
        <textarea bind:value={usage_example} rows="3" class="w-full p-2 border rounded" placeholder="Example usage"></textarea>
      </div>
    {:else if content_type === "article"}
      <div>
        <label class="block font-medium mb-2">Content (Full article body)</label>
        <textarea bind:value={content} rows="8" class="w-full p-2 border rounded" placeholder="Full article content"></textarea>
      </div>
    {/if}

    <div class="flex items-center gap-2">
      <input type="checkbox" id="classical" bind:checked={is_classical} class="w-4 h-4" />
      <label for="classical" class="font-medium">Classical source</label>
    </div>

    {#if is_classical}
      <div>
        <label class="block font-medium mb-2">Author</label>
        <select bind:value={selected_author_slug} on:change={() => loadWorks(selected_author_slug)} class="w-full p-2 border rounded">
          <option value="">-- Select Author --</option>
          {#each authors as author}
            <option value={author.slug}>{author.name}</option>
          {/each}
        </select>
      </div>

      {#if selected_author_slug && works.length > 0}
        <div>
          <label class="block font-medium mb-2">Work</label>
          <select bind:value={selected_work_slug} on:change={() => loadChapters(selected_author_slug, selected_work_slug)} class="w-full p-2 border rounded">
            <option value="">-- Select Work --</option>
            {#each works as work}
              <option value={work.slug}>{work.title}</option>
            {/each}
          </select>
        </div>
      {/if}

      {#if selected_work_slug && chapters.length > 0}
        <div>
          <label class="block font-medium mb-2">Chapter</label>
          <select bind:value={selected_chapter_slug} class="w-full p-2 border rounded">
            <option value="">-- Select Chapter --</option>
            {#each chapters as chapter}
              <option value={chapter.slug}>{chapter.title}</option>
            {/each}
          </select>
        </div>
      {/if}

      <div>
        <label class="block font-medium mb-2">Number in Chapter</label>
        <input type="number" bind:value={number_in_chapter} min="1" class="w-full p-2 border rounded" placeholder="e.g., 1" />
      </div>
    {:else}
      <div>
        <label class="block font-medium mb-2">Author Name (Free-text)</label>
        <input type="text" bind:value={free_author_name} class="w-full p-2 border rounded" placeholder="e.g., Anonymous folk tradition" />
      </div>
    {/if}

    <div>
      <label class="block font-medium mb-2">External References</label>
      <textarea bind:value={external_refs} rows="2" class="w-full p-2 border rounded" placeholder="URLs, citations, etc."></textarea>
    </div>

    <div>
      <label class="block font-medium mb-2">Visibility</label>
      <select bind:value={visibility} class="w-full p-2 border rounded">
        <option value="private">Private (draft)</option>
        <option value="public">Public (submit for moderation)</option>
      </select>
    </div>

    <div class="flex gap-4">
      <button type="submit" disabled={submitting} class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
        {submitting ? "Updating..." : "Update Submission"}
      </button>
      <a href={`/submissions/${submissionId}`} class="px-6 py-2 border rounded hover:bg-stone-50">Cancel</a>
    </div>
  </form>
{/if}
