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
          contributor = await api(`/users/id/${submission.contributor_id}`);
        } catch (e) {
          log("failed to load contributor via /users/id, trying /admin/users", e);
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
        body: { note, guideline_version, approved_by_human: true },
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
        body: { note: rejectNote.trim(), approved_by_human: true },
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
    <div class="bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-lg p-5 mb-4">
      <div class="flex justify-between items-start gap-4">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2">
            <h2 class="text-2xl font-bold text-slate-900">Submission #{submission.id}</h2>
            <span class="px-3 py-1 bg-blue-100 text-blue-900 rounded-full text-xs font-semibold">{submission.content_type}</span>
            <span class="px-3 py-1 {submission.status === 'pending_review' ? 'bg-yellow-100 text-yellow-900' : 'bg-gray-100 text-gray-900'} rounded-full text-xs font-semibold">{submission.status}</span>
          </div>
          <p class="text-sm text-slate-700">
            <span class="font-semibold">Contributor:</span>
            {#if contributor}
              <a href={`/admin/users/${contributor.id}`} class="text-blue-600 hover:underline">{contributor.username ?? contributor.email ?? 'Unknown'}</a>
            {:else}
              <span class="text-slate-500">ID: {submission.contributor_id}</span>
            {/if}
            • <span class="font-semibold">Version:</span> {submission.version}
          </p>
        </div>
        <div class="flex gap-2">
          <button class="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 font-medium transition" on:click={load}>↻ Reload</button>
          <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition disabled:opacity-50" on:click={() => approve("v1")} disabled={actionInProgress}>✓ Approve</button>
          <button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition disabled:opacity-50" on:click={openRejectModal} disabled={actionInProgress}>✗ Reject</button>
        </div>
      </div>
    </div>

    <div class="mb-6 p-5 bg-gradient-to-br from-slate-50 to-slate-100 border-l-4 border-l-blue-500 rounded-lg">
      <label class="block">
        <div class="text-sm font-semibold mb-3 text-slate-900 flex items-center gap-2">
          <span class="text-lg">📝</span>
          <span>Moderator Notes</span>
        </div>
        <textarea
          rows="3"
          bind:value={moderatorNote}
          class="w-full border border-slate-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          placeholder="Add notes for approval or rejection (e.g., 'Fixed typo in meaning', 'Needs citation', etc.)"
        ></textarea>
        <p class="text-xs text-slate-600 mt-2 flex items-center gap-1">
          <span>ℹ</span>
          These notes will be saved with your decision and visible in moderation logs.
        </p>
      </label>
    </div>

    <div class="space-y-4 bg-slate-50 p-5 rounded-lg border border-slate-200">
      <h3 class="text-lg font-semibold text-slate-900 mb-4">Content Details</h3>
      
      <label class="block">
        <div class="text-sm font-medium text-slate-700 mb-2">Main Text</div>
        <textarea rows="6" bind:value={edit.main_text} class="w-full border border-slate-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm bg-white"></textarea>
      </label>

      <label class="block">
        <div class="text-sm font-medium text-slate-700 mb-2">Meaning / Translation</div>
        <textarea rows="4" bind:value={edit.meaning} class="w-full border border-slate-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"></textarea>
      </label>

      {#if submission.external_references}
        <div class="bg-white border-l-4 border-l-slate-400 p-4 rounded-lg">
          <h3 class="text-sm font-semibold text-slate-900 mb-3">External References</h3>
          <p class="text-xs text-slate-600 mb-2">Type-specific data ({submission.content_type})</p>
          <pre class="bg-slate-100 p-3 rounded text-xs overflow-auto max-h-64 text-slate-800 font-mono">{JSON.stringify(submission.external_references, null, 2)}</pre>
        </div>
      {/if}

      <div class="bg-white p-4 rounded-lg border border-slate-200">
        <h3 class="text-sm font-semibold text-slate-900 mb-3">Classical Content Fields</h3>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <div class="text-xs font-medium text-slate-700 mb-1">Author slug</div>
            <input class="w-full border border-slate-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={edit.author_slug} />
          </label>

          <label class="block">
            <div class="text-xs font-medium text-slate-700 mb-1">Work slug</div>
            <input class="w-full border border-slate-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={edit.work_slug} />
          </label>

          <label class="block">
            <div class="text-xs font-medium text-slate-700 mb-1">Chapter slug</div>
            <input class="w-full border border-slate-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={edit.chapter_slug} />
          </label>

          <label class="block">
            <div class="text-xs font-medium text-slate-700 mb-1">Number in chapter</div>
            <input type="number" class="w-full border border-slate-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" bind:value={edit.number_in_chapter} />
          </label>
        </div>
      </div>

      <div class="flex gap-3 pt-4 border-t border-slate-200">
        <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition disabled:opacity-50" on:click={saveChanges} disabled={saving}>{saving ? 'Saving...' : '✓ Save Changes'}</button>
        <button class="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-100 font-medium transition" on:click={() => (window.location.href = "/moderation")}>← Back to Queue</button>
      </div>
    </div>
  </div>
{/if}

<!-- Rejection Modal -->
{#if showRejectModal}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    on:click|self={closeRejectModal}
    on:keydown={(e) => e.key === "Escape" && closeRejectModal()}
  >
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 p-6 border border-slate-200">
      <div class="flex items-center gap-3 mb-4">
        <span class="text-2xl">⚠️</span>
        <h3 class="text-xl font-bold text-slate-900">Reject Submission</h3>
      </div>
      
      <p class="text-sm text-slate-600 mb-6 leading-relaxed">
        Please provide a constructive reason for rejection. This feedback will help the contributor improve their submission.
      </p>
      
      <label class="block mb-6">
        <div class="text-sm font-semibold text-slate-900 mb-2">Rejection Reason <span class="text-red-600">*</span></div>
        <textarea 
          rows="5" 
          bind:value={rejectNote} 
          class="w-full border border-slate-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white resize-none" 
          placeholder="E.g., 'Translation is incomplete', 'Source citation needed', 'Formatting issues', etc."
        ></textarea>
      </label>
      
      <div class="flex gap-3">
        <button 
          class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition disabled:opacity-50" 
          on:click={confirmReject}
          disabled={!rejectNote.trim()}
        >
          ✗ Confirm Reject
        </button>
        <button 
          class="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 font-medium transition" 
          on:click={closeRejectModal}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}
