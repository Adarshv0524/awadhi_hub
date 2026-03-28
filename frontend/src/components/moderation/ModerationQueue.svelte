<script>
  import { onMount } from "svelte";
  import { api } from "../../lib/api";
  import { getModerationQueue, approveSubmission, rejectSubmission, getCurrentUser } from "../../lib/admin";

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

  // contributor id -> { id, username, email }
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
    const ids = [...new Set(itemsArr.map(i => i.contributor_id).filter(Boolean))];
    if (ids.length === 0) return;

    // Fallback: fetch users individually (more reliable for moderators)
    await Promise.all(ids.map(async (id) => {
      if (contributorsMap.has(id)) return;
      try {
        // Try public user endpoint first (should work for everyone)
        const u = await api(`/users/${id}`);
        if (u && u.id) {
          contributorsMap.set(u.id, { id: u.id, username: u.username, email: u.email });
          return;
        }
      } catch (e) {
        log(`failed to load user ${id} from /users`, e);
      }
      
      // Fallback to admin endpoint (for admins only)
      try {
        const arr = await api(`/admin/users?ids=${id}`);
        if (Array.isArray(arr) && arr[0]) {
          const u = arr[0];
          contributorsMap.set(u.id, { id: u.id, username: u.username, email: u.email });
        }
      } catch (e) {
        log(`failed to load user ${id} from /admin/users`, e);
        // Store a placeholder so we don't retry
        contributorsMap.set(id, { id, username: null, email: null });
      }
    }));
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

  function viewDetail(id) {
    window.location.href = `/moderation/${id}`;
  }

  async function singleApprove(id) {
    if (!confirm("Approve submission #" + id + "?")) return;
    try {
      await approveSubmission(id);
      await load();
    } catch (e) {
      alert("Approve failed: " + (e.message || e));
      console.error(e);
    }
  }

  async function singleReject(id) {
    const reason = prompt("Rejection reason (required):");
    if (reason === null || !reason.trim()) return;
    try {
      await rejectSubmission(id, reason);
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

<div class="mb-4 flex items-center gap-3">
  <label class="inline-flex items-center gap-2">
    <input type="checkbox" bind:checked={assignedOnly} on:change={resetAndReload} />
    <span>Assigned to me</span>
  </label>
  <label class="inline-flex items-center gap-2">
    <input type="checkbox" bind:checked={unassignedOnly} on:change={resetAndReload} />
    <span>Unassigned only</span>
  </label>

  <div class="ml-auto flex gap-2">
    <button class="px-3 py-1 border rounded" on:click={() => batchAction("approve")}>Batch Approve</button>
    <button class="px-3 py-1 border rounded" on:click={() => batchAction("reject")}>Batch Reject</button>
  </div>
</div>

{#if loading}
  <p>Loading moderation queue…</p>
{:else if error}
  <p class="text-red-600">{error}</p>
{:else if items.length === 0}
  <p>No pending submissions.</p>
{:else}
  <table class="w-full table-auto border-collapse">
    <thead>
      <tr class="text-left">
        <th class="p-2">
          <input type="checkbox" on:change={(e) => { if (e.target.checked) items.forEach(i => selected.add(i.id)); else selected = new Set(); }} />
        </th>
        <th class="p-2">#</th>
        <th class="p-2">Priority</th>
        <th class="p-2">Type</th>
        <th class="p-2">Snippet</th>
        <th class="p-2">Assigned To</th>
        <th class="p-2">Contributor</th>
        <th class="p-2">Created</th>
        <th class="p-2">Actions</th>
      </tr>
    </thead>
    <tbody>
      {#each items as it}
        <tr class="border-t {it.assigned_moderator_id === currentUser?.id ? 'bg-blue-50' : ''}">
          <td class="p-2"><input type="checkbox" checked={selected.has(it.id)} on:change={() => toggleSelect(it.id)} /></td>
          <td class="p-2">{it.id}</td>
          <td class="p-2">
            <span class="px-2 py-1 text-xs rounded font-medium {
              (it.priority || 0) >= 3 ? 'bg-red-100 text-red-700' :
              (it.priority || 0) === 2 ? 'bg-orange-100 text-orange-700' :
              (it.priority || 0) === 1 ? 'bg-yellow-100 text-yellow-700' :
              'bg-gray-100 text-gray-700'
            }">
              {it.priority !== undefined && it.priority !== null ? it.priority : 0}
            </span>
          </td>
          <td class="p-2">{it.content_type}</td>
          <td class="p-2">
            <div class="line-clamp-2">{snippetFor(it)}</div>
          </td>
          <td class="p-2">
            {#if it.assigned_moderator_id}
              <span class="text-blue-500">Assigned</span>
            {:else}
              <span class="text-gray-500">Unassigned</span>
            {/if}
          </td>
          <td class="p-2">
            {#if contributorsMap.get(it.contributor_id)}
              <a href={`/admin/users/${it.contributor_id}`} class="underline">{contributorsMap.get(it.contributor_id).username ?? contributorsMap.get(it.contributor_id).email}</a>
            {:else}
              {it.contributor_id ?? "—"}
            {/if}
          </td>
          <td class="p-2">{it.created_at ? new Date(it.created_at).toLocaleString() : "—"}</td>
          <td class="p-2">
            <div class="flex gap-2 flex-wrap">
              <button class="px-2 py-1 border rounded text-sm" on:click={() => viewDetail(it.id)}>View</button>
              <button class="px-2 py-1 bg-green-600 text-white rounded text-sm" on:click={() => singleApprove(it.id)}>Approve</button>
              <button class="px-2 py-1 bg-red-600 text-white rounded text-sm" on:click={() => singleReject(it.id)}>Reject</button>
            </div>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>

  <div class="mt-4 flex items-center justify-between gap-2">
    <p class="text-sm text-slate-500">Page {page} · Showing up to {limit} items</p>
    <div class="flex items-center gap-2">
      <button class="px-3 py-1 border rounded disabled:opacity-40" on:click={goPrevPage} disabled={offset === 0}>Previous</button>
      <button class="px-3 py-1 border rounded disabled:opacity-40" on:click={goNextPage} disabled={items.length < limit}>Next</button>
    </div>
  </div>
{/if}
