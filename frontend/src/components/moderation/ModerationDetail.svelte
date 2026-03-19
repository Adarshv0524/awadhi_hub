<script>
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  export let submissionId;

  let submission = null;
  let loading = true;
  let error = null;
  let saving = false;
  let actionInProgress = false;
  let contributor = null;
  
  // Moderation notes
  let moderatorNote = "";
  let showRejectModal = false;
  let rejectNote = "";

  let edit = {
    main_text: "",
    meaning: "",
    author_slug: "",
    work_slug: "",
    chapter_slug: "",
    number_in_chapter: null,
    is_classical: false,
  };

  const log = (...args) => import.meta.env.DEV && console.debug("[MOD-DETAIL]", ...args);

  async function load() {
    loading = true;
    error = null;
    try {
      submission = await api(`/moderation/submissions/${submissionId}`);
      edit = {
        main_text: submission.main_text || "",
        meaning: submission.meaning || "",
        author_slug: submission.author_slug || "",
        work_slug: submission.work_slug || "",
        chapter_slug: submission.chapter_slug || "",
        number_in_chapter: submission.number_in_chapter || null,
        is_classical: submission.is_classical || false,
      };

      // Load contributor info (best-effort, try public endpoint first)
      if (submission.contributor_id) {
        try {
          contributor = await api(`/users/${submission.contributor_id}`);
        } catch (e) {
          log("failed to load contributor via /users, trying /admin/users", e);
          try {
            const arr = await api(`/admin/users?ids=${submission.contributor_id}`);
            contributor = Array.isArray(arr) && arr[0] ? arr[0] : null;
          } catch (e2) {
            log("fallback contributor fetch failed", e2);
            // Set placeholder with just the ID
            contributor = { id: submission.contributor_id, username: null, email: null };
          }
        }
      }

    } catch (e) {
      error = e?.message || "Failed to load submission";
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(load);

  async function saveChanges() {
    saving = true;
    try {
      const body = {
        main_text: edit.main_text,
        meaning: edit.meaning,
        author_slug: edit.author_slug || null,
        work_slug: edit.work_slug || null,
        chapter_slug: edit.chapter_slug || null,
        number_in_chapter: edit.number_in_chapter,
        is_classical: edit.is_classical,
        expectedVersion: submission.version,
      };
      const res = await api(`/submissions/${submissionId}`, {
        method: "PUT",
        body,
      });
      submission = res;
      // Update edit state with returned data
      edit = {
        main_text: submission.main_text || "",
        meaning: submission.meaning || "",
        author_slug: submission.author_slug || "",
        work_slug: submission.work_slug || "",
        chapter_slug: submission.chapter_slug || "",
        number_in_chapter: submission.number_in_chapter || null,
        is_classical: submission.is_classical || false,
      };
      alert("Changes saved successfully!");
    } catch (e) {
      alert("Save failed: " + (e.message || e));
      console.error(e);
    } finally {
      saving = false;
    }
  }

  async function approve(guideline_version = "v1") {
    if (!confirm("Approve this submission?")) return;
    actionInProgress = true;
    try {
      const note = moderatorNote.trim() || "Approved by moderator UI";
      const res = await api(`/moderation/submissions/${submissionId}/approve`, {
        method: "POST",
        body: { note, guideline_version },
      });
      submission = res;
      moderatorNote = ""; // Clear note after approval
      alert("Approved successfully!");
    } catch (e) {
      alert("Approve failed: " + (e.message || e));
      console.error(e);
    } finally {
      actionInProgress = false;
    }
  }

  function openRejectModal() {
    showRejectModal = true;
    rejectNote = moderatorNote.trim() || "";
  }

  function closeRejectModal() {
    showRejectModal = false;
    rejectNote = "";
  }

  async function confirmReject() {
    if (!rejectNote.trim()) {
      alert("Rejection note is required");
      return;
    }
    actionInProgress = true;
    showRejectModal = false;
    try {
      const res = await api(`/moderation/submissions/${submissionId}/reject`, {
        method: "POST",
        body: { note: rejectNote.trim() },
      });
      submission = res;
      moderatorNote = ""; // Clear note after rejection
      alert("Rejected successfully!");
    } catch (e) {
      alert("Reject failed: " + (e.message || e));
      console.error(e);
    } finally {
      actionInProgress = false;
      rejectNote = "";
    }
  }
</script>

{#if loading}
  <p>Loading submission…</p>
{:else if error}
  <p class="text-red-600">{error}</p>
{:else}
  <div class="space-y-6">
    <div class="flex justify-between items-start gap-4 mb-4">
      <div>
        <h2 class="text-xl font-semibold">Submission #{submission.id} — {submission.content_type}</h2>
        <p class="text-sm text-stone-600">
          Contributor:
          {#if contributor}
            <a href={`/admin/users/${contributor.id}`} class="underline">{contributor.username ?? contributor.email}</a>
          {:else}
            {submission.contributor_id ?? "—"}
          {/if}
          • Status: {submission.status} • Version: {submission.version}
        </p>
      </div>
      <div class="flex gap-2">
        <button class="px-3 py-1 border rounded" on:click={load}>Reload</button>
        <button class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700" on:click={() => approve("v1")} disabled={actionInProgress}>Approve</button>
        <button class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700" on:click={openRejectModal} disabled={actionInProgress}>Reject</button>
      </div>
    </div>

    <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
      <label class="block">
        <div class="text-sm font-semibold mb-2 text-blue-900">📝 Moderator Notes / Comments</div>
        <textarea
          rows="3"
          bind:value={moderatorNote}
          class="w-full border border-blue-300 p-3 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Add notes for approval or rejection (e.g., 'Fixed typo in meaning', 'Needs citation', etc.)"
        ></textarea>
        <p class="text-xs text-stone-600 mt-1">
          💡 These notes will be saved with your approval/rejection decision and visible in moderation logs.
        </p>
      </label>
    </div>

    <div class="space-y-3">
      <label class="block">
        <div class="text-sm mb-1">Main Text</div>
        <textarea rows="6" bind:value={edit.main_text} class="w-full border p-2 rounded"></textarea>
      </label>

      <label class="block">
        <div class="text-sm mb-1">Meaning</div>
        <textarea rows="4" bind:value={edit.meaning} class="w-full border p-2 rounded"></textarea>
      </label>

      {#if submission.external_references}
        <div class="border-t pt-3 mt-3">
          <h3 class="text-sm font-semibold mb-2">External References ({submission.content_type} specific data)</h3>
          <pre class="bg-gray-100 p-3 rounded text-xs overflow-auto max-h-60">{JSON.stringify(submission.external_references, null, 2)}</pre>
        </div>
      {/if}

      <div class="grid grid-cols-2 gap-3">
        <label class="block">
          <div class="text-sm mb-1">Author slug</div>
          <input class="w-full border p-2 rounded" bind:value={edit.author_slug} />
        </label>

        <label class="block">
          <div class="text-sm mb-1">Work slug</div>
          <input class="w-full border p-2 rounded" bind:value={edit.work_slug} />
        </label>

        <label class="block">
          <div class="text-sm mb-1">Chapter slug</div>
          <input class="w-full border p-2 rounded" bind:value={edit.chapter_slug} />
        </label>

        <label class="block">
          <div class="text-sm mb-1">Number in chapter</div>
          <input type="number" class="w-full border p-2 rounded" bind:value={edit.number_in_chapter} />
        </label>
      </div>

      <div class="flex gap-2">
        <button class="px-3 py-1 bg-blue-600 text-white rounded" on:click={saveChanges} disabled={saving}>Save</button>
        <button class="px-3 py-1 border rounded" on:click={() => (window.location.href = "/moderation")}>Back to queue</button>
      </div>
    </div>
  </div>
{/if}

<!-- Rejection Modal -->
{#if showRejectModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" on:click={closeRejectModal}>
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6" on:click|stopPropagation>
      <h3 class="text-xl font-semibold mb-4 text-red-600">Reject Submission</h3>
      
      <p class="text-sm text-stone-600 mb-4">
        Please provide a clear reason for rejection. This will help the contributor improve their submission.
      </p>
      
      <label class="block mb-4">
        <div class="text-sm font-medium mb-2">Rejection Reason *</div>
        <textarea 
          rows="5" 
          bind:value={rejectNote} 
          class="w-full border border-stone-300 p-3 rounded focus:outline-none focus:ring-2 focus:ring-red-500" 
          placeholder="E.g., 'Translation is incomplete', 'Source citation needed', 'Contains inappropriate content', etc."
          autofocus
        ></textarea>
      </label>
      
      <div class="flex gap-3">
        <button 
          class="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium" 
          on:click={confirmReject}
          disabled={!rejectNote.trim()}
        >
          Confirm Reject
        </button>
        <button 
          class="px-4 py-2 border border-stone-300 rounded hover:bg-stone-50" 
          on:click={closeRejectModal}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}
