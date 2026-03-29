<script>
  import { onMount } from "svelte";
  import { api } from "../../lib/api";
  import {
    getModerationQueue,
    approveSubmissionWithModelDecision,
    rejectSubmissionWithModelDecision,
    getCurrentUser,
    getModerationSubmissionDetail,
    getModerationTriage,
    logModelDecision,
  } from "../../lib/admin";

  let items = [];
  let loading = true;
  let error = null;
  let assignedOnly = false;
  let unassignedOnly = false;
  let selected = new Set();
  let offset = 0;
  let limit = 50;
  let currentUser = null;
  let page = 1;
  let detailOpen = false;
  let detailLoading = false;
  let detailError = "";
  let detailSubmission = null;
  let detailNote = "";
  let detailRejectOpen = false;
  let explicitHumanApproval = false;
  let triageMap = new Map();
  let contributorsMap = new Map();

  const log = (...args) => import.meta.env.DEV && console.debug("[MOD-QUEUE]", ...args);

  onMount(async () => {
    currentUser = await getCurrentUser();
    load();
  });

  function snippetFor(it) {
    if (!it) return "";
    
    // Check main_text first (for doha, etc.)
    if (it.main_text) return String(it.main_text).slice(0, 140);
    
    // Check external_references for article, dictionary, idiom
    if (it.external_references) {
      const refs = it.external_references;
      // Article
      if (refs.title) return String(refs.title).slice(0, 140);
      if (refs.body) return String(refs.body).slice(0, 140);
      // Dictionary
      if (refs.lemma_devanagari) return String(refs.lemma_devanagari).slice(0, 140);
      if (refs.lemma_roman) return String(refs.lemma_roman).slice(0, 140);
      // Idiom
      if (refs.text_devanagari) return String(refs.text_devanagari).slice(0, 140);
      if (refs.text_roman) return String(refs.text_roman).slice(0, 140);
    }
    
    // Fallback to direct fields (in case data structure varies)
    if (it.title) return String(it.title).slice(0, 140);
    if (it.body) return String(it.body).slice(0, 140);
    if (it.lemma_devanagari) return String(it.lemma_devanagari).slice(0, 140);
    if (it.text_devanagari) return String(it.text_devanagari).slice(0, 140);
    if (it.text) return String(it.text).slice(0, 140);
    
    return "(no preview)";
  }

  async function enrichContributors(itemsArr) {
    const ids = [...new Set((itemsArr || []).map((i) => i?.contributor_id).filter(Boolean))];
    if (ids.length === 0) return;

    await Promise.all(
      ids.map(async (id) => {
        if (contributorsMap.has(id)) return;
        try {
          const u = await api(`/users/id/${id}`);
          if (u && u.id) {
            contributorsMap.set(u.id, {
              id: u.id,
              name: u.name || null,
              username: u.username || null,
            });
            return;
          }
        } catch (e) {
          log(`failed to load user ${id} from /users/id`, e);
        }

        try {
          const arr = await api(`/admin/users?ids=${id}`);
          const u = Array.isArray(arr) ? arr[0] : null;
          if (u && u.id) {
            contributorsMap.set(u.id, {
              id: u.id,
              name: u.name || null,
              username: u.username || null,
              email: u.email || null,
            });
            return;
          }
        } catch (e2) {
          log(`failed to load user ${id} from /admin/users`, e2);
        }

        contributorsMap.set(id, { id, name: null, username: null, email: null });
      })
    );
  }

  function contributorLabel(it) {
    const info = contributorsMap.get(it?.contributor_id);
    if (!info) return `#${it?.contributor_id ?? "-"}`;
    return info.name || info.username || info.email || `#${it?.contributor_id ?? "-"}`;
  }

  async function load() {
    loading = true;
    error = null;
    try {
      const qs = new URLSearchParams();
      if (assignedOnly) qs.set("assigned_to_me", "true");
      if (unassignedOnly) qs.set("unassigned_only", "true");
      qs.set("limit", String(limit));
      qs.set("offset", String(offset));

      const path = `/moderation/submissions?${qs.toString()}`;
      log("fetch", path);
      const raw = await api(path);

      // ensure we handle either array or object payload
      items = Array.isArray(raw) ? raw : (raw?.items ?? []);
      
      if (import.meta.env.DEV) {
        const counts = items.reduce((acc, it) => { acc[it.content_type] = (acc[it.content_type]||0)+1; return acc; }, {});
        console.debug("[MOD-QUEUE] loaded", items.length, "items", counts);
      }

      // enrich contributors (best-effort)
      await enrichContributors(items);

      try {
        const triage = await getModerationTriage(Math.max(items.length, 20));
        triageMap = new Map(triage.map((t) => [t.submission_id, t]));
      } catch (triageErr) {
        console.warn("[MOD-QUEUE] triage unavailable", triageErr);
        triageMap = new Map();
      }

      // reset selection
      selected = new Set();

      // sort newest first by created_at if present
      items.sort((a,b) => {
        const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
        const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
        return tb - ta || (a.id - b.id);
      });

    } catch (e) {
      error = e?.message || "Unable to load moderation queue";
      console.error("[MOD-QUEUE] load error:", e);
    } finally {
      loading = false;
    }
  }

  function toggleSelect(id) {
    if (selected.has(id)) selected.delete(id);
    else selected.add(id);
  }

  async function viewDetail(id) {
    detailOpen = true;
    detailLoading = true;
    detailError = "";
    detailSubmission = null;
    detailNote = "";
    detailRejectOpen = false;
    explicitHumanApproval = false;
    try {
      detailSubmission = await getModerationSubmissionDetail(id);
    } catch (e) {
      detailError = e?.message || "Failed to load moderation details";
    } finally {
      detailLoading = false;
    }
  }

  function closeDetailPanel() {
    detailOpen = false;
    detailLoading = false;
    detailError = "";
    detailSubmission = null;
    detailNote = "";
    detailRejectOpen = false;
    explicitHumanApproval = false;
  }

  async function approveFromDetail() {
    if (!detailSubmission) return;
    if (!explicitHumanApproval) {
      detailError = "Explicit human approval checkbox is required for irreversible actions.";
      return;
    }
    if (!confirm(`Approve submission #${detailSubmission.id}?`)) return;
    try {
      const triage = triageMap.get(detailSubmission.id);
      await approveSubmissionWithModelDecision(detailSubmission.id, {
        note: detailNote.trim() || "Approved from moderation detail panel",
        guideline_version: "v1",
        approved_by_human: true,
        model_recommendation_id: triage?.recommendation_id,
        model_confidence: triage?.confidence,
        model_rationale_snippets: triage?.rationale_snippets || [],
      });
      if (triage?.recommendation_id) {
        await logModelDecision({
          recommendation_id: triage.recommendation_id,
          use_case: "moderation_triage",
          human_decision: "approve",
          rationale: detailNote.trim() || "Approved by moderator",
          reversible: false,
          approved_by_human: true,
          explainability_payload: triage.explainability || {},
        });
      }
      await load();
      closeDetailPanel();
    } catch (e) {
      detailError = e?.message || "Approval failed";
    }
  }

  async function rejectFromDetail() {
    if (!detailSubmission) return;
    if (!explicitHumanApproval) {
      detailError = "Explicit human approval checkbox is required for irreversible actions.";
      return;
    }
    const note = detailNote.trim();
    if (!note) {
      detailError = "Rejection note is required";
      return;
    }
    try {
      const triage = triageMap.get(detailSubmission.id);
      await rejectSubmissionWithModelDecision(detailSubmission.id, {
        note,
        approved_by_human: true,
        model_recommendation_id: triage?.recommendation_id,
        model_confidence: triage?.confidence,
        model_rationale_snippets: triage?.rationale_snippets || [],
      });
      if (triage?.recommendation_id) {
        await logModelDecision({
          recommendation_id: triage.recommendation_id,
          use_case: "moderation_triage",
          human_decision: "reject",
          rationale: note,
          reversible: false,
          approved_by_human: true,
          explainability_payload: triage.explainability || {},
        });
      }
      await load();
      closeDetailPanel();
    } catch (e) {
      detailError = e?.message || "Rejection failed";
    }
  }

  async function singleApprove(id) {
    const triage = triageMap.get(id);
    if (!confirm("Approve submission #" + id + "?")) return;
    try {
      await approveSubmissionWithModelDecision(id, {
        approved_by_human: true,
        note: "Approved via queue quick action",
        guideline_version: "v1",
        model_recommendation_id: triage?.recommendation_id,
        model_confidence: triage?.confidence,
        model_rationale_snippets: triage?.rationale_snippets || [],
      });
      await load();
    } catch (e) {
      alert("Approve failed: " + (e.message || e));
      console.error(e);
    }
  }

  async function singleReject(id) {
    const triage = triageMap.get(id);
    const reason = prompt("Rejection reason (required):");
    if (reason === null || !reason.trim()) return;
    try {
      await rejectSubmissionWithModelDecision(id, {
        note: reason,
        approved_by_human: true,
        model_recommendation_id: triage?.recommendation_id,
        model_confidence: triage?.confidence,
        model_rationale_snippets: triage?.rationale_snippets || [],
      });
      await load();
    } catch (e) {
      alert("Reject failed: " + (e.message || e));
      console.error(e);
    }
  }

  async function batchAction(action) {
    if (selected.size === 0) { alert("No items selected"); return; }
    if (!confirm(`${action} ${selected.size} submissions?`)) return;
    
    let reason = null;
    if (action === "reject") {
      reason = prompt("Rejection reason (required for batch reject):");
      if (!reason || !reason.trim()) return;
    }
    
    try {
      const body = {
        submission_ids: Array.from(selected),
        note: reason || `${action} via queue`,
        guideline_version: "v1",
      };
      
      // Backend endpoints: /moderation/batch-approve or /moderation/batch-reject
      const endpoint = action === "approve" ? "/moderation/batch-approve" : "/moderation/batch-reject";
      const result = await api(endpoint, { method: "POST", body });
      
      // Show results
      if (result?.results) {
        const succeeded = result.results.filter((r) => r.status === 'success').length;
        const failed = result.results.filter((r) => r.status === 'error').length;
        alert(`Batch ${action}: ${succeeded} succeeded, ${failed} failed`);
      }
      
      await load();
    } catch (e) {
      alert("Batch failed: " + (e.message || e));
      console.error(e);
    }
  }

  async function goPrevPage() {
    if (offset === 0) return;
    offset = Math.max(0, offset - limit);
    page = Math.floor(offset / limit) + 1;
    await load();
  }

  async function goNextPage() {
    if (items.length < limit) return;
    offset += limit;
    page = Math.floor(offset / limit) + 1;
    await load();
  }

  async function resetAndReload() {
    offset = 0;
    page = 1;
    await load();
  }
</script>

<div class="max-w-7xl mx-auto p-4">
  <!-- Simple Header -->
  <div class="mb-6">
    <h1 class="text-2xl font-bold text-slate-100">Moderation Queue</h1>
  </div>

  <!-- Controls -->
  <div class="flex flex-wrap gap-2 mb-4">
    <label class="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded cursor-pointer">
      <input type="checkbox" bind:checked={assignedOnly} on:change={resetAndReload} />
      <span class="text-sm text-slate-200">My Queue</span>
    </label>
    <label class="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded cursor-pointer">
      <input type="checkbox" bind:checked={unassignedOnly} on:change={resetAndReload} />
      <span class="text-sm text-slate-200">Unassigned</span>
    </label>
    <button 
      class="ml-auto px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded disabled:opacity-50"
      on:click={() => batchAction("approve")}
      disabled={selected.size === 0}
    >
      Approve ({selected.size})
    </button>
    <button 
      class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded disabled:opacity-50"
      on:click={() => batchAction("reject")}
      disabled={selected.size === 0}
    >
      Reject ({selected.size})
    </button>
  </div>

  <!-- Content -->
  {#if loading}
    <div class="text-center py-8 text-slate-400">Loading...</div>
  {:else if error}
    <div class="p-4 bg-rose-900 text-rose-100 rounded">{error}</div>
  {:else if items.length === 0}
    <div class="p-8 text-center text-slate-400 bg-slate-800 rounded">No pending items</div>
  {:else}
    <div class="overflow-x-auto border border-slate-700 rounded">
      <table class="w-full text-sm">
        <thead class="bg-slate-700 border-b border-slate-600 text-slate-100 font-semibold">
          <tr>
            <th class="px-4 py-2 text-left w-8"><input type="checkbox" on:change={(e) => { if (e.target.checked) items.forEach(i => selected.add(i.id)); else selected = new Set(); }} /></th>
            <th class="px-4 py-2 text-left">ID</th>
            <th class="px-4 py-2 text-left">Priority</th>
            <th class="px-4 py-2 text-left">Type</th>
            <th class="px-4 py-2 text-left">Preview</th>
            <th class="px-4 py-2 text-left">Status</th>
            <th class="px-4 py-2 text-left">By</th>
            <th class="px-4 py-2 text-left">Created</th>
            <th class="px-4 py-2 text-center">AI</th>
            <th class="px-4 py-2 text-center">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-700">
          {#each items as it (it.id)}
            <tr class="bg-slate-800 hover:bg-slate-750 border-b border-slate-700">
              <td class="px-4 py-2"><input type="checkbox" checked={selected.has(it.id)} on:change={() => toggleSelect(it.id)} /></td>
              <td class="px-4 py-2 font-mono text-slate-300">#{it.id}</td>
              <td class="px-4 py-2">
                <span class="px-2 py-1 text-xs rounded {
                  (it.priority || 0) >= 3 ? 'bg-red-900 text-red-200' :
                  (it.priority || 0) === 2 ? 'bg-orange-900 text-orange-200' :
                  (it.priority || 0) === 1 ? 'bg-yellow-900 text-yellow-200' :
                  'bg-slate-700 text-slate-300'
                }">P{it.priority || 0}</span>
              </td>
              <td class="px-4 py-2"><span class="px-2 py-1 text-xs rounded bg-blue-900 text-blue-200">{it.content_type}</span></td>
              <td class="px-4 py-2 max-w-xs truncate text-slate-300">{snippetFor(it)}</td>
              <td class="px-4 py-2">
                {#if it.assigned_moderator_id}
                  <span class="px-2 py-1 text-xs rounded bg-emerald-900 text-emerald-200">Assigned</span>
                {:else}
                  <span class="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300">Unassigned</span>
                {/if}
              </td>
              <td class="px-4 py-2 text-slate-400 text-xs">{contributorLabel(it)}</td>
              <td class="px-4 py-2 text-slate-400 text-xs">{it.created_at ? new Date(it.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—'}</td>
              <td class="px-4 py-2 text-center text-xs">
                {#if triageMap.get(it.id)}
                  <div class="text-slate-300">{Math.round((triageMap.get(it.id).confidence || 0) * 100)}%</div>
                  <div class="text-slate-400">{triageMap.get(it.id).recommendation}</div>
                {:else}
                  <span class="text-slate-500">—</span>
                {/if}
              </td>
              <td class="px-4 py-2 text-center">
                <div class="flex gap-1 justify-center">
                  <button 
                    class="px-2 py-1 text-xs bg-blue-700 hover:bg-blue-600 text-white rounded"
                    on:click={() => viewDetail(it.id)}
                  >
                    View
                  </button>
                  <button 
                    class="px-2 py-1 text-xs bg-emerald-700 hover:bg-emerald-600 text-white rounded"
                    on:click={() => singleApprove(it.id)}
                  >
                    OK
                  </button>
                  <button 
                    class="px-2 py-1 text-xs bg-rose-700 hover:bg-rose-600 text-white rounded"
                    on:click={() => singleReject(it.id)}
                  >
                    ✕
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="mt-4 flex items-center justify-between text-sm text-slate-300">
      <span>Page {page} ({items.length} items)</span>
      <div class="flex gap-2">
        <button 
          class="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded disabled:opacity-50"
          on:click={goPrevPage}
          disabled={offset === 0}
        >
          ← Prev
        </button>
        <button 
          class="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded disabled:opacity-50"
          on:click={goNextPage}
          disabled={items.length < limit}
        >
          Next →
        </button>
      </div>
    </div>
  {/if}
</div>

{#if detailOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    on:click|self={closeDetailPanel}
    on:keydown={(e) => e.key === "Escape" && closeDetailPanel()}
  >
    <div class="bg-slate-900 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-auto border border-slate-700">
      <!-- Header -->
      <div class="sticky top-0 bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
        <h2 class="text-lg font-bold text-slate-100">Submission #{detailSubmission?.id}</h2>
        <button 
          class="text-slate-400 hover:text-slate-200"
          on:click={closeDetailPanel}
        >
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-4">
        {#if detailLoading}
          <p class="text-slate-400">Loading...</p>
        {:else if detailError}
          <div class="p-3 bg-rose-900 text-rose-100 rounded text-sm">{detailError}</div>
        {:else if detailSubmission}
          <!-- Metadata -->
          <div class="grid grid-cols-2 gap-4 p-4 bg-slate-800 rounded text-sm">
            <div>
              <p class="text-xs text-slate-400 uppercase font-semibold">Type</p>
              <p class="text-slate-200">{detailSubmission.content_type}</p>
            </div>
            <div>
              <p class="text-xs text-slate-400 uppercase font-semibold">Priority</p>
              <p class="text-slate-200">P{detailSubmission.priority || 0}</p>
            </div>
            <div>
              <p class="text-xs text-slate-400 uppercase font-semibold">Status</p>
              <p class="text-slate-200">{detailSubmission.status}</p>
            </div>
            <div>
              <p class="text-xs text-slate-400 uppercase font-semibold">By</p>
              <p class="text-slate-200">#{detailSubmission.contributor_id}</p>
            </div>
          </div>

          <!-- Content -->
          {#if detailSubmission.main_text}
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Main Text</p>
              <pre class="p-3 bg-slate-800 rounded text-sm text-slate-200 whitespace-pre-wrap max-h-32 overflow-y-auto">{detailSubmission.main_text}</pre>
            </div>
          {/if}

          {#if detailSubmission.meaning}
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Meaning</p>
              <pre class="p-3 bg-slate-800 rounded text-sm text-slate-200 whitespace-pre-wrap max-h-32 overflow-y-auto">{detailSubmission.meaning}</pre>
            </div>
          {/if}

          <!-- AI Recommendation -->
          {#if triageMap.get(detailSubmission.id)}
            <div class="p-3 bg-blue-900 rounded text-sm border border-blue-700">
              <p class="font-semibold text-blue-200">{triageMap.get(detailSubmission.id).recommendation}</p>
              <p class="text-blue-300 text-xs mt-1">{Math.round((triageMap.get(detailSubmission.id).confidence || 0) * 100)}% confident</p>
            </div>
          {/if}

          <!-- Note -->
          <div>
            <label for="detail-note" class="text-xs font-semibold text-slate-400 uppercase mb-2 block">Moderator Note</label>
            <textarea
              id="detail-note"
              rows="3"
              class="w-full p-3 bg-slate-800 border border-slate-700 rounded text-slate-100 text-sm"
              bind:value={detailNote}
              placeholder="Add your reason..."
            ></textarea>
          </div>

          <!-- Confirmation -->
          <label class="flex items-center gap-2 p-3 bg-slate-800 rounded text-sm cursor-pointer">
            <input 
              type="checkbox" 
              bind:checked={explicitHumanApproval}
              class="w-4 h-4"
            />
            <span class="text-slate-200">I confirm this irreversible action</span>
          </label>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t border-slate-700">
            <button 
              class="flex-1 px-4 py-2 bg-emerald-700 hover:bg-emerald-600 text-white font-medium rounded text-sm disabled:opacity-50"
              on:click={approveFromDetail}
              disabled={!explicitHumanApproval}
            >
              Approve
            </button>
            {#if !detailRejectOpen}
              <button 
                class="flex-1 px-4 py-2 bg-rose-700 hover:bg-rose-600 text-white font-medium rounded text-sm"
                on:click={() => detailRejectOpen = true}
              >
                Reject
              </button>
            {:else}
              <button 
                class="flex-1 px-4 py-2 bg-rose-800 hover:bg-rose-700 text-white font-medium rounded text-sm disabled:opacity-50"
                on:click={rejectFromDetail}
                disabled={!explicitHumanApproval || !detailNote.trim()}
              >
                Confirm
              </button>
              <button 
                class="px-4 py-2 border border-slate-600 text-slate-300 hover:bg-slate-700 font-medium rounded text-sm"
                on:click={() => detailRejectOpen = false}
              >
                Cancel
              </button>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
