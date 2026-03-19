<script lang="ts">
  export let apiBase: string = "";
  import { onMount } from "svelte";
  let settings = [];
  let loading = true;
  let error = "";
  let editingKey = null;
  let editValue = "";
  let importing = false;

  function getAuthHeader() {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("awadhi_access_token") : null;
      return token ? { Authorization: `Bearer ${token}` } : {};
    } catch {
      return {};
    }
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
      settings = await res.json();
      if (import.meta.env.DEV) console.log("[SettingsTable] Loaded settings:", settings.length);
    } catch (e) {
      error = String(e);
      console.error("[SettingsTable] load error:", e);
    } finally {
      loading = false;
    }
  }

  function startEdit(key, currentValue) {
    editingKey = key;
    editValue = typeof currentValue === "string" ? currentValue : JSON.stringify(currentValue, null, 2);
  }

  function cancelEdit() {
    editingKey = null;
    editValue = "";
  }

  async function saveEdit(key) {
    try {
      // Try to parse as JSON first; if it fails, treat as string
      let parsedValue;
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
      alert("Update failed: " + (e.message || e));
    }
  }

  async function deleteSetting(key) {
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
      alert("Delete failed: " + (e.message || e));
    }
  }

  function exportSettings() {
    const dataStr = JSON.stringify(settings, null, 2);
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

  async function importSettings(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    
    importing = true;
    try {
      const text = await file.text();
      const imported = JSON.parse(text);
      
      if (!Array.isArray(imported)) {
        throw new Error("Invalid format: expected array of settings");
      }
      
      // Bulk update all settings
      for (const setting of imported) {
        if (!setting.key) continue;
        await fetch(`${apiBase}/admin/system_settings/${setting.key}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json", ...getAuthHeader() },
          body: JSON.stringify({ value: setting.value })
        });
      }
      
      await load();
      alert(`Successfully imported ${imported.length} settings`);
    } catch (e) {
      alert("Import failed: " + (e.message || e));
    } finally {
      importing = false;
      event.target.value = ''; // Reset input
    }
  }

  onMount(load);
</script>

{#if loading}
  <p>Loading settings…</p>
{:else if error}
  <p class="text-red-600">{error}</p>
{:else}
  <div class="mb-4 flex justify-between items-center">
    <p class="text-sm text-stone-600">
      System-wide configuration settings. These control application behavior, feature flags, and limits.
      Values can be JSON objects, arrays, numbers, strings, or booleans.
    </p>
    <div class="flex gap-2">
      <button 
        on:click={exportSettings}
        class="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm flex items-center gap-2"
      >
        📥 Export JSON
      </button>
      <label class="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm cursor-pointer flex items-center gap-2">
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

  {#if settings.length === 0}
    <p class="text-stone-600">No settings configured.</p>
  {:else}
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
          <tr class="border-b hover:bg-stone-50">
            <td class="py-3 px-3">
              <code class="text-sm font-mono bg-stone-100 px-2 py-1 rounded">{s.key}</code>
            </td>
            <td class="py-3 px-3">
              {#if editingKey === s.key}
                <textarea
                  bind:value={editValue}
                  class="w-full p-2 border rounded font-mono text-sm"
                  rows="3"
                ></textarea>
              {:else}
                <pre class="text-xs bg-stone-50 p-2 rounded overflow-auto max-h-32">{JSON.stringify(s.value, null, 2)}</pre>
              {/if}
            </td>
            <td class="py-3 px-3">
              {#if editingKey === s.key}
                <div class="flex gap-2">
                  <button on:click={() => saveEdit(s.key)} class="px-2 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                    Save
                  </button>
                  <button on:click={cancelEdit} class="px-2 py-1 text-sm border rounded hover:bg-stone-100">
                    Cancel
                  </button>
                </div>
              {:else}
                <div class="flex gap-2">
                  <button on:click={() => startEdit(s.key, s.value)} class="px-2 py-1 text-sm border rounded hover:bg-stone-100">
                    Edit
                  </button>
                  <button on:click={() => deleteSetting(s.key)} class="px-2 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700">
                    Delete
                  </button>
                </div>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
{/if}
