<script>
  // apiBase prop kept for backward compatibility but unused (uses admin.ts wrapper)
  export let apiBase = "";
  import { onMount } from "svelte";
  import { getAuditLogs, exportAuditLogsCSV } from "../../lib/admin";
  
  let rows = [];
  let loading = true;
  let error = "";
  let currentPage = 1;
  let pageSize = 50;
  let total = 0;
  let exporting = false;

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
      await exportAuditLogsCSV();
    } catch (e) {
      error = "Failed to export CSV: " + String(e);
      console.error("[AuditTable] export error:", e);
    } finally {
      exporting = false;
    }
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
    <p class="text-red-600">{error}</p> 
  {:else}
    <div class="mb-4 flex justify-between items-center">
      <div class="text-sm">
        Page {currentPage} of {Math.ceil(total / pageSize)} • {total} total logs
      </div>
      <div class="flex gap-2">
        <button 
          on:click={exportCSV}
          disabled={exporting}
          class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-500 disabled:opacity-50 flex items-center gap-2"
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
          class="px-3 py-1 bg-gray-600 text-white rounded disabled:opacity-50"
        >
          ← Previous
        </button>
        <button 
          on:click={nextPage} 
          disabled={(currentPage * pageSize) >= total}
          class="px-3 py-1 bg-gray-600 text-white rounded disabled:opacity-50"
        >
          Next →
        </button>
      </div>
    </div>

    <table class="w-full border text-sm">
      <thead>
        <tr class="text-left">
          <th class="py-2">ID</th>
          <th>User</th>
          <th>Action</th>
          <th>Resource</th>
          <th>IP</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {#each rows as log}
          <tr class="border-t">
            <td class="py-2">{log.id}</td>
            <td>{log.username || log.user_id || "-"}</td>
            <td>{log.action}</td>
            <td>{log.resource_type || "-"} #{log.resource_id || ""}</td>
            <td>{log.ip_address || "-"}</td>
            <td class="text-sm text-stone-600">{new Date(log.created_at).toLocaleString()}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
{/if}
