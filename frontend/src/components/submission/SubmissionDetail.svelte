<!-- src/components/submission/SubmissionDetail.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { deleteSubmission } from "../../lib/submissions";
  import { api, ApiError } from "../../lib/api";

  export let submissionId: string;

  let submission: any = null;
  let loading = true;
  let fetchError = "";
  let showDeleteModal = false;
  let isDeleting = false;
  let deleteError = "";

  onMount(async () => {
    loading = true;
    fetchError = "";
    
    try {
      submission = await api(`/submissions/${submissionId}`);
    } catch (e: any) {
      if (e instanceof ApiError && e.status === 404) {
        fetchError = "Submission not found";
      } else if (e instanceof ApiError && e.status === 401) {
        // Not logged in - redirect to login
        if (typeof window !== "undefined") {
          window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
        }
        return;
      } else {
        fetchError = e?.message || "Unable to load submission";
      }
    } finally {
      loading = false;
    }
  });

  function confirmDelete() {
    showDeleteModal = true;
  }

  function cancelDelete() {
    showDeleteModal = false;
    isDeleting = false;
    deleteError = "";
  }

  async function performDelete() {
    if (!submission) return;
    
    isDeleting = true;
    deleteError = "";

    try {
      await deleteSubmission(submission.id);
      // Redirect to submissions list after successful delete
      if (typeof window !== "undefined") {
        window.location.href = "/submissions";
      }
    } catch (e: any) {
      deleteError = e?.message || "Failed to delete submission";
      isDeleting = false;
    }
  }

  $: canDelete = submission && (submission.status === "draft" || submission.status === "rejected");
</script>

{#if loading}
  <div class="flex items-center justify-center py-12">
    <div class="flex flex-col items-center gap-3">
      <svg class="animate-spin h-8 w-8 text-cyan-400" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-slate-400">Loading submission...</p>
    </div>
  </div>
{:else if fetchError}
  <div class="bg-red-950 border border-red-800 rounded-lg p-6">
    <p class="text-red-300">{fetchError}</p>
    <a href="/submissions" class="mt-4 inline-block text-cyan-400 hover:text-cyan-300 underline">
      ← Back to Submissions
    </a>
  </div>
{:else if submission}
  <div class="space-y-6 max-w-3xl">
    {#if deleteError}
      <div class="bg-red-950 border border-red-800 rounded-lg p-4">
        <p class="text-red-300 text-sm">{deleteError}</p>
      </div>
    {/if}

  <div class="flex items-start justify-between">
    <h1 class="text-3xl font-serif font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
      {submission.content_type ?? "Submission"} #{submission.id}
    </h1>
    <div class="text-sm">
      <span
        class="px-3 py-1 rounded-full font-medium {submission.status === 'approved'
          ? 'bg-green-900 text-green-300'
          : submission.status === 'rejected'
            ? 'bg-red-900 text-red-300'
            : submission.status === 'pending_review'
              ? 'bg-yellow-900 text-yellow-300'
              : 'bg-slate-700 text-slate-300'}"
      >
        {submission.status}
      </span>
    </div>
  </div>

  <section class="bg-slate-800/50 border border-slate-700 p-6 rounded-lg">
    <h2 class="font-semibold text-cyan-400 mb-4 text-lg">Content</h2>
    {#if submission.main_text}
      <div class="mb-4">
        <div class="text-sm font-medium text-slate-400 mb-1">Main Text:</div>
        <div class="text-lg text-slate-200">{submission.main_text}</div>
      </div>
    {/if}
    {#if submission.meaning}
      <div class="mb-4">
        <div class="text-sm font-medium text-slate-400 mb-1">Meaning:</div>
        <div class="text-slate-300">{submission.meaning}</div>
      </div>
    {/if}
    {#if submission.metadata && typeof submission.metadata === "object"}
      <div class="mb-4">
        <div class="text-sm font-medium text-slate-400 mb-1">Metadata:</div>
        <pre class="text-xs bg-slate-900 p-3 rounded border border-slate-700 overflow-auto text-slate-300">{JSON.stringify(
            submission.metadata,
            null,
            2
          )}</pre>
      </div>
    {/if}
  </section>

  <section class="text-sm text-slate-400">
    <div class="grid grid-cols-2 gap-3">
      <div>
        <strong class="text-slate-300">Visibility:</strong>
        {submission.visibility ?? "draft"}
      </div>
      <div>
        <strong class="text-slate-300">Version:</strong>
        {submission.version ?? 1}
      </div>
      <div>
        <strong class="text-slate-300">Submitted:</strong>
        {submission.created_at ? new Date(submission.created_at).toLocaleString() : "—"}
      </div>
      {#if submission.updated_at}
        <div>
          <strong class="text-slate-300">Updated:</strong>
          {new Date(submission.updated_at).toLocaleString()}
        </div>
      {/if}
    </div>
  </section>

  {#if submission.moderator_notes}
    <section class="bg-blue-900/20 border border-blue-800/30 p-5 rounded-lg">
      <h2 class="font-semibold text-blue-300 mb-2">Moderator Notes</h2>
      <p class="text-sm text-blue-200">{submission.moderator_notes}</p>
    </section>
  {/if}

  <div class="flex gap-3 pt-4 border-t border-slate-700">
    <a
      href="/submissions"
      class="px-4 py-2 rounded border border-slate-600 hover:bg-slate-800 text-slate-200 font-medium transition-colors"
    >
      ← Back to My Submissions
    </a>
    {#if canDelete}
      <a
        href={`/submissions/${submission.id}/edit`}
        class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-500 font-medium transition-colors"
      >
        Edit Submission
      </a>
      <button
        on:click={confirmDelete}
        class="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-500 font-medium transition-colors ml-auto"
      >
        Delete Submission
      </button>
    {/if}
  </div>
</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && submission}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    on:click={cancelDelete}
  >
    <div
      class="bg-slate-900 border-2 border-red-700 rounded-xl p-6 max-w-md mx-4 shadow-2xl"
      on:click|stopPropagation
    >
      <div class="flex items-start gap-3 mb-4">
        <svg
          class="w-6 h-6 text-red-400 flex-shrink-0 mt-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          ></path>
        </svg>
        <div class="flex-1">
          <h3 class="text-xl font-bold text-red-400 mb-2">Delete Submission?</h3>
          <p class="text-slate-300 text-sm mb-3">
            Are you sure you want to delete this submission? This action cannot be undone.
          </p>
          <div class="bg-slate-800 border border-slate-700 rounded p-3 mb-4">
            <p class="text-xs text-slate-400 mb-1">Submission ID:</p>
            <p class="text-sm text-slate-200 font-mono">#{submission.id}</p>
          </div>
          <div class="bg-slate-800 border border-slate-700 rounded p-3 mb-2">
            <p class="text-xs text-slate-400 mb-1">Preview:</p>
            <p class="text-sm text-slate-200 italic">
              "{submission.main_text?.slice(0, 80) || "No content"}..."
            </p>
          </div>
        </div>
      </div>

      <div class="flex gap-3 justify-end">
        <button
          on:click={cancelDelete}
          disabled={isDeleting}
          class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded font-medium transition-colors disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          on:click={performDelete}
          disabled={isDeleting}
          class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {#if isDeleting}
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Deleting...
          {:else}
            Delete Submission
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}
