<!-- src/components/submission/SubmissionForm.svelte -->
<script lang="ts">
  import { onMount, onDestroy } from "svelte";

  export let apiBase: string = "";

  type Author = { id: number; slug: string; name: string };
  type Work = { id: number; slug: string; title: string };
  type Chapter = { id: number; slug: string; title: string };

  let authors: Author[] = [];
  let works: Work[] = [];
  let chapters: Chapter[] = [];

  let user: any = null;

  let content_type = "doha";
  
  // Common fields
  let main_text = "";
  let meaning = "";
  
  // Dictionary-specific
  let lemma_devanagari = "";
  let lemma_roman = "";
  
  // Idiom-specific
  // Technical note (MED-003): Idiom submission contract is now aligned end-to-end.
  // Frontend captures Romanized text and passes it in external_references.text_roman.
  // Moderation canonicalization maps this into idiom_entries.text_roman during approval.
  // See Architecture.md Section 3.4 "Submission and Moderation Alignment" for details.
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
  
  // Draft safety features
  let hasUnsavedChanges = false;
  let lastSaved: Date | null = null;
  let saveStatus: "idle" | "saving" | "saved" = "idle";
  let formStartTime: Date = new Date();
  
  // LocalStorage cache key
  const CACHE_KEY = "awadhi_submission_draft";
  
  // Track initial state for unsaved changes detection
  let initialFormState = "";
  
  function getFormState() {
    return JSON.stringify({
      content_type,
      main_text,
      meaning,
      lemma_devanagari,
      lemma_roman,
      usage_example,
      idiom_text_roman,
      title,
      content,
      excerpt,
      selected_author_slug,
      free_author_name,
      selected_work_slug,
      selected_chapter_slug,
      number_in_chapter,
      external_refs,
      visibility
    });
  }
  
  function checkUnsavedChanges() {
    const currentState = getFormState();
    hasUnsavedChanges = currentState !== initialFormState && (
      main_text.trim() !== "" ||
      meaning.trim() !== "" ||
      lemma_devanagari.trim() !== "" ||
      lemma_roman.trim() !== "" ||
      usage_example.trim() !== "" ||
      idiom_text_roman.trim() !== "" ||
      title.trim() !== "" ||
      content.trim() !== "" ||
      excerpt.trim() !== ""
    );
  }
  
  // Save to localStorage
  function saveToCache() {
    if (typeof window === "undefined") return;
    
    try {
      const formData = {
        content_type,
        main_text,
        meaning,
        lemma_devanagari,
        lemma_roman,
        usage_example,
        idiom_text_roman,
        title,
        content,
        excerpt,
        is_classical,
        selected_author_slug,
        free_author_name,
        selected_work_slug,
        selected_chapter_slug,
        number_in_chapter,
        external_refs,
        visibility,
        saved_at: new Date().toISOString()
      };
      
      localStorage.setItem(CACHE_KEY, JSON.stringify(formData));
      lastSaved = new Date();
      saveStatus = "saved";
      
      // Reset status after 2 seconds
      setTimeout(() => {
        if (saveStatus === "saved") saveStatus = "idle";
      }, 2000);
    } catch (e) {
      console.error("Failed to save to cache:", e);
    }
  }
  
  // Restore from localStorage
  function restoreFromCache() {
    if (typeof window === "undefined") return;
    
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (!cached) return;
      
      const data = JSON.parse(cached);
      
      // Restore all fields
      content_type = data.content_type || "doha";
      main_text = data.main_text || "";
      meaning = data.meaning || "";
      lemma_devanagari = data.lemma_devanagari || "";
      lemma_roman = data.lemma_roman || "";
      usage_example = data.usage_example || "";
      idiom_text_roman = data.idiom_text_roman || "";
      title = data.title || "";
      content = data.content || "";
      excerpt = data.excerpt || "";
      is_classical = data.is_classical || false;
      selected_author_slug = data.selected_author_slug || "";
      free_author_name = data.free_author_name || "";
      selected_work_slug = data.selected_work_slug || "";
      selected_chapter_slug = data.selected_chapter_slug || "";
      number_in_chapter = data.number_in_chapter || null;
      external_refs = data.external_refs || "";
      visibility = data.visibility || "private";
      
      console.log("Restored draft from cache");
    } catch (e) {
      console.error("Failed to restore from cache:", e);
    }
  }
  
  // Clear cache
  function clearCache() {
    if (typeof window === "undefined") return;
    
    try {
      localStorage.removeItem(CACHE_KEY);
      lastSaved = null;
      saveStatus = "idle";
    } catch (e) {
      console.error("Failed to clear cache:", e);
    }
  }
  
  // Debounced cache save
  let cacheTimer: any = null;
  function scheduleCacheSave() {
    if (cacheTimer) clearTimeout(cacheTimer);
    saveStatus = "saving";
    cacheTimer = setTimeout(() => {
      saveToCache();
    }, 1000); // Save after 1 second of inactivity
  }
  
  function buildPayload(submitForReview: boolean, timeSpent?: number) {
    const parsedExternalReferences = external_refs ? JSON.parse(external_refs) : {};
    const payload: any = {
      content_type,
      submit_for_review: submitForReview,
      visibility,
    };
    
    // Add time tracking
    if (timeSpent !== undefined) {
      payload.time_spent_seconds = timeSpent;
    }
    
    // Type-specific fields
    if (content_type === "dictionary") {
      payload.lemma_devanagari = lemma_devanagari || null;
      payload.lemma_roman = lemma_roman || null;
      payload.main_text = lemma_devanagari || lemma_roman || null; // Fallback
      payload.meaning = meaning || null;
    } else if (content_type === "idiom") {
      payload.main_text = main_text || null;
      payload.meaning = meaning || null;
      payload.usage_example = usage_example || null;
      payload.external_references = {
        ...parsedExternalReferences,
        text_devanagari: main_text || null,
        text_roman: idiom_text_roman || null,
        meaning: meaning || null,
        examples: usage_example ? [usage_example] : null,
      };
    } else if (content_type === "article") {
      payload.title = title || null;
      payload.main_text = content || null;
      payload.meaning = excerpt || null;
    } else if (content_type === "doha") {
      payload.main_text = main_text || null;
      payload.meaning = meaning || null;
    }
    
    // Common metadata
    payload.is_classical = Boolean(is_classical);
    payload.author_slug = selected_author_slug || (free_author_name || null);
    payload.work_slug = selected_work_slug || null;
    payload.chapter_slug = selected_chapter_slug || null;
    payload.number_in_chapter = number_in_chapter || null;
    if (content_type !== "idiom") {
      payload.external_references = Object.keys(parsedExternalReferences).length ? parsedExternalReferences : null;
    }
    
    // Clean up null values
    Object.keys(payload).forEach(k => payload[k] == null && delete payload[k]);
    
    return payload;
  }

  function authHeader(): string | null {
    try {
      if (typeof window === "undefined") return null;
      const t = window.localStorage.getItem("awadhi_access_token");
      return t ? `Bearer ${t}` : null;
    } catch {
      return null;
    }
  }

  async function safeFetch(path: string, opts: RequestInit = {}) {
    const url = apiBase && apiBase.length ? `${apiBase}${path}` : path;
    const headers = new Headers(opts.headers as HeadersInit | undefined);
    if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
    const bearer = authHeader();
    if (bearer) headers.set("Authorization", bearer);

    const finalOpts: RequestInit = {
      ...opts,
      credentials: "include",
      headers,
    };
    const r = await fetch(url, finalOpts);
    const ct = r.headers.get("content-type") || "";
    const payload = ct.includes("application/json") ? await r.json() : await r.text();
    if (!r.ok) {
      const err = new Error("Request failed");
      (err as any).status = r.status;
      (err as any).payload = payload;
      throw err;
    }
    return payload;
  }

  onMount(async () => {
    try {
      // check auth client-side
      try {
        user = await safeFetch("/auth/me", { method: "GET" });
      } catch (e: any) {
        // not logged in - redirect to /login
        if (e?.status === 401) {
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
          return;
        }
      }

      // fetch authors list
      try {
        authors = await safeFetch("/authors");
      } catch (e) {
        console.warn("Could not fetch authors", e);
        authors = [];
      }
      
      // Initialize form state tracking
      initialFormState = getFormState();
      formStartTime = new Date();
      
      // Restore from cache if available
      restoreFromCache();
      
      // Update initial state after restoration
      initialFormState = getFormState();
      
      // Setup beforeunload warning for unsaved changes (browser only)
      if (typeof window !== "undefined") {
        window.addEventListener("beforeunload", handleBeforeUnload);
      }
    } catch (e) {
      console.error("Init error", e);
      error = "Unable to initialize submission form.";
    }
  });
  
  onDestroy(() => {
    if (cacheTimer) clearTimeout(cacheTimer);
    if (typeof window !== "undefined") {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    }
  });
  
  function handleBeforeUnload(e: BeforeUnloadEvent) {
    if (hasUnsavedChanges && saveStatus !== "saving") {
      e.preventDefault();
      e.returnValue = "You have unsaved changes. Are you sure you want to leave?";
      return e.returnValue;
    }
  }
  
  function handleInput() {
    checkUnsavedChanges();
    if (hasUnsavedChanges) {
      scheduleCacheSave();
    }
  }
  
  function handleTypeChange() {
    // Clear type-specific fields when switching types
    if (content_type === "dictionary") {
      main_text = "";
      usage_example = "";
      idiom_text_roman = "";
      title = "";
      content = "";
      excerpt = "";
    } else if (content_type === "idiom") {
      lemma_devanagari = "";
      lemma_roman = "";
      title = "";
      content = "";
      excerpt = "";
    } else if (content_type === "article") {
      lemma_devanagari = "";
      lemma_roman = "";
      main_text = "";
      usage_example = "";
      idiom_text_roman = "";
    } else if (content_type === "doha") {
      lemma_devanagari = "";
      lemma_roman = "";
      usage_example = "";
      idiom_text_roman = "";
      title = "";
      content = "";
      excerpt = "";
    }
    
    checkUnsavedChanges();
  }

  async function onAuthorChange(e: Event) {
    selected_work_slug = "";
    selected_chapter_slug = "";
    works = [];
    chapters = [];
    const val = (e.target as HTMLSelectElement).value;
    selected_author_slug = val;
    if (!val) return;
    try {
      works = await safeFetch(`/authors/${encodeURIComponent(val)}/works`);
    } catch (e) {
      console.warn("Works fetch failed", e);
      works = [];
    }
  }

  async function onWorkChange(e: Event) {
    selected_chapter_slug = "";
    chapters = [];
    const val = (e.target as HTMLSelectElement).value;
    selected_work_slug = val;
    if (!val || !selected_author_slug) return;
    try {
      chapters = await safeFetch(`/authors/${encodeURIComponent(selected_author_slug)}/works/${encodeURIComponent(val)}/chapters`);
    } catch (e) {
      console.warn("Chapters fetch failed", e);
      chapters = [];
    }
  }

  function resetMessages() {
    message = "";
    error = "";
  }

  async function submitSubmission(action: "draft" | "submit") {
    resetMessages();
    submitting = true;
    try {
      const timeSpent = Math.floor((new Date().getTime() - formStartTime.getTime()) / 1000);
      const submit_for_review = action === "submit";
      const payload = buildPayload(submit_for_review, timeSpent);

      const res = await safeFetch("/submissions", { 
        method: "POST", 
        body: JSON.stringify(payload) 
      });
      
      const statusLabel = submit_for_review ? "pending review" : "draft";
      message = `Successfully ${action === "draft" ? "saved as draft" : "submitted for review"} (ID: ${res?.id ?? "(no id)"})`;
      
      // Clear form and cache after successful submission (not draft)
      if (action === "submit") {
        clearForm();
        clearCache();
        formStartTime = new Date();
      }
      
      initialFormState = getFormState();
      hasUnsavedChanges = false;
      saveStatus = "idle";
    } catch (e: any) {
      console.error("submit error", e);
      if (e?.status === 401) {
        error = "You must be logged in to submit. Redirecting to login...";
        if (typeof window !== "undefined") {
          setTimeout(() => window.location.href = "/login", 1200);
        }
      } else {
        try {
          error = (typeof e.payload === "string") ? e.payload : JSON.stringify(e.payload);
        } catch {
          error = "Submission failed.";
        }
      }
    } finally {
      submitting = false;
    }
  }
  
  function clearForm() {
    main_text = "";
    meaning = "";
    lemma_devanagari = "";
    lemma_roman = "";
    usage_example = "";
    idiom_text_roman = "";
    title = "";
    content = "";
    excerpt = "";
    is_classical = false;
    selected_author_slug = "";
    free_author_name = "";
    selected_work_slug = "";
    selected_chapter_slug = "";
    number_in_chapter = null;
    external_refs = "";
  }
</script>

<style>
  .field { margin-bottom: 1rem; }
  textarea { min-height: 100px; resize: vertical; }
  .small { font-size:0.9rem;color:#94a3b8 }
  .btn { padding: 10px 16px; border-radius:8px; cursor:pointer; font-weight: 500; transition: all 0.2s; }
  .btn-primary { background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%); color:#fff; border:0; }
  .btn-primary:hover:not(:disabled) { background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3); }
  .btn-ghost { background:transparent; border:1px solid #475569; color:#e2e8f0; }
  .btn-ghost:hover:not(:disabled) { background:#334155; border-color:#64748b; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  
  .autosave-indicator {
    position: sticky;
    top: 20px;
    z-index: 10;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 16px;
    transition: all 0.3s;
  }
  
  .autosave-idle { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }
  .autosave-saving { background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
  .autosave-saved { background: #14532d; color: #86efac; border: 1px solid #22c55e; }
  
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .unsaved-warning {
    background: #7c2d12;
    color: #fed7aa;
    border: 1px solid #ea580c;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .form-section {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
  }
  
  .form-section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #38bdf8;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #334155;
  }
  
  input, select, textarea {
    background: #0f172a;
    border: 1px solid #334155;
    color: #e2e8f0;
    padding: 10px 12px;
    border-radius: 6px;
    width: 100%;
    transition: border-color 0.2s;
  }
  
  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #0ea5e9;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
  }
  
  label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: #cbd5e1;
  }
</style>

{#if error}
  <div style="background:#fee2e2;color:#991b1b;padding:12px;border-radius:8px;margin-bottom:12px;border:1px solid #dc2626">
    <strong>Error:</strong> {error}
  </div>
{/if}

{#if message}
  <div style="background:#d1fae5;color:#065f46;padding:12px;border-radius:8px;margin-bottom:12px;border:1px solid #10b981">
    <strong>Success:</strong> {message}
  </div>
{/if}

<!-- Autosave Indicator -->
{#if saveStatus !== "idle"}
  <div class="autosave-indicator autosave-{saveStatus}">
    {#if saveStatus === "saving"}
      <div class="spinner"></div>
      <span>Saving...</span>
    {:else if saveStatus === "saved"}
      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
        <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
      </svg>
      <span>Saved locally {lastSaved ? "at " + lastSaved.toLocaleTimeString() : ""}</span>
    {/if}
  </div>
{/if}

<!-- Unsaved Changes Warning -->
{#if hasUnsavedChanges && saveStatus === "idle"}
  <div class="unsaved-warning">
    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
      <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
    </svg>
    <span>You have unsaved changes. Changes auto-save locally every few seconds.</span>
  </div>
{/if}

<!-- Submission Type Selector -->
<div class="form-section">
  <div class="field">
    <label for="submission-type">Content Type</label>
    <select id="submission-type" bind:value={content_type} on:change={handleTypeChange}>
      <option value="doha">Doha (दोहा)</option>
      <option value="dictionary">Dictionary Entry (शब्दकोश)</option>
      <option value="idiom">Idiom/Proverb (मुहावरा)</option>
      <option value="article">Article (लेख)</option>
    </select>
    <p class="small" style="margin-top:6px">
      {#if content_type === "doha"}
        Submit a traditional Awadhi doha (couplet) with meaning
      {:else if content_type === "dictionary"}
        Add a word or phrase to the Awadhi dictionary
      {:else if content_type === "idiom"}
        Contribute an Awadhi idiom, saying, or proverb
      {:else if content_type === "article"}
        Write an article about Awadhi language or culture
      {/if}
    </p>
  </div>
</div>

<!-- Type-Specific Fields -->
<div class="form-section">
  <h3 class="form-section-title">
    {#if content_type === "doha"}
      Doha Content
    {:else if content_type === "dictionary"}
      Dictionary Entry
    {:else if content_type === "idiom"}
      Idiom Details
    {:else if content_type === "article"}
      Article Content
    {/if}
  </h3>

  {#if content_type === "doha"}
    <div class="field">
      <label for="main-text">Doha Text (Devanagari) <span style="color:#ef4444">*</span></label>
      <textarea 
        id="main-text" 
        bind:value={main_text} 
        on:input={handleInput}
        required
        placeholder="Enter the doha in Devanagari script..."
      ></textarea>
    </div>

    <div class="field">
      <label for="meaning">Meaning / Translation</label>
      <textarea 
        id="meaning" 
        bind:value={meaning}
        on:input={handleInput}
        placeholder="Explain the meaning in Hindi or English..."
      ></textarea>
    </div>
    
  {:else if content_type === "dictionary"}
    <div class="field">
      <label for="lemma-devanagari">Word (Devanagari) <span style="color:#ef4444">*</span></label>
      <input 
        id="lemma-devanagari" 
        type="text"
        bind:value={lemma_devanagari}
        on:input={handleInput}
        required
        placeholder="शब्द (in Devanagari)"
      />
    </div>

    <div class="field">
      <label for="lemma-roman">Word (Roman Script)</label>
      <input 
        id="lemma-roman" 
        type="text"
        bind:value={lemma_roman}
        on:input={handleInput}
        placeholder="shabd (in Roman script)"
      />
    </div>

    <div class="field">
      <label for="meaning">Meaning / Definition <span style="color:#ef4444">*</span></label>
      <textarea 
        id="meaning" 
        bind:value={meaning}
        on:input={handleInput}
        required
        placeholder="Provide the meaning or definition..."
      ></textarea>
    </div>
    
  {:else if content_type === "idiom"}
    <div class="field">
      <label for="main-text">Idiom/Proverb Text <span style="color:#ef4444">*</span></label>
      <input 
        id="main-text" 
        type="text"
        bind:value={main_text}
        on:input={handleInput}
        required
        placeholder="Enter the idiom or proverb..."
      />
    </div>

    <div class="field">
      <label for="idiom-text-roman">Romanized Text <span style="color:#ef4444">*</span></label>
      <input
        id="idiom-text-roman"
        type="text"
        bind:value={idiom_text_roman}
        on:input={handleInput}
        required
        placeholder="e.g., andhon mein kana raja"
      />
    </div>

    <div class="field">
      <label for="meaning">Meaning <span style="color:#ef4444">*</span></label>
      <textarea 
        id="meaning" 
        bind:value={meaning}
        on:input={handleInput}
        required
        placeholder="Explain what this idiom means..."
      ></textarea>
    </div>

    <div class="field">
      <label for="usage-example">Usage Example</label>
      <textarea 
        id="usage-example" 
        bind:value={usage_example}
        on:input={handleInput}
        placeholder="Show how this idiom is used in a sentence..."
      ></textarea>
    </div>
    
  {:else if content_type === "article"}
    <div class="field">
      <label for="title">Article Title <span style="color:#ef4444">*</span></label>
      <input 
        id="title" 
        type="text"
        bind:value={title}
        on:input={handleInput}
        required
        placeholder="Enter a descriptive title..."
      />
    </div>

    <div class="field">
      <label for="excerpt">Excerpt / Summary</label>
      <textarea 
        id="excerpt" 
        bind:value={excerpt}
        on:input={handleInput}
        style="min-height: 80px"
        placeholder="Brief summary or excerpt (optional)..."
      ></textarea>
    </div>

    <div class="field">
      <label for="content">Article Content <span style="color:#ef4444">*</span></label>
      <textarea 
        id="content" 
        bind:value={content}
        on:input={handleInput}
        style="min-height: 200px"
        required
        placeholder="Write your article content here..."
      ></textarea>
    </div>
  {/if}
</div>

<!-- Metadata Section (Optional) -->
<div class="form-section">
  <h3 class="form-section-title">Metadata (Optional)</h3>

  <div class="field">
    <label for="is-classical">
      <input 
        id="is-classical" 
        type="checkbox" 
        bind:checked={is_classical}
        on:change={handleInput}
        style="width: auto; margin-right: 8px"
      />
      This is classical/historical content
    </label>
  </div>

  <div class="field">
    <label for="author-slug">Classical Author</label>
    <select 
      id="author-slug" 
      on:change={onAuthorChange} 
      bind:value={selected_author_slug}
    >
      <option value="">— Select classical author (optional) —</option>
      {#each authors as a}
        <option value={a.slug}>{a.name}</option>
      {/each}
    </select>
    <p class="small" style="margin-top:6px">Or enter author name manually:</p>
  </div>

  <div class="field">
    <label for="author-free">Author Name (Free Text)</label>
    <input 
      id="author-free" 
      type="text" 
      bind:value={free_author_name}
      on:input={handleInput}
      placeholder="e.g., Tulsidas, Kabir"
    />
  </div>

  {#if works.length > 0}
    <div class="field">
      <label for="work-slug">Work</label>
      <select id="work-slug" on:change={onWorkChange} bind:value={selected_work_slug}>
        <option value="">— Select work (optional) —</option>
        {#each works as w}
          <option value={w.slug}>{w.title}</option>
        {/each}
      </select>
    </div>
  {/if}

  {#if chapters.length > 0}
    <div class="field">
      <label for="chapter-slug">Chapter</label>
      <select id="chapter-slug" bind:value={selected_chapter_slug} on:change={handleInput}>
        <option value="">— Select chapter (optional) —</option>
        {#each chapters as c}
          <option value={c.slug}>{c.title}</option>
        {/each}
      </select>
    </div>
  {/if}

  <div class="field">
    <label for="number-in-chapter">Number in Chapter</label>
    <input 
      id="number-in-chapter" 
      type="number" 
      bind:value={number_in_chapter}
      on:input={handleInput}
      placeholder="e.g., 1, 2, 3..."
    />
  </div>

  <div class="field">
    <label for="external-refs">External References (JSON)</label>
    <textarea 
      id="external-refs" 
      bind:value={external_refs}
      on:input={handleInput}
      style="min-height: 60px; font-family: monospace; font-size: 0.85rem"
      placeholder='&#123;"source":"book","urn":"..."&#125;'
    ></textarea>
    <p class="small" style="margin-top:6px">Advanced: Provide external references in JSON format</p>
  </div>

  <div class="field">
    <label for="visibility">Visibility</label>
    <select id="visibility" bind:value={visibility} on:change={handleInput}>
      <option value="private">Private (only visible to you and moderators)</option>
      <option value="public">Public (visible to everyone after approval)</option>
    </select>
  </div>
</div>

<!-- Action Buttons -->
<div style="display:flex; gap:12px; margin-top:24px; flex-wrap: wrap;">
  <button 
    class="btn btn-primary" 
    on:click|preventDefault={() => submitSubmission("submit")} 
    disabled={submitting}
    style="flex: 1; min-width: 180px"
  >
    {submitting ? "Submitting..." : "Submit for Review"}
  </button>
  <button 
    class="btn btn-ghost" 
    on:click|preventDefault={() => submitSubmission("draft")} 
    disabled={submitting}
    style="flex: 1; min-width: 180px"
  >
    {submitting ? "Saving..." : "Save as Draft"}
  </button>
</div>

<div style="margin-top:16px; font-size:0.9rem; color:#94a3b8; text-align: center;">
  {#if user}
    Submitting as <strong style="color:#38bdf8">{user.username ?? user.email}</strong>
  {:else}
    <em>Not logged in.</em>
  {/if}
</div>

<div style="margin-top:12px; font-size:0.85rem; color:#64748b; text-align: center;">
  <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16" style="display: inline; margin-right: 4px">
    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
    <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
  </svg>
  Fields marked with <span style="color:#ef4444">*</span> are required. Your work auto-saves as you type.
</div>
