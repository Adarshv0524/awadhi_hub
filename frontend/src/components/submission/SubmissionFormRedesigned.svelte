<!-- src/components/submission/SubmissionFormRedesigned.svelte -->
<!-- Minimal, mobile-first contribution form with progressive disclosure -->
<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { validateSubmissionPayload } from "../../lib/submissionValidation";

  export let apiBase: string = "";

  const API_V1_PREFIX = "/api/v1";

  function resolvedApiBase(): string {
    return (apiBase || "").replace(/\/$/, "").replace(/\/api\/v1$/, "");
  }

  function apiUrl(path: string): string {
    const normalized = path.startsWith("/") ? path : `/${path}`;
    const v1Path =
      normalized === API_V1_PREFIX || normalized.startsWith(`${API_V1_PREFIX}/`)
        ? normalized
        : `${API_V1_PREFIX}${normalized}`;
    return `${resolvedApiBase()}${v1Path}`;
  }

  function authHeaders(includeJson = false): Record<string, string> {
    const headers: Record<string, string> = {};
    if (includeJson) headers["Content-Type"] = "application/json";
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("awadhi_access_token");
      if (token) headers.Authorization = `Bearer ${token}`;
    }
    return headers;
  }

  // Types
  type Author = { id: number; slug: string; name: string };
  type Work = { id: number; slug: string; title: string };
  type Chapter = { id: number; slug: string; title: string; number: number };
  type PoetryTypeOption = {
    poetry_type: string;
    display_name: string;
    family?: string | null;
    is_user_defined?: boolean;
    is_active?: boolean;
  };

  // State
  let authors: Author[] = [];
  let works: Work[] = [];
  let chapters: Chapter[] = [];
  let user: any = null;

  // Content type
  let content_type = "";
  const LEGACY_TYPES = ["dictionary", "idiom", "article"];
  let poetryTypes: PoetryTypeOption[] = [];
  let allContentTypes: any[] = []; // Combined poetry + legacy types for rendering

  // Main content fields
  let main_text = "";
  let meaning = "";

  // Dictionary-specific
  let lemma_devanagari = "";
  let lemma_roman = "";
  type DictionarySenseInput = {
    definition: string;
    pos: string;
    example: string;
  };
  let dictionarySenses: DictionarySenseInput[] = [
    { definition: "", pos: "", example: "" },
  ];

  // Idiom-specific
  let idiom_text_roman = "";
  let usage_example = "";

  // Article-specific
  let title = "";
  let content = "";
  let excerpt = "";

  // Classical hierarchy metadata (collapsible)
  let is_classical = false;
  let selected_author_slug = "";
  let free_author_name = "";
  let selected_work_slug = "";
  let selected_chapter_slug = "";
  let number_in_chapter: number | null = null;
  let external_refs = "";
  let visibility = "private";

  // UI state
  let submitting = false;
  let message = "";
  let error = "";
  let showMetadata = false;
  let lastAutosave: Date | null = null;
  let autosaveTimeout: ReturnType<typeof setTimeout> | null = null;

  // LocalStorage cache
  const CACHE_KEY = "awadhi_submission_draft";

  $: isPoetryType = !LEGACY_TYPES.includes(content_type);
  $: activePoetryOption = poetryTypes.find((t) => t.poetry_type === content_type) ?? null;

  // ===== LIFECYCLE =====
  onMount(async () => {
    // Fetch current user
    try {
      const userResponse = await fetch(apiUrl("/auth/me"), {
        headers: authHeaders(),
        credentials: "include",
      });
      if (userResponse.ok) {
        user = await userResponse.json();
      }
    } catch (e) {
      console.error("Failed to fetch user:", e);
    }

    // Fetch poetry types
    try {
      const typesResponse = await fetch(apiUrl("/poetry/types"), {
        credentials: "include",
      });
      if (typesResponse.ok) {
        const types = await typesResponse.json();
        poetryTypes = Array.isArray(types) ? types : [];
        
        // Set default to first active poetry type
        const defaultType = poetryTypes.find((t) => t.is_active !== false);
        if (defaultType) {
          content_type = defaultType.poetry_type;
        } else if (poetryTypes.length > 0) {
          content_type = poetryTypes[0].poetry_type;
        } else {
          content_type = "dictionary";
        }
        
        // Build combined type list for rendering
        allContentTypes = [
          ...poetryTypes.map((t) => ({ value: t.poetry_type, label: t.display_name, isPoetry: true })),
          { value: "dictionary", label: "शब्दकोश (Dictionary)", isPoetry: false },
          { value: "idiom", label: "मुहावरा (Idiom)", isPoetry: false },
          { value: "article", label: "लेख (Article)", isPoetry: false },
        ];
      }
    } catch (e) {
      console.error("Failed to fetch poetry types:", e);
      // Fallback: start with dictionary if types can't be fetched
      content_type = "dictionary";
      allContentTypes = [
        { value: "dictionary", label: "शब्दकोश (Dictionary)", isPoetry: false },
        { value: "idiom", label: "मुहावरा (Idiom)", isPoetry: false },
        { value: "article", label: "लेख (Article)", isPoetry: false },
      ];
    }

    // Fetch classical authors
    try {
      const authorsResponse = await fetch(apiUrl("/authors?limit=100"), {
        headers: authHeaders(),
        credentials: "include",
      });
      if (authorsResponse.ok) {
        const data = await authorsResponse.json();
        authors = Array.isArray(data) ? data : data.results || [];
      }
    } catch (e) {
      console.error("Failed to fetch authors:", e);
    }

    // Restore draft from cache
    restoreFromCache();
  });

  onDestroy(() => {
    if (autosaveTimeout) clearTimeout(autosaveTimeout);
  });

  // ===== AUTOSAVE / CACHE =====
  function scheduleAutosave() {
    if (autosaveTimeout) clearTimeout(autosaveTimeout);
    autosaveTimeout = setTimeout(() => {
      saveToCache();
      lastAutosave = new Date();
    }, 1500); // Micro autosave after 1.5s inactivity
  }

  function saveToCache() {
    if (typeof window === "undefined") return;
    try {
      const formData = {
        content_type,
        main_text,
        meaning,
        lemma_devanagari,
        lemma_roman,
        dictionarySenses,
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
        visibility,
      };
      localStorage.setItem(CACHE_KEY, JSON.stringify(formData));
    } catch (e) {
      console.error("Failed to cache form:", e);
    }
  }

  function restoreFromCache() {
    if (typeof window === "undefined") return;
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (!cached) return;

      const data = JSON.parse(cached);
      content_type = data.content_type || content_type;
      main_text = data.main_text || "";
      meaning = data.meaning || "";
      lemma_devanagari = data.lemma_devanagari || "";
      lemma_roman = data.lemma_roman || "";
      dictionarySenses = data.dictionarySenses || dictionarySenses;
      usage_example = data.usage_example || "";
      idiom_text_roman = data.idiom_text_roman || "";
      title = data.title || "";
      content = data.content || "";
      excerpt = data.excerpt || "";
      is_classical = data.is_classical || false;
      selected_author_slug = data.selected_author_slug || "";
      free_author_name = data.free_author_name || "";
      visibility = data.visibility || "private";
    } catch (e) {
      console.error("Failed to restore cache:", e);
    }
  }

  function clearCache() {
    if (typeof window !== "undefined") {
      localStorage.removeItem(CACHE_KEY);
    }
  }

  // ===== EVENT HANDLERS =====
  function handleInput() {
    scheduleAutosave();
  }

  async function onAuthorChange() {
    if (!selected_author_slug) {
      works = [];
      chapters = [];
      selected_work_slug = "";
      selected_chapter_slug = "";
      return;
    }

    try {
      const res = await fetch(
        apiUrl(`/authors/${selected_author_slug}/works?limit=100`),
        { headers: authHeaders(), credentials: "include" }
      );
      if (res.ok) {
        const data = await res.json();
        works = Array.isArray(data) ? data : data.results || [];
      }
    } catch (e) {
      console.error("Failed to fetch works:", e);
    }
  }

  async function onWorkChange() {
    if (!selected_author_slug || !selected_work_slug) {
      chapters = [];
      selected_chapter_slug = "";
      return;
    }

    try {
      const res = await fetch(
        apiUrl(`/authors/${selected_author_slug}/works/${selected_work_slug}/chapters?limit=100`),
        { headers: authHeaders(), credentials: "include" }
      );
      if (res.ok) {
        const data = await res.json();
        chapters = Array.isArray(data) ? data : data.results || [];
      }
    } catch (e) {
      console.error("Failed to fetch chapters:", e);
    }
  }

  function handleTypeChange() {
    // Clear type-specific fields when switching types
    main_text = "";
    meaning = "";
    lemma_devanagari = "";
    lemma_roman = "";
    dictionarySenses = [{ definition: "", pos: "", example: "" }];
    idiom_text_roman = "";
    usage_example = "";
    title = "";
    content = "";
    excerpt = "";
    showMetadata = false;
    scheduleAutosave();
  }

  function addSense() {
    dictionarySenses = [...dictionarySenses, { definition: "", pos: "", example: "" }];
    handleInput();
  }

  function removeSense(index: number) {
    dictionarySenses = dictionarySenses.filter((_, i) => i !== index);
    handleInput();
  }

  // ===== SUBMISSION =====
  async function submitSubmission(action: "submit" | "draft") {
    error = "";
    message = "";
    submitting = true;

    try {
      // Build payload based on content type
      let payload: any = {
        content_type,
        visibility,
        is_classical,
        submit_for_review: action === "submit",
        version: 1,
      };

      // Add type-specific fields
      if (isPoetryType) {
        payload.main_text = main_text;
        payload.meaning = meaning;
        payload.external_references = {
          poetry_type: content_type,
        };

        if (is_classical) {
          payload.author_slug = selected_author_slug || free_author_name || null;
          payload.work_slug = selected_work_slug || null;
          payload.chapter_slug = selected_chapter_slug || null;
          payload.number_in_chapter = number_in_chapter || null;
        }
      } else if (content_type === "dictionary") {
        payload.main_text = lemma_devanagari;
        payload.meaning = dictionarySenses[0]?.definition || "";
        payload.external_references = {
          lemma_devanagari,
          lemma_roman,
          senses: dictionarySenses.filter((s) => s.definition.trim()),
        };
        payload.author_slug = selected_author_slug || free_author_name || null;
      } else if (content_type === "idiom") {
        payload.main_text = main_text;
        payload.meaning = meaning;
        payload.external_references = {
          text_devanagari: main_text,
          text_roman: idiom_text_roman,
          meaning,
          examples: usage_example ? [usage_example] : [],
        };
        payload.author_slug = selected_author_slug || free_author_name || null;
      } else if (content_type === "article") {
        payload.main_text = content;
        payload.meaning = excerpt;
        payload.external_references = {
          title,
          body: content,
          excerpt,
        };
        payload.author_slug = selected_author_slug || free_author_name || null;
      }

      // Validate payload
      const validationError = validateSubmissionPayload(payload);
      if (validationError) {
        error = validationError;
        submitting = false;
        return;
      }

      // Submit to API
      const response = await fetch(apiUrl("/submissions"), {
        method: "POST",
        headers: authHeaders(true),
        credentials: "include",
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        error = errorData.detail || "Submission failed";
        submitting = false;
        return;
      }

      const result = await response.json();
      message = action === "submit" 
        ? "Submitted for review! Thank you for contributing."
        : "Draft saved successfully.";
      
      clearCache();
      
      // Reset form
      content_type = "doha";
      main_text = "";
      meaning = "";
      title = "";
      content = "";
      excerpt = "";
      lemma_devanagari = "";
      lemma_roman = "";
      dictionarySenses = [{ definition: "", pos: "", example: "" }];
      idiom_text_roman = "";
      usage_example = "";
      is_classical = false;
      selected_author_slug = "";
      free_author_name = "";

      // Auto-hide success message after 5 seconds
      setTimeout(() => {
        message = "";
      }, 5000);
    } catch (e: any) {
      error = e?.message || "An error occurred during submission";
    } finally {
      submitting = false;
    }
  }
</script>

<style>
  :global(body) {
    --color-primary: #10b981;
    --color-error: #ef4444;
    --color-text: #1e293b;
    --color-text-muted: #64748b;
    --color-border: #e2e8f0;
    --color-bg-light: #f8fafc;
  }

  .form-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
  }

  @media (max-width: 640px) {
    .form-container {
      padding: 0.5rem 0;
    }
  }

  .form-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    gap: 1rem;
  }

  .form-header h1 {
    font-size: 1.875rem;
    font-weight: 700;
    margin: 0;
  }

  @media (max-width: 640px) {
    .form-header {
      margin-bottom: 0.75rem;
      min-height: 1.5rem;
    }

    .form-header h1 {
      display: none;
    }
  }

  .autosave-badge {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .autosave-badge.active {
    color: var(--color-primary);
  }

  /* Messages */
  .message-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid;
    font-size: 0.95rem;
  }

  .message-box.success {
    background: #f0fdf4;
    color: #065f46;
    border-color: var(--color-primary);
  }

  .message-box.error {
    background: #fef2f2;
    color: #991b1b;
    border-color: var(--color-error);
  }

  /* Content type selector - Segmented Control */
  .content-type-section {
    margin-bottom: 1.5rem;
  }

  .content-type-section .section-label {
    display: block;
    font-weight: 500;
    margin-bottom: 0.75rem;
    color: #cbd5e1;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .type-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 0.625rem;
    padding: 0.4rem;
    -webkit-backdrop-filter: blur(10px);
  }

  .type-option {
    flex: 1;
    min-width: 100px;
    padding: 0.6rem 1rem;
    border: none;
    border-radius: 0.5rem;
    background: transparent;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    color: #cbd5e1;
    transition: all 0.3s ease;
    white-space: nowrap;
    position: relative;

    &:hover {
      color: #e2e8f0;
      background: rgba(71, 85, 105, 0.3);
    }

    &.active {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);
    }
  }

  @media (max-width: 640px) {
    .type-selector {
      flex-wrap: nowrap;
      overflow-x: auto;
      overflow-y: hidden;
      gap: 0.35rem;
      padding: 0.3rem;
      scrollbar-width: thin;
    }

    .type-option {
      flex: 0 0 auto;
      min-width: 92px;
      padding: 0.5rem 0.75rem;
      font-size: 0.8rem;
    }
  }

  .form-section {
    margin-bottom: 1.5rem;
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(8px);
    padding: 1.5rem;
    border-radius: 0.625rem;
    border: 1px solid rgba(148, 163, 184, 0.1);
    -webkit-backdrop-filter: blur(8px);
  }

  @media (max-width: 640px) {
    .form-section {
      margin-bottom: 0.9rem;
      padding: 1rem;
      border-radius: 0.55rem;
    }
  }

  .section-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #e2e8f0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .required-badge {
    color: var(--color-error);
    font-weight: 700;
  }

  .field {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
  }

  @media (max-width: 640px) {
    .field {
      margin-bottom: 1rem;
    }
  }

  .field:last-child {
    margin-bottom: 0;
  }

  .field label {
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: #cbd5e1;
    font-size: 0.95rem;
  }

  .field input,
  .field textarea,
  .field select {
    padding: 0.75rem;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.375rem;
    font-size: 1rem;
    font-family: inherit;
    transition: all 0.2s;
    background: rgba(15, 23, 42, 0.6);
    color: #e2e8f0;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);

    &::placeholder {
      color: #64748b;
    }

    &:focus {
      outline: none;
      border-color: rgba(16, 185, 129, 0.4);
      background: rgba(15, 23, 42, 0.8);
      box-shadow: 0 0 16px rgba(16, 185, 129, 0.15);
    }

    &:disabled {
      background: rgba(15, 23, 42, 0.3);
      color: #64748b;
    }
  }

  .field textarea {
    resize: vertical;
    min-height: 100px;

    @media (max-width: 640px) {
      min-height: 72px;
    }
  }

  /* Dictionary senses */
  .senses-container {
    margin: 1.5rem 0;
  }

  .sense-item {
    background: rgba(15, 23, 42, 0.4);
    padding: 1rem;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(148, 163, 184, 0.1);
  }

  .sense-item .field {
    margin-bottom: 1rem;
  }

  .sense-header {
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: var(--color-text);
    font-size: 0.95rem;
  }

  .sense-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
  }

  /* Metadata section - Collapsible */
  .metadata-toggle {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    background: none;
    border: none;
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text);
    padding: 0.75rem;
    margin: -0.75rem 0 1rem -0.75rem;
    transition: color 0.2s;

    &:hover {
      color: var(--color-primary);
    }
  }

  .metadata-toggle.open::before {
    content: "▼";
    display: inline-block;
    transition: transform 0.2s;
  }

  .metadata-toggle:not(.open)::before {
    content: "▶";
    display: inline-block;
  }

  .metadata-content {
    max-height: 500px;
    overflow: hidden;
    transition: all 0.3s ease-out;

    &.collapsed {
      max-height: 0;
      opacity: 0;
    }
  }

  /* Buttons */
  .button-group {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    flex-wrap: wrap;

    @media (max-width: 640px) {
      flex-direction: column;
      gap: 0.6rem;
      margin-top: 1rem;
    }
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.375rem;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    flex: 1;

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .btn-primary {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(16, 185, 129, 0.1) 100%);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.4) 0%, rgba(16, 185, 129, 0.2) 100%);
      border-color: rgba(16, 185, 129, 0.5);
      box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
      transform: translateY(-1px);
    }
  }

  .btn-ghost {
    background: rgba(71, 85, 105, 0.2);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.2);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);

    &:hover:not(:disabled) {
      background: rgba(71, 85, 105, 0.3);
      border-color: rgba(148, 163, 184, 0.3);
      color: #e2e8f0;
    }
  }

  .helper-text {
    font-size: 0.875rem;
    color: #94a3b8;
    margin-top: 0.375rem;
  }

  .user-info {
    font-size: 0.9rem;
    color: #94a3b8;
    text-align: center;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(148, 163, 184, 0.1);
  }

  .user-info strong {
    color: #10b981;
  }
</style>

<div class="form-container">
  <!-- Header -->
  <div class="form-header">
    <h1>Contribute to Awadhi</h1>
    <div class="autosave-badge" class:active={lastAutosave}>
      {#if lastAutosave}
        ✓ Saved
      {:else}
        💾
      {/if}
    </div>
  </div>

  <!-- Messages -->
  {#if message}
    <div class="message-box success">{message}</div>
  {/if}

  {#if error}
    <div class="message-box error">{error}</div>
  {/if}

  <!-- Content Type Selector -->
  <div class="form-section content-type-section">
    <div class="section-label">Content Type</div>
    <div class="type-selector">
      {#each allContentTypes as option}
        <button
          class="type-option"
          class:active={content_type === option.value}
          on:click={() => {
            content_type = option.value;
            handleTypeChange();
          }}
          type="button"
        >
          {option.label.split('(')[0].trim()}
        </button>
      {/each}
    </div>
  </div>

  <!-- Main Content Form -->
  <div class="form-section">
    <h2 class="section-title">
      {#if isPoetryType}
        {activePoetryOption?.display_name || "Poetry"} Content
      {:else if content_type === "dictionary"}
        Word Details
      {:else if content_type === "idiom"}
        Idiom Details
      {:else if content_type === "article"}
        Article Content
      {/if}
    </h2>

    <!-- Poetry Form -->
    {#if isPoetryType}
      <div class="field">
        <label for="poetry-text">
          Poetry Text <span class="required-badge">*</span>
        </label>
        <textarea
          id="poetry-text"
          bind:value={main_text}
          on:input={handleInput}
          required
          placeholder="Enter the poetry text in Devanagari script..."
        ></textarea>
      </div>

      <div class="field">
        <label for="poetry-meaning">Meaning / Translation</label>
        <textarea
          id="poetry-meaning"
          bind:value={meaning}
          on:input={handleInput}
          placeholder="Explain the meaning in Hindi or English (optional)..."
        ></textarea>
      </div>

    <!-- Dictionary Form -->
    {:else if content_type === "dictionary"}
      <div class="field">
        <label for="lemma-devanagari">
          Word (Devanagari) <span class="required-badge">*</span>
        </label>
        <input
          id="lemma-devanagari"
          type="text"
          bind:value={lemma_devanagari}
          on:input={handleInput}
          required
          placeholder="शब्द"
        />
      </div>

      <div class="field">
        <label for="lemma-roman">Word (Roman Script)</label>
        <input
          id="lemma-roman"
          type="text"
          bind:value={lemma_roman}
          on:input={handleInput}
          placeholder="shabd (optional)"
        />
      </div>

      <div class="senses-container">
        <div class="section-title">
          Meanings <span class="required-badge">*</span>
          <span class="helper-text" style="margin-left: auto; font-weight: 400; font-size: 0.875rem;">
            (At least one required)
          </span>
        </div>

        {#each dictionarySenses as sense, index}
          <div class="sense-item">
            <div class="sense-header">Meaning {index + 1}</div>

            <div class="field">
              <label for={`sense-def-${index}`}>
                Definition <span class="required-badge">*</span>
              </label>
              <textarea
                id={`sense-def-${index}`}
                bind:value={sense.definition}
                on:input={handleInput}
                placeholder="What does this word mean?"
                required
              ></textarea>
            </div>

            <div class="field">
              <label for={`sense-pos-${index}`}>Part of Speech</label>
              <input
                id={`sense-pos-${index}`}
                type="text"
                bind:value={sense.pos}
                on:input={handleInput}
                placeholder="e.g., noun, verb, adjective"
              />
              <div class="helper-text">Optional - helps categorize the word</div>
            </div>

            <div class="field">
              <label for={`sense-ex-${index}`}>Example Usage</label>
              <input
                id={`sense-ex-${index}`}
                type="text"
                bind:value={sense.example}
                on:input={handleInput}
                placeholder="Show an example sentence"
              />
            </div>

            <div class="sense-actions">
              <button
                class="btn btn-ghost"
                on:click={() => removeSense(index)}
                disabled={dictionarySenses.length <= 1}
              >
                Remove
              </button>
            </div>
          </div>
        {/each}

        <button class="btn btn-ghost" on:click={addSense}>
          + Add Another Meaning
        </button>
      </div>

    <!-- Idiom Form -->
    {:else if content_type === "idiom"}
      <div class="field">
        <label for="idiom-text">
          Idiom / Proverb (Devanagari) <span class="required-badge">*</span>
        </label>
        <input
          id="idiom-text"
          type="text"
          bind:value={main_text}
          on:input={handleInput}
          required
          placeholder="Enter the idiom in Devanagari..."
        />
      </div>

      <div class="field">
        <label for="idiom-roman">
          Romanized Form <span class="required-badge">*</span>
        </label>
        <input
          id="idiom-roman"
          type="text"
          bind:value={idiom_text_roman}
          on:input={handleInput}
          required
          placeholder="e.g., andu mein kana raja"
        />
      </div>

      <div class="field">
        <label for="idiom-meaning">
          Meaning <span class="required-badge">*</span>
        </label>
        <textarea
          id="idiom-meaning"
          bind:value={meaning}
          on:input={handleInput}
          required
          placeholder="What does this idiom mean?"
        ></textarea>
      </div>

      <div class="field">
        <label for="idiom-example">Usage Example</label>
        <textarea
          id="idiom-example"
          bind:value={usage_example}
          on:input={handleInput}
          placeholder="Show how this idiom is used in a sentence (optional)..."
        ></textarea>
      </div>

    <!-- Article Form -->
    {:else if content_type === "article"}
      <div class="field">
        <label for="article-title">
          Article Title <span class="required-badge">*</span>
        </label>
        <input
          id="article-title"
          type="text"
          bind:value={title}
          on:input={handleInput}
          required
          placeholder="Enter a clear, descriptive title..."
        />
      </div>

      <div class="field">
        <label for="article-excerpt">Brief Summary</label>
        <textarea
          id="article-excerpt"
          bind:value={excerpt}
          on:input={handleInput}
          placeholder="Short summary of your article (optional)..."
          style="min-height: 60px"
        ></textarea>
      </div>

      <div class="field">
        <label for="article-content">
          Article Content <span class="required-badge">*</span>
        </label>
        <textarea
          id="article-content"
          bind:value={content}
          on:input={handleInput}
          required
          placeholder="Write your article here..."
          style="min-height: 240px"
        ></textarea>
      </div>
    {/if}
  </div>

  <!-- Optional Metadata Section (Collapsible) -->
  <div class="form-section">
    <button
      class="metadata-toggle"
      class:open={showMetadata}
      on:click={() => (showMetadata = !showMetadata)}
    >
      Link to Classical Work
    </button>

    <div class="metadata-content" class:collapsed={!showMetadata}>
      <div class="field">
        <label>
          <input
            type="checkbox"
            bind:checked={is_classical}
            on:change={handleInput}
            style="margin-right: 0.5rem; width: auto"
          />
          <span>This is from a classical work</span>
        </label>
        <div class="helper-text">
          Check if this content is from a known classical author/work
        </div>
      </div>

      {#if is_classical}
        <div class="field">
          <label for="author-select">Author</label>
          <select
            id="author-select"
            on:change={onAuthorChange}
            bind:value={selected_author_slug}
          >
            <option value="">— Select author (optional) —</option>
            {#each authors as a}
              <option value={a.slug}>{a.name}</option>
            {/each}
          </select>
          <div class="helper-text">Or enter manually below</div>
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
            <label for="work-select">Work</label>
            <select
              id="work-select"
              on:change={onWorkChange}
              bind:value={selected_work_slug}
            >
              <option value="">— Select work —</option>
              {#each works as w}
                <option value={w.slug}>{w.title}</option>
              {/each}
            </select>
          </div>
        {/if}

        {#if chapters.length > 0}
          <div class="field">
            <label for="chapter-select">Chapter</label>
            <select
              id="chapter-select"
              bind:value={selected_chapter_slug}
              on:change={handleInput}
            >
              <option value="">— Select chapter —</option>
              {#each chapters as c}
                <option value={c.slug}>{c.title}</option>
              {/each}
            </select>
          </div>

          <div class="field">
            <label for="position">Position in Chapter</label>
            <input
              id="position"
              type="number"
              bind:value={number_in_chapter}
              on:input={handleInput}
              placeholder="e.g., 1, 2, 3..."
            />
          </div>
        {/if}
      {/if}

      <div class="field">
        <label for="visibility">Privacy</label>
        <select id="visibility" bind:value={visibility} on:change={handleInput}>
          <option value="private">Private (only you and moderators see this)</option>
          <option value="public">Public (visible to everyone after approval)</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Submit Buttons -->
  <div class="button-group">
    <button
      class="btn btn-primary"
      on:click={() => submitSubmission("submit")}
      disabled={submitting}
    >
      {submitting ? "Submitting..." : "Submit for Review"}
    </button>
    <button
      class="btn btn-ghost"
      on:click={() => submitSubmission("draft")}
      disabled={submitting}
    >
      {submitting ? "Saving..." : "Save as Draft"}
    </button>
  </div>

  <!-- User Info -->
  <div class="user-info">
    {#if user}
      Submitting as <strong>{user.username ?? user.email}</strong>
    {:else}
      <em>Not logged in</em>
    {/if}
  </div>
</div>
