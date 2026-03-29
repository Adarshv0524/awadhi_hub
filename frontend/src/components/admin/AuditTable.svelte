<script>
  // apiBase prop kept for backward compatibility but unused (uses admin.ts wrapper)
  export let apiBase = "";
  void apiBase;
  import { onMount } from "svelte";
  import { getAuditLogs, getAuditLogById } from "../../lib/admin";
  
  let rows = [];
  let loading = true;
  let error = "";
  let currentPage = 1;
  let pageSize = 50;
  let total = 0;
  let exporting = false;
  let detailLoading = false;
  let detailError = "";
  let selectedAudit = null;

  function formatTimestamp(timestamp) {
    if (!timestamp) return "-";
    return new Date(timestamp).toLocaleString();
  }

  async function load() {
    loading = true;
    error = "";
    try {
      const offset = (currentPage - 1) * pageSize;
      const response = await getAuditLogs(pageSize, offset);
      rows = response.results || [];
      total = response.total || 0;
      console.log("[AuditTable] Loaded audit logs:", rows.length, "of", total);
    } catch (e) {
      error = String(e);
      console.error("[AuditTable] load error:", e);
    } finally {
      loading = false;
    }
  }

  async function exportCSV() {
    exporting = true;
    error = "";
    try {
      const headers = ["id", "actor_user_id", "action", "resource_type", "resource_id", "before", "after", "metadata", "created_at"];
      const rowsForExport = rows.map((row) => [
        row.id,
        row.actor_user_id,
        row.action,
        row.resource_type,
        row.resource_id,
        JSON.stringify(row.before ?? {}),
        JSON.stringify(row.after ?? {}),
        JSON.stringify(row.metadata ?? {}),
        row.created_at,
      ]);
      const csv = [headers, ...rowsForExport]
        .map((line) => line.map((cell) => `"${String(cell ?? "").replaceAll('"', '""')}"`).join(","))
        .join("\n");

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit_logs_page_${currentPage}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      error = "Failed to export CSV: " + String(e);
      console.error("[AuditTable] export error:", e);
    } finally {
      exporting = false;
    }
  }

  async function viewDetails(id) {
    detailLoading = true;
    detailError = "";
    selectedAudit = null;
    try {
      selectedAudit = await getAuditLogById(id);
    } catch (e) {
      detailError = "Failed to load audit details: " + String(e);
    } finally {
      detailLoading = false;
    }
  }

  function closeDetails() {
    selectedAudit = null;
    detailError = "";
    detailLoading = false;
  }

  function nextPage() {
    if ((currentPage * pageSize) < total) {
      currentPage++;
      load();
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      load();
    }
  }
  onMount(load);
</script>

{#if loading} 
  <p>Loading…</p> 
{:else}
  {#if error}
    <p class="admin-state-bad">{error}</p>
  {:else}
    <div class="mb-4 flex justify-between items-center">
      <div class="text-sm">
        Page {currentPage} of {Math.ceil(total / pageSize)} • {total} total logs
      </div>
      <div class="flex gap-2">
        <button 
          on:click={exportCSV}
          disabled={exporting}
          class="admin-btn disabled:opacity-50 flex items-center gap-2"
          title="Export all audit logs to CSV"
        >
          {#if exporting}
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Exporting...
          {:else}
            📥 Export CSV
          {/if}
        </button>
        <button 
          on:click={prevPage} 
          disabled={currentPage === 1}
          class="admin-btn disabled:opacity-50"
        >
          ← Previous
        </button>
        <button 
          on:click={nextPage} 
          disabled={(currentPage * pageSize) >= total}
          class="admin-btn disabled:opacity-50"
        >
          Next →
        </button>
      </div>
    </div>

    <table class="w-full border text-sm">
      <thead>
        <tr class="text-left">
          <th class="py-2">ID</th>
          <th>Actor User ID</th>
          <th>Action</th>
          <th>Resource Type</th>
          <th>Resource ID</th>
          <th>Before</th>
          <th>After</th>
          <th>Metadata</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each rows as log}
          <tr class="border-t">
            <td class="py-2">{log.id}</td>
            <td>{log.actor_user_id ?? "-"}</td>
            <td>{log.action}</td>
            <td>{log.resource_type || "-"}</td>
            <td>{log.resource_id ?? "-"}</td>
            <td class="max-w-40 truncate" title={JSON.stringify(log.before ?? {})}>{log.before ? "present" : "-"}</td>
            <td class="max-w-40 truncate" title={JSON.stringify(log.after ?? {})}>{log.after ? "present" : "-"}</td>
            <td class="max-w-40 truncate" title={JSON.stringify(log.metadata ?? {})}>{log.metadata ? "present" : "-"}</td>
            <td class="text-sm text-slate-400">{formatTimestamp(log.created_at)}</td>
            <td>
              <button
                class="admin-btn"
                on:click={() => viewDetails(log.id)}
              >
                View Details
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
{/if}

{#if selectedAudit || detailLoading || detailError}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    on:click|self={closeDetails}
    on:keydown={(e) => e.key === "Escape" && closeDetails()}
  >
    <div class="bg-slate-900 border border-slate-700 rounded-lg shadow-xl max-w-2xl w-full mx-4 p-5 text-slate-200">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Audit Details</h3>
        <button class="admin-btn" on:click={closeDetails}>Close</button>
      </div>

      {#if detailLoading}
        <p class="text-sm text-slate-400">Loading audit payload…</p>
      {:else if detailError}
        <p class="text-sm admin-state-bad">{detailError}</p>
      {:else if selectedAudit}
        <div class="space-y-3 text-sm">
          <p><strong>ID:</strong> {selectedAudit.id}</p>
          <p><strong>Actor User ID:</strong> {selectedAudit.actor_user_id ?? "-"}</p>
          <p><strong>Action:</strong> {selectedAudit.action}</p>
          <p><strong>Resource:</strong> {selectedAudit.resource_type || "-"} #{selectedAudit.resource_id || ""}</p>
          <p><strong>Created:</strong> {formatTimestamp(selectedAudit.created_at)}</p>

          <div>
            <p class="font-semibold mb-1">Before</p>
            <pre class="bg-slate-900/65 border border-slate-700 p-2 rounded overflow-auto max-h-40 text-xs">{JSON.stringify(selectedAudit.before, null, 2)}</pre>
          </div>
          <div>
            <p class="font-semibold mb-1">After</p>
            <pre class="bg-slate-900/65 border border-slate-700 p-2 rounded overflow-auto max-h-40 text-xs">{JSON.stringify(selectedAudit.after, null, 2)}</pre>
          </div>
          <div>
            <p class="font-semibold mb-1">Metadata</p>
            <pre class="bg-slate-900/65 border border-slate-700 p-2 rounded overflow-auto max-h-40 text-xs">{JSON.stringify(selectedAudit.metadata, null, 2)}</pre>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}
