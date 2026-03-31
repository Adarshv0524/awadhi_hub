<script>
  import { onMount } from "svelte";
  import { api } from "../../lib/api";
  import {
    getModerationQueue,
    getModerationReports,
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

  let reports = [];
  let reportsLoading = false;
  let reportsError = null;
  let reportsStatus = "open";
  let reportsContentType = "";
  let reportsReason = "";
  let queueSearch = "";
  let queueTypeFilter = "";

  const log = (...args) => import.meta.env.DEV && console.debug("[MOD-QUEUE]", ...args);

  onMount(async () => {
    currentUser = await getCurrentUser();
    await Promise.all([load(), loadReports()]);
  });

  async function refreshAll() {
    await Promise.all([load(), loadReports()]);
  }

  $: queuePendingCount = items.length;
  $: queueAssignedCount = items.filter((it) => Boolean(it.assigned_moderator_id)).length;
  $: queueCriticalCount = items.filter((it) => Number(it.priority || 0) >= 3).length;
  $: openReportsCount = reports.filter((r) => r.status === "open").length;

  $: displayedItems = items.filter((it) => {
    const typeOk = !queueTypeFilter || String(it.content_type || "").toLowerCase() === queueTypeFilter.toLowerCase();
    if (!typeOk) return false;

    const q = queueSearch.trim().toLowerCase();
    if (!q) return true;
    const hay = [
      String(it.id || ""),
      String(it.content_type || ""),
      snippetFor(it),
      contributorLabel(it),
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });

  function reportReporterLabel(report) {
    return report?.reporter_username || report?.reporter_email || `#${report?.user_id ?? "-"}`;
  }

  async function loadReports() {
    reportsLoading = true;
    reportsError = null;
    try {
      const payload = await getModerationReports({
        status: reportsStatus || undefined,
        content_type: reportsContentType || undefined,
        reason: reportsReason || undefined,
        limit: 20,
        offset: 0,
      });
      reports = Array.isArray(payload?.results) ? payload.results : [];
    } catch (e) {
      reportsError = e?.message || "Unable to load reports";
      console.error("[MOD-REPORTS] load error:", e);
    } finally {
      reportsLoading = false;
    }
  }

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
      await loadReports();
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
      await loadReports();
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
      await loadReports();
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
      await loadReports();
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
      await loadReports();
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

<div class="mod-shell max-w-7xl mx-auto p-4 md:p-6">
  <section class="mod-hero rounded-2xl border border-slate-700/80 p-5 md:p-7 mb-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <p class="text-xs uppercase tracking-[0.28em] text-cyan-300/80 font-semibold">Moderation Command</p>
        <h1 class="text-2xl md:text-3xl font-semibold text-white mt-1">Queue + Report Triage</h1>
        <p class="text-sm md:text-base text-slate-300 mt-2 max-w-2xl">
          Review high-priority submissions, inspect user reports across poetry/dictionary/idiom/article content, and take decisive action.
        </p>
      </div>
      <button
        class="mod-btn mod-btn-secondary"
        on:click={refreshAll}
      >
        Refresh Board
      </button>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-6">
      <article class="mod-kpi">
        <p class="mod-kpi-label">Queue Items</p>
        <p class="mod-kpi-value">{queuePendingCount}</p>
      </article>
      <article class="mod-kpi">
        <p class="mod-kpi-label">Assigned</p>
        <p class="mod-kpi-value">{queueAssignedCount}</p>
      </article>
      <article class="mod-kpi">
        <p class="mod-kpi-label">Critical Priority</p>
        <p class="mod-kpi-value text-amber-300">{queueCriticalCount}</p>
      </article>
      <article class="mod-kpi">
        <p class="mod-kpi-label">Open Reports</p>
        <p class="mod-kpi-value text-rose-300">{openReportsCount}</p>
      </article>
    </div>
  </section>

  <section class="rounded-2xl border border-slate-700/80 bg-slate-900/55 p-4 md:p-5 mb-6">
    <div class="flex flex-wrap gap-2 items-center">
      <label class="mod-chip cursor-pointer">
        <input type="checkbox" bind:checked={assignedOnly} on:change={resetAndReload} />
        <span>My Queue</span>
      </label>
      <label class="mod-chip cursor-pointer">
        <input type="checkbox" bind:checked={unassignedOnly} on:change={resetAndReload} />
        <span>Unassigned</span>
      </label>
      <div class="ml-auto flex flex-wrap gap-2">
        <button
          class="mod-btn mod-btn-success"
          on:click={() => batchAction("approve")}
          disabled={selected.size === 0}
        >
          Approve Selected ({selected.size})
        </button>
        <button
          class="mod-btn mod-btn-danger"
          on:click={() => batchAction("reject")}
          disabled={selected.size === 0}
        >
          Reject Selected ({selected.size})
        </button>
      </div>
    </div>
  </section>

  <div class="grid grid-cols-1 xl:grid-cols-[1.35fr_1fr] gap-6 mb-6">
    <section class="rounded-2xl border border-slate-700/80 bg-slate-900/55 p-4 md:p-5">
      <div class="flex items-center justify-between gap-3 mb-3">
        <h2 class="text-lg font-semibold text-slate-100">Submission Queue</h2>
        <span class="text-xs text-slate-400">Page {page}</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
        <input
          class="mod-input"
          placeholder="Search by id, type, preview, or contributor"
          bind:value={queueSearch}
        />
        <input
          class="mod-input"
          placeholder="Filter by content type"
          bind:value={queueTypeFilter}
        />
      </div>

      {#if loading}
        <div class="text-center py-10 text-slate-400">Loading queue...</div>
      {:else if error}
        <div class="p-3 rounded-lg bg-rose-900/50 text-rose-100 border border-rose-700/60">{error}</div>
      {:else if displayedItems.length === 0}
        <div class="p-8 text-center text-slate-400 bg-slate-800/60 rounded-xl border border-slate-700/60">No matching queue items.</div>
      {:else}
        <div class="hidden lg:block overflow-x-auto border border-slate-700/70 rounded-xl">
          <table class="w-full text-sm">
            <thead class="bg-slate-800/90 border-b border-slate-700 text-slate-100">
              <tr>
                <th class="px-3 py-2 text-left w-10">
                  <input type="checkbox" on:change={(e) => { if (e.target.checked) displayedItems.forEach((i) => selected.add(i.id)); else selected = new Set(); }} />
                </th>
                <th class="px-3 py-2 text-left">Submission</th>
                <th class="px-3 py-2 text-left">Preview</th>
                <th class="px-3 py-2 text-left">Assignment</th>
                <th class="px-3 py-2 text-center">AI</th>
                <th class="px-3 py-2 text-center">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/70">
              {#each displayedItems as it (it.id)}
                <tr class="bg-slate-900/35 hover:bg-slate-800/55 transition-colors">
                  <td class="px-3 py-2"><input type="checkbox" checked={selected.has(it.id)} on:change={() => toggleSelect(it.id)} /></td>
                  <td class="px-3 py-2">
                    <p class="font-mono text-xs text-slate-300">#{it.id}</p>
                    <div class="mt-1 flex items-center gap-2">
                      <span class="px-2 py-0.5 text-[11px] rounded bg-cyan-900/70 text-cyan-200">{it.content_type}</span>
                      <span class="px-2 py-0.5 text-[11px] rounded {(it.priority || 0) >= 3 ? 'bg-rose-900/70 text-rose-200' : (it.priority || 0) === 2 ? 'bg-amber-900/70 text-amber-200' : 'bg-slate-700 text-slate-200'}">P{it.priority || 0}</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-1">{it.created_at ? new Date(it.created_at).toLocaleString() : "-"}</p>
                  </td>
                  <td class="px-3 py-2 max-w-sm">
                    <p class="text-slate-200 line-clamp-2">{snippetFor(it)}</p>
                    <p class="text-xs text-slate-400 mt-1">By {contributorLabel(it)}</p>
                  </td>
                  <td class="px-3 py-2">
                    {#if it.assigned_moderator_id}
                      <span class="px-2 py-1 text-xs rounded bg-emerald-900/70 text-emerald-200">Assigned</span>
                    {:else}
                      <span class="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300">Unassigned</span>
                    {/if}
                  </td>
                  <td class="px-3 py-2 text-center text-xs">
                    {#if triageMap.get(it.id)}
                      <p class="text-slate-100 font-medium">{Math.round((triageMap.get(it.id).confidence || 0) * 100)}%</p>
                      <p class="text-slate-400">{triageMap.get(it.id).recommendation}</p>
                    {:else}
                      <span class="text-slate-500">—</span>
                    {/if}
                  </td>
                  <td class="px-3 py-2">
                    <div class="flex gap-1 justify-center">
                      <button class="mod-mini-btn bg-blue-700 hover:bg-blue-600" on:click={() => viewDetail(it.id)}>View</button>
                      <button class="mod-mini-btn bg-emerald-700 hover:bg-emerald-600" on:click={() => singleApprove(it.id)}>Approve</button>
                      <button class="mod-mini-btn bg-rose-700 hover:bg-rose-600" on:click={() => singleReject(it.id)}>Reject</button>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        <div class="lg:hidden space-y-3">
          {#each displayedItems as it (it.id)}
            <article class="rounded-xl border border-slate-700/70 bg-slate-900/45 p-3">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-mono text-xs text-slate-300">#{it.id}</p>
                  <div class="flex gap-2 mt-1">
                    <span class="px-2 py-0.5 text-[11px] rounded bg-cyan-900/70 text-cyan-200">{it.content_type}</span>
                    <span class="px-2 py-0.5 text-[11px] rounded {(it.priority || 0) >= 3 ? 'bg-rose-900/70 text-rose-200' : (it.priority || 0) === 2 ? 'bg-amber-900/70 text-amber-200' : 'bg-slate-700 text-slate-200'}">P{it.priority || 0}</span>
                  </div>
                </div>
                <input type="checkbox" checked={selected.has(it.id)} on:change={() => toggleSelect(it.id)} />
              </div>
              <p class="text-sm text-slate-200 mt-2">{snippetFor(it)}</p>
              <p class="text-xs text-slate-400 mt-1">By {contributorLabel(it)}</p>
              <div class="flex gap-1 mt-3">
                <button class="mod-mini-btn bg-blue-700 hover:bg-blue-600 flex-1" on:click={() => viewDetail(it.id)}>View</button>
                <button class="mod-mini-btn bg-emerald-700 hover:bg-emerald-600 flex-1" on:click={() => singleApprove(it.id)}>Approve</button>
                <button class="mod-mini-btn bg-rose-700 hover:bg-rose-600 flex-1" on:click={() => singleReject(it.id)}>Reject</button>
              </div>
            </article>
          {/each}
        </div>

        <div class="mt-4 flex items-center justify-between text-sm text-slate-300">
          <span>Showing {displayedItems.length} items</span>
          <div class="flex gap-2">
            <button class="mod-btn mod-btn-secondary" on:click={goPrevPage} disabled={offset === 0}>Prev</button>
            <button class="mod-btn mod-btn-secondary" on:click={goNextPage} disabled={items.length < limit}>Next</button>
          </div>
        </div>
      {/if}
    </section>

    <section class="rounded-2xl border border-slate-700/80 bg-slate-900/55 p-4 md:p-5">
      <div class="flex items-center justify-between gap-3 mb-3">
        <h2 class="text-lg font-semibold text-slate-100">User Reports</h2>
        <button class="mod-btn mod-btn-secondary" on:click={loadReports}>Refresh</button>
      </div>

      <div class="grid grid-cols-1 gap-2 mb-3">
        <select class="mod-input" bind:value={reportsStatus} on:change={loadReports}>
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
          <option value="rejected">Rejected</option>
          <option value="">All statuses</option>
        </select>
        <input class="mod-input" placeholder="Filter by content type" bind:value={reportsContentType} on:change={loadReports} />
        <select class="mod-input" bind:value={reportsReason} on:change={loadReports}>
          <option value="">All reasons</option>
          <option value="spam">spam</option>
          <option value="abuse">abuse</option>
          <option value="copyright">copyright</option>
          <option value="other">other</option>
        </select>
      </div>

      {#if reportsLoading}
        <div class="text-sm text-slate-400 py-6">Loading reports...</div>
      {:else if reportsError}
        <div class="text-sm text-rose-300">{reportsError}</div>
      {:else if reports.length === 0}
        <div class="text-sm text-slate-400 py-6">No reports found for current filters.</div>
      {:else}
        <div class="space-y-2 max-h-[540px] overflow-auto pr-1">
          {#each reports as r (r.id)}
            <article class="rounded-xl border border-slate-700/70 bg-slate-900/45 p-3">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p class="font-mono text-xs text-slate-400">Report #{r.id}</p>
                  <p class="text-sm text-slate-100 mt-1">{r.content_type} #{r.content_id}</p>
                </div>
                <span class="px-2 py-0.5 rounded text-[11px] bg-rose-900/70 text-rose-200">{r.reason}</span>
              </div>
              <p class="text-xs text-slate-300 mt-1">Reporter: {reportReporterLabel(r)}</p>
              {#if r.content_title}
                <p class="text-xs text-slate-400 mt-1 truncate">{r.content_title}</p>
              {/if}
              <p class="text-xs text-slate-400 mt-1 line-clamp-2">{r.note || "No reporter note"}</p>
              <p class="text-[11px] text-slate-500 mt-2">{r.created_at ? new Date(r.created_at).toLocaleString() : "-"}</p>
            </article>
          {/each}
        </div>
      {/if}
    </section>
  </div>
</div>

<style>
  .mod-shell {
    background:
      radial-gradient(1200px 420px at 0% 0%, rgba(34, 211, 238, 0.08), transparent 60%),
      radial-gradient(900px 420px at 100% 100%, rgba(248, 113, 113, 0.06), transparent 58%);
  }

  .mod-hero {
    background:
      linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(17, 24, 39, 0.92) 45%, rgba(22, 78, 99, 0.55) 100%);
    box-shadow: 0 12px 35px rgba(2, 6, 23, 0.35);
  }

  .mod-kpi {
    border: 1px solid rgba(51, 65, 85, 0.75);
    background: rgba(15, 23, 42, 0.64);
    border-radius: 0.85rem;
    padding: 0.8rem 0.9rem;
  }

  .mod-kpi-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: rgb(148 163 184);
    font-weight: 600;
  }

  .mod-kpi-value {
    font-size: 1.5rem;
    line-height: 1.95rem;
    color: rgb(241 245 249);
    margin-top: 0.35rem;
    font-weight: 700;
  }

  .mod-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border-radius: 9999px;
    border: 1px solid rgba(51, 65, 85, 0.75);
    background: rgba(15, 23, 42, 0.68);
    color: rgb(226 232 240);
    font-size: 0.8rem;
    padding: 0.45rem 0.8rem;
  }

  .mod-input {
    width: 100%;
    border-radius: 0.7rem;
    border: 1px solid rgba(51, 65, 85, 0.8);
    background: rgba(15, 23, 42, 0.72);
    color: rgb(226 232 240);
    font-size: 0.86rem;
    padding: 0.58rem 0.72rem;
  }

  .mod-input::placeholder {
    color: rgb(148 163 184);
  }

  .mod-input:focus {
    outline: none;
    border-color: rgba(34, 211, 238, 0.8);
    box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.22);
  }

  .mod-btn {
    border-radius: 0.72rem;
    border: 1px solid transparent;
    padding: 0.52rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.18s ease;
    color: white;
  }

  .mod-btn:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .mod-btn-secondary {
    background: rgba(30, 41, 59, 0.88);
    border-color: rgba(71, 85, 105, 0.8);
  }

  .mod-btn-secondary:hover:not(:disabled) {
    background: rgba(51, 65, 85, 0.95);
  }

  .mod-btn-success {
    background: rgba(5, 150, 105, 0.85);
  }

  .mod-btn-success:hover:not(:disabled) {
    background: rgba(5, 150, 105, 1);
  }

  .mod-btn-danger {
    background: rgba(190, 24, 93, 0.88);
  }

  .mod-btn-danger:hover:not(:disabled) {
    background: rgba(190, 24, 93, 1);
  }

  .mod-mini-btn {
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: 0.45rem;
    padding: 0.33rem 0.52rem;
    transition: background 0.16s ease;
  }
</style>

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
