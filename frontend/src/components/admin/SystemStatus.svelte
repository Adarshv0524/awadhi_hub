<script lang="ts">
  export let apiBase: string = "";
  import { onMount } from "svelte";
  
  let status = {
    authors: { loading: true, count: 0, error: "" },
    users: { loading: true, count: 0, error: "" },
    settings: { loading: true, count: 0, error: "" },
    auditLogs: { loading: true, count: 0, error: "" },
    backend: { loading: true, healthy: false, error: "" },
  };

  function getAuthHeader() {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("awadhi_access_token") : null;
      return token ? { Authorization: `Bearer ${token}` } : {};
    } catch {
      return {};
    }
  }

  async function checkBackend() {
    status.backend.loading = true;
    try {
      const res = await fetch(`${apiBase}/health`);
      status.backend.healthy = res.ok;
      if (!res.ok) {
        status.backend.error = `Backend returned ${res.status}`;
      }
    } catch (e: any) {
      status.backend.healthy = false;
      status.backend.error = e.message || String(e);
    } finally {
      status.backend.loading = false;
    }
  }

  async function checkAuthors() {
    status.authors.loading = true;
    try {
      const res = await fetch(`${apiBase}/authors?limit=1`, { headers: { ...getAuthHeader() }});
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      status.authors.count = Array.isArray(data) ? data.length : 0;
    } catch (e: any) {
      status.authors.error = e.message || String(e);
    } finally {
      status.authors.loading = false;
    }
  }

  async function checkUsers() {
    status.users.loading = true;
    try {
      const res = await fetch(`${apiBase}/admin/users?limit=1`, { headers: { ...getAuthHeader() }});
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      status.users.count = Array.isArray(data) ? data.length : 0;
    } catch (e: any) {
      status.users.error = e.message || String(e);
    } finally {
      status.users.loading = false;
    }
  }

  async function checkSettings() {
    status.settings.loading = true;
    try {
      const res = await fetch(`${apiBase}/admin/system_settings`, { headers: { ...getAuthHeader() }});
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      status.settings.count = Array.isArray(data) ? data.length : 0;
    } catch (e: any) {
      status.settings.error = e.message || String(e);
    } finally {
      status.settings.loading = false;
    }
  }

  async function checkAuditLogs() {
    status.auditLogs.loading = true;
    try {
      const res = await fetch(`${apiBase}/admin/audit_logs?limit=1`, { headers: { ...getAuthHeader() }});
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      status.auditLogs.count = data?.total || (data?.results?.length ?? 0);
    } catch (e: any) {
      status.auditLogs.error = e.message || String(e);
    } finally {
      status.auditLogs.loading = false;
    }
  }

  onMount(() => {
    checkBackend();
    checkAuthors();
    checkUsers();
    checkSettings();
    checkAuditLogs();
  });
</script>

<div class="p-4 border rounded bg-stone-50">
  <h3 class="font-semibold mb-3">System Status</h3>
  <div class="space-y-2 text-sm">
    <div class="flex justify-between items-center">
      <span>Backend Health:</span>
      {#if status.backend.loading}
        <span class="text-stone-500">Checking...</span>
      {:else if status.backend.healthy}
        <span class="text-green-600 font-medium">✓ Healthy</span>
      {:else}
        <span class="text-red-600 font-medium">✗ {status.backend.error}</span>
      {/if}
    </div>

    <div class="flex justify-between items-center">
      <span>Authors Endpoint:</span>
      {#if status.authors.loading}
        <span class="text-stone-500">Checking...</span>
      {:else if status.authors.error}
        <span class="text-red-600 text-xs">{status.authors.error}</span>
      {:else}
        <span class="text-green-600">✓ Working</span>
      {/if}
    </div>

    <div class="flex justify-between items-center">
      <span>Admin Users:</span>
      {#if status.users.loading}
        <span class="text-stone-500">Checking...</span>
      {:else if status.users.error}
        <span class="text-red-600 text-xs">{status.users.error}</span>
      {:else}
        <span class="text-green-600">✓ Working</span>
      {/if}
    </div>

    <div class="flex justify-between items-center">
      <span>System Settings:</span>
      {#if status.settings.loading}
        <span class="text-stone-500">Checking...</span>
      {:else if status.settings.error}
        <span class="text-red-600 text-xs">{status.settings.error}</span>
      {:else}
        <span class="text-green-600">✓ {status.settings.count} settings</span>
      {/if}
    </div>

    <div class="flex justify-between items-center">
      <span>Audit Logs:</span>
      {#if status.auditLogs.loading}
        <span class="text-stone-500">Checking...</span>
      {:else if status.auditLogs.error}
        <span class="text-red-600 text-xs">{status.auditLogs.error}</span>
      {:else}
        <span class="text-green-600">✓ {status.auditLogs.count} logs</span>
      {/if}
    </div>
  </div>
  
  <div class="mt-3 pt-3 border-t text-xs text-stone-600">
    <div><strong>API Base:</strong> {apiBase || "(not set)"}</div>
    <div><strong>Auth Token:</strong> {typeof window !== "undefined" && localStorage.getItem("awadhi_access_token") ? "Present" : "Missing"}</div>
  </div>
</div>
