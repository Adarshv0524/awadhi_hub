<script lang="ts">
  import { onMount } from "svelte";
  import { listMySubmissions, deleteSubmission } from "../../lib/submissions";

  let submissions: any[] = [];
  let loading = true;
  let error = "";

  let status = "";
  let content_type = "";
  let offset = 0;
  const limit = 20;
  
  // Delete confirmation modal state
  let showDeleteModal = false;
  let deletingSubmissionId: number | null = null;
  let deletingSubmissionText = "";
  let isDeleting = false;

  async function load() {
    loading = true;
    error = "";
    try {
      submissions = await listMySubmissions({ status, content_type, offset, limit });
    } catch (e: any) {
      error = e?.message || "Failed to load submissions";
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function reset() {
    offset = 0;
    load();
  }

  function loadMore() {
    offset += limit;
    load();
  }
  
  function confirmDelete(id: number, text: string) {
    deletingSubmissionId = id;
    deletingSubmissionText = text;
    showDeleteModal = true;
  }
  
  function cancelDelete() {
    showDeleteModal = false;
    deletingSubmissionId = null;
    deletingSubmissionText = "";
    isDeleting = false;
  }
  
  async function performDelete() {
    if (!deletingSubmissionId) return;
    
    isDeleting = true;
    error = "";
    
    try {
      await deleteSubmission(deletingSubmissionId);
      
      // Remove from local list
      submissions = submissions.filter(s => s.id !== deletingSubmissionId);
      
      // Close modal
      cancelDelete();
    } catch (e: any) {
      error = e?.message || "Failed to delete submission";
      isDeleting = false;
    }
  }
</script>

<div class="max-w-4xl mx-auto bg-slate-900 text-slate-100 p-6 rounded-lg">
  <h2 class="text-2xl font-serif font-bold mb-6 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
    My Submissions
  </h2>

  <!-- Filters -->
  <div class="filters mb-6 flex flex-wrap gap-4">
    <div class="flex flex-col">
      <label for="status-filter" class="text-xs text-slate-400 mb-1">Status</label>
      <select
        id="status-filter"
        bind:value={status}
        on:change={reset}
        class="px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 hover:border-blue-500 focus:border-blue-500 focus:outline-none"
      >
        <option value="">All</option>
        <option value="draft">Draft</option>
        <option value="pending_review">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <div class="flex flex-col">
      <label for="type-filter" class="text-xs text-slate-400 mb-1">Content Type</label>
      <select
        id="type-filter"
        bind:value={content_type}
        on:change={reset}
        class="px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 hover:border-blue-500 focus:border-blue-500 focus:outline-none"
      >
        <option value="">All Types</option>
        <option value="doha">Doha</option>
        <option value="dictionary">Dictionary</option>
        <option value="idiom">Idiom</option>
        <option value="article">Article</option>
      </select>
    </div>
  </div>

  <!-- Content -->
  {#if loading}
    <p class="text-cyan-400 text-center py-8">Loading submissions…</p>
  {:else if error}
    <p class="error text-red-400 bg-red-950 border border-red-800 rounded p-4">{error}</p>
  {:else if submissions.length === 0}
    <p class="text-slate-400 text-center py-8">No submissions found.</p>
  {:else}
    <ul class="space-y-4">
      {#each submissions as s}
        <li class="border border-slate-700 bg-slate-800 p-4 rounded-lg hover:border-blue-500 transition-colors">
          <div class="flex justify-between items-start mb-2">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <strong class="text-blue-300 font-semibold">{s.content_type}</strong>
                <span
                  class="px-2 py-1 text-xs rounded font-medium {s.status === 'approved'
                    ? 'bg-green-900 text-green-300'
                    : s.status === 'rejected'
                      ? 'bg-red-900 text-red-300'
                      : s.status === 'pending_review'
                        ? 'bg-yellow-900 text-yellow-300'
                        : 'bg-slate-700 text-slate-300'}"
                >
                  {s.status}
                </span>
              </div>
              <div class="text-sm text-slate-300 mb-2">
                {s.main_text?.slice(0, 200) || "(no text)"}
                {#if s.main_text && s.main_text.length > 200}...{/if}
              </div>
              <div class="text-xs text-slate-500">
                Created: {new Date(s.created_at).toLocaleString()}
              </div>
            </div>
          </div>
          <div class="mt-3 flex gap-3">
            <a
              href={`/submissions/${s.id}`}
              class="text-sm text-cyan-400 hover:text-cyan-300 underline font-medium"
            >
              View Details
            </a>
            {#if s.status === "approved"}
              <a
                href={`/${s.content_type}/${s.id}`}
                class="text-sm text-green-400 hover:text-green-300 underline font-medium"
              >
                View Published
              </a>
            {/if}
            {#if s.status === "draft" || s.status === "rejected"}
              <button
                on:click={() => confirmDelete(s.id, s.main_text?.slice(0, 50) || "this submission")}
                class="text-sm text-red-400 hover:text-red-300 underline font-medium"
                aria-label="Delete submission"
              >
                Delete
              </button>
            {/if}
          </div>
        </li>
      {/each}
    </ul>

    <!-- Load More Button -->
    {#if submissions.length >= limit}
      <div class="mt-6 text-center">
        <button
          on:click={loadMore}
          class="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-medium transition-colors"
        >
          Load More
        </button>
      </div>
    {/if}
  {/if}
</div>

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" on:click={cancelDelete}>
    <div class="bg-slate-900 border-2 border-red-700 rounded-xl p-6 max-w-md mx-4 shadow-2xl" on:click|stopPropagation>
      <div class="flex items-start gap-3 mb-4">
        <svg class="w-6 h-6 text-red-400 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
        <div class="flex-1">
          <h3 class="text-xl font-bold text-red-400 mb-2">Delete Submission?</h3>
          <p class="text-slate-300 text-sm mb-3">
            Are you sure you want to delete this submission? This action cannot be undone.
          </p>
          <div class="bg-slate-800 border border-slate-700 rounded p-3 mb-4">
            <p class="text-xs text-slate-400 mb-1">Submission Preview:</p>
            <p class="text-sm text-slate-200 italic">"{deletingSubmissionText}..."</p>
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
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
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
