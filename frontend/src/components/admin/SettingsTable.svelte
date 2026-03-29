<script lang="ts">
  export let apiBase: string = "";
  import { onMount } from "svelte";
  type SettingRow = { key: string; value: unknown };
  type ImportItemReport = {
    key: string;
    action: string;
    is_critical: boolean;
    errors: string[];
  };
  type ImportSummary = {
    total: number;
    valid: number;
    invalid: number;
    critical: number;
    applyable: number;
  };
  type ImportPreviewResponse = {
    summary: ImportSummary;
    items: ImportItemReport[];
    applied: boolean;
    confirmation_required?: boolean;
    confirmation_text_hint?: string | null;
  };
  type ImportPayload = {
    schema_version: number;
    settings: Array<{ key: string; value: unknown }>;
  };
  type ApiErrorPayload = { detail?: string | { message?: string } };

  let settings: SettingRow[] = [];
  let loading = true;
  let error = "";
  let editingKey: string | null = null;
  let editValue = "";
  let importing = false;
  let importPreview: ImportPreviewResponse | null = null;
  let importPayload: ImportPayload | null = null;
  let importError = "";
  let confirmationText = "";
  let importFileName = "";
  const SETTINGS_SCHEMA_VERSION = 1;
  const CRITICAL_CONFIRM_TEXT = "APPLY CRITICAL SETTINGS";

  function getAuthHeader(): Record<string, string> {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("awadhi_access_token") : null;
      return token ? { Authorization: `Bearer ${token}` } : {};
    } catch {
      return {};
    }
  }

  function getErrorMessage(e: unknown): string {
    return e instanceof Error ? e.message : String(e);
  }

  async function load() {
    loading = true;
    error = "";
    try {
      const res = await fetch(`${apiBase}/admin/system_settings`, { headers: { ...getAuthHeader() }});
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (res.status === 403) {
        error = "Admins only.";
        return;
      }
      if (!res.ok) {
        const errText = await res.text().catch(() => res.statusText);
        throw new Error(`Failed to load settings: ${res.status} ${errText}`);
      }
      settings = (await res.json()) as SettingRow[];
      if (import.meta.env.DEV) console.log("[SettingsTable] Loaded settings:", settings.length);
    } catch (e) {
      error = String(e);
      console.error("[SettingsTable] load error:", e);
    } finally {
      loading = false;
    }
  }

  function startEdit(key: string, currentValue: unknown) {
    editingKey = key;
    editValue = typeof currentValue === "string" ? currentValue : JSON.stringify(currentValue, null, 2);
  }

  function cancelEdit() {
    editingKey = null;
    editValue = "";
  }

  async function saveEdit(key: string) {
    try {
      // Try to parse as JSON first; if it fails, treat as string
      let parsedValue: unknown;
      try {
        parsedValue = JSON.parse(editValue);
      } catch {
        parsedValue = editValue;
      }

      const res = await fetch(`${apiBase}/admin/system_settings/${key}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({ value: parsedValue })
      });

      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (res.status === 403) {
        alert("Admins only.");
        return;
      }
      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail || res.statusText);
      }

      await load();
      editingKey = null;
      editValue = "";
    } catch (e) {
      alert("Update failed: " + getErrorMessage(e));
    }
  }

  async function deleteSetting(key: string) {
    if (!confirm(`Delete setting "${key}"?`)) return;
    try {
      const res = await fetch(`${apiBase}/admin/system_settings/${key}`, {
        method: "DELETE",
        headers: { ...getAuthHeader() }
      });

      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (res.status === 403) {
        alert("Admins only.");
        return;
      }
      if (!res.ok && res.status !== 204) {
        throw new Error("Delete failed");
      }

      await load();
    } catch (e) {
      alert("Delete failed: " + getErrorMessage(e));
    }
  }

  function exportSettings() {
    const exportPayload = {
      schema_version: SETTINGS_SCHEMA_VERSION,
      settings: settings.map((s) => ({ key: s.key, value: s.value })),
    };
    const dataStr = JSON.stringify(exportPayload, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `awadhi_settings_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  async function importSettings(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;

    importing = true;
    importError = "";
    importPreview = null;
    importPayload = null;
    confirmationText = "";
    importFileName = file.name;

    try {
      const text = await file.text();
      const parsed = JSON.parse(text);

      // Support legacy array export while preferring schema-versioned payload.
      const normalized = Array.isArray(parsed)
        ? { schema_version: SETTINGS_SCHEMA_VERSION, settings: parsed }
        : (parsed as { schema_version?: number; settings?: Array<{ key: string; value: unknown }> });

      if (!normalized || !Array.isArray(normalized.settings)) {
        throw new Error("Invalid format: expected { schema_version, settings[] } or legacy settings[] array");
      }

      const previewRes = await fetch(`${apiBase}/admin/system_settings/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({
          schema_version: normalized.schema_version ?? SETTINGS_SCHEMA_VERSION,
          settings: normalized.settings,
          dry_run: true,
        }),
      });

      if (previewRes.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (previewRes.status === 403) {
        throw new Error("Admins only.");
      }

      const previewDataRaw = (await previewRes.json().catch(() => null)) as ImportPreviewResponse | ApiErrorPayload | null;
      if (!previewRes.ok) {
        const detail = (previewDataRaw as ApiErrorPayload | null)?.detail;
        const message = typeof detail === "string" ? detail : detail?.message;
        throw new Error(message || "Failed to preview import");
      }

      importPreview = previewDataRaw as ImportPreviewResponse;
      importPayload = {
        schema_version: normalized.schema_version ?? SETTINGS_SCHEMA_VERSION,
        settings: normalized.settings,
      };
    } catch (e) {
      importError = "Import preview failed: " + getErrorMessage(e);
    } finally {
      importing = false;
      target.value = ''; // Reset input
    }
  }

  async function applyImportedSettings() {
    if (!importPayload) return;

    importing = true;
    importError = "";
    try {
      const res = await fetch(`${apiBase}/admin/system_settings/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({
          schema_version: importPayload.schema_version,
          settings: importPayload.settings,
          dry_run: false,
          confirmation_text: confirmationText,
        }),
      });

      const payloadRaw = (await res.json().catch(() => null)) as ImportPreviewResponse | ApiErrorPayload | null;
      if (!res.ok) {
        const detail = (payloadRaw as ApiErrorPayload | null)?.detail;
        const message = typeof detail === "string" ? detail : detail?.message;
        throw new Error(message || "Failed to apply settings import");
      }

      const payload = payloadRaw as ImportPreviewResponse;

      await load();
      importPreview = payload;
      alert(`Applied ${payload.summary?.applyable ?? 0} setting updates atomically.`);
    } catch (e) {
      importError = "Import apply failed: " + getErrorMessage(e);
    } finally {
      importing = false;
    }
  }

  function resetImportState() {
    importPreview = null;
    importPayload = null;
    importError = "";
    confirmationText = "";
    importFileName = "";
  }

  onMount(load);
</script>

{#if loading}
  <p>Loading settings…</p>
{:else if error}
  <p class="admin-state-bad">{error}</p>
{:else}
  <div class="mb-4 flex flex-col gap-3 lg:flex-row lg:justify-between lg:items-center">
    <p class="text-sm text-slate-300">
      System-wide configuration settings. These control application behavior, feature flags, and limits.
      Values can be JSON objects, arrays, numbers, strings, or booleans.
    </p>
    <div class="flex flex-wrap gap-2">
      <button 
        on:click={exportSettings}
        class="admin-btn text-sm flex items-center gap-2"
      >
        📥 Export JSON
      </button>
      <label class="admin-btn admin-btn-primary text-sm cursor-pointer flex items-center gap-2">
        {#if importing}
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Importing...
        {:else}
          📤 Import JSON
        {/if}
        <input 
          type="file" 
          accept=".json" 
          on:change={importSettings}
          class="hidden"
          disabled={importing}
        />
      </label>
    </div>
  </div>

  {#if importError}
    <div class="mb-4 rounded border border-rose-500/30 bg-rose-900/15 p-3 text-sm text-rose-200">{importError}</div>
  {/if}

  {#if importPreview}
    <div class="mb-5 admin-panel p-4">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-base font-semibold">Import Preview {importFileName ? `• ${importFileName}` : ""}</h3>
        <button class="admin-btn" on:click={resetImportState}>Clear</button>
      </div>

      <div class="mb-3 grid grid-cols-2 gap-2 text-xs md:grid-cols-5">
        <div class="rounded border border-slate-700 p-2">Total: <strong>{importPreview.summary?.total ?? 0}</strong></div>
        <div class="rounded border border-slate-700 p-2">Valid: <strong>{importPreview.summary?.valid ?? 0}</strong></div>
        <div class="rounded border border-slate-700 p-2">Invalid: <strong>{importPreview.summary?.invalid ?? 0}</strong></div>
        <div class="rounded border border-slate-700 p-2">Applyable: <strong>{importPreview.summary?.applyable ?? 0}</strong></div>
        <div class="rounded border border-slate-700 p-2">Critical: <strong>{importPreview.summary?.critical ?? 0}</strong></div>
      </div>

      <div class="admin-table-wrap max-h-64 overflow-auto rounded border border-slate-700">
        <table class="w-full border-collapse text-xs">
          <thead>
            <tr class="border-b border-slate-700 text-left">
              <th class="px-2 py-2">Key</th>
              <th class="px-2 py-2">Action</th>
              <th class="px-2 py-2">Critical</th>
              <th class="px-2 py-2">Errors</th>
            </tr>
          </thead>
          <tbody>
            {#each importPreview.items || [] as item}
              <tr class="border-b border-slate-800">
                <td class="px-2 py-2 font-mono">{item.key}</td>
                <td class="px-2 py-2">{item.action}</td>
                <td class="px-2 py-2">{item.is_critical ? "yes" : "no"}</td>
                <td class="px-2 py-2 text-rose-200">{(item.errors || []).join("; ") || "-"}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      {#if importPreview.confirmation_required}
        <div class="mt-3 rounded border border-amber-500/35 bg-amber-900/12 p-3 text-xs">
          <p class="mb-2 text-amber-200">
            Critical keys detected. To apply changes, type
            <strong>{importPreview.confirmation_text_hint || CRITICAL_CONFIRM_TEXT}</strong>.
          </p>
          <input
            bind:value={confirmationText}
            class="w-full rounded border p-2 font-mono"
            placeholder={importPreview.confirmation_text_hint || CRITICAL_CONFIRM_TEXT}
          />
        </div>
      {/if}

      <div class="mt-3 flex gap-2">
        <button
          class="admin-btn admin-btn-primary disabled:opacity-50"
          on:click={applyImportedSettings}
          disabled={importing || (importPreview.summary?.invalid ?? 0) > 0 || ((importPreview.confirmation_required ?? false) && confirmationText !== (importPreview.confirmation_text_hint || CRITICAL_CONFIRM_TEXT))}
        >
          {importing ? "Applying..." : "Apply Import Atomically"}
        </button>
        <button class="admin-btn" on:click={resetImportState} disabled={importing}>Cancel</button>
      </div>
      <p class="mt-2 text-xs text-slate-500">Apply is atomic: if any setting fails validation, no changes are committed.</p>
    </div>
  {/if}

  {#if settings.length === 0}
    <p class="text-slate-400">No settings configured.</p>
  {:else}
    <div class="admin-table-wrap">
      <table class="w-full border-collapse">
        <thead>
          <tr class="text-left border-b">
            <th class="py-2 px-3 font-semibold">Key</th>
            <th class="py-2 px-3 font-semibold">Value</th>
            <th class="py-2 px-3 font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each settings as s}
            <tr class="border-b border-slate-700/70 hover:bg-slate-800/35">
            <td class="py-3 px-3">
              <code class="text-sm font-mono bg-slate-900/65 px-2 py-1 rounded">{s.key}</code>
            </td>
            <td class="py-3 px-3">
              {#if editingKey === s.key}
                <textarea
                  bind:value={editValue}
                  class="w-full p-2 border rounded font-mono text-sm"
                  rows="3"
                ></textarea>
              {:else}
                <pre class="text-xs bg-slate-900/65 p-2 rounded overflow-auto max-h-32">{JSON.stringify(s.value, null, 2)}</pre>
              {/if}
            </td>
            <td class="py-3 px-3">
              {#if editingKey === s.key}
                <div class="flex gap-2">
                  <button on:click={() => saveEdit(s.key)} class="admin-btn admin-btn-primary">
                    Save
                  </button>
                  <button on:click={cancelEdit} class="admin-btn">
                    Cancel
                  </button>
                </div>
              {:else}
                <div class="flex gap-2">
                  <button on:click={() => startEdit(s.key, s.value)} class="admin-btn">
                    Edit
                  </button>
                  <button on:click={() => deleteSetting(s.key)} class="admin-btn admin-btn-danger">
                    Delete
                  </button>
                </div>
              {/if}
            </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
{/if}
