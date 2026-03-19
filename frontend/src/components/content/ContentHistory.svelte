<!-- src/components/content/ContentHistory.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  export let dohaId: number;

  let versions: any[] = [];
  let open = false;
  let loading = false;
  let error = "";
  let selectedVersion: number | null = null;
  let compareVersion: number | null = null;

  async function load() {
    if (versions.length > 0) return; // Already loaded
    
    loading = true;
    error = "";
    try {
      const response = await api(`/content/doha/${dohaId}/history`);
      versions = Array.isArray(response) ? response : response?.results || [];
    } catch (e: any) {
      error = e?.message || "Failed to load edit history";
      console.error("[ContentHistory] Error:", e);
      versions = [];
    } finally {
      loading = false;
    }
  }

  function toggle() {
    open = !open;
    if (open && versions.length === 0 && !loading) {
      load();
    }
  }

  function selectVersion(versionNum: number) {
    if (selectedVersion === versionNum) {
      selectedVersion = null;
      compareVersion = null;
    } else if (selectedVersion === null) {
      selectedVersion = versionNum;
    } else {
      compareVersion = versionNum;
    }
  }

  function clearSelection() {
    selectedVersion = null;
    compareVersion = null;
  }

  // Simple word-level diff highlighting
  function getDiff(oldText: string, newText: string) {
    if (!oldText || !newText) return { old: oldText || "", new: newText || "" };
    
    const oldWords = oldText.split(/(\s+)/);
    const newWords = newText.split(/(\s+)/);
    
    // Simple comparison (for production, use a proper diff library like diff-match-patch)
    const maxLen = Math.max(oldWords.length, newWords.length);
    let oldHighlighted = '';
    let newHighlighted = '';
    
    for (let i = 0; i < maxLen; i++) {
      const oldWord = oldWords[i] || '';
      const newWord = newWords[i] || '';
      
      if (oldWord !== newWord) {
        if (oldWord) oldHighlighted += `<span class="bg-red-900/40 text-red-300">${oldWord}</span>`;
        if (newWord) newHighlighted += `<span class="bg-green-900/40 text-green-300">${newWord}</span>`;
      } else {
        oldHighlighted += oldWord;
        newHighlighted += newWord;
      }
    }
    
    return { old: oldHighlighted, new: newHighlighted };
  }

  $: selectedVersionData = versions.find(v => v.version_number === selectedVersion);
  $: compareVersionData = versions.find(v => v.version_number === compareVersion);
  $: showDiff = selectedVersion !== null && compareVersion !== null;
  $: diff = showDiff && selectedVersionData && compareVersionData
    ? getDiff(
        compareVersionData.main_text || compareVersionData.text || "",
        selectedVersionData.main_text || selectedVersionData.text || ""
      )
    : null;
</script>

<div class="mt-8 border-t border-slate-700 pt-6">
  <button
    class="text-sm text-cyan-400 hover:text-cyan-300 underline focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
    on:click={toggle}
    aria-expanded={open}
  >
    {open ? "📖 Hide edit history" : "📜 View edit history"}
  </button>

  {#if open}
    <div class="mt-4">
      {#if loading}
        <p class="text-slate-500 text-sm">Loading version history...</p>
      {:else if error}
        <div class="bg-red-900/20 border border-red-700/50 rounded p-3 text-red-400 text-sm">
          {error}
        </div>
      {:else if versions.length === 0}
        <p class="text-slate-500 text-sm">No previous versions available.</p>
      {:else}
        <!-- Diff Viewer Instructions -->
        {#if selectedVersion || compareVersion}
          <div class="mb-4 bg-blue-900/20 border border-blue-700/50 rounded p-3">
            <p class="text-sm text-blue-300 mb-2">
              {#if selectedVersion && !compareVersion}
                <strong>Selected v{selectedVersion}</strong> - Click another version to compare
              {:else if showDiff}
                <strong>Comparing:</strong> v{compareVersion} → v{selectedVersion}
              {/if}
            </p>
            <button 
              on:click={clearSelection}
              class="text-xs text-blue-400 hover:text-blue-300 underline"
            >
              Clear selection
            </button>
          </div>
        {:else}
          <div class="mb-4 bg-slate-800/50 border border-slate-700 rounded p-3 text-xs text-slate-400">
            💡 Click on versions to select and compare changes
          </div>
        {/if}

        <!-- Diff Display -->
        {#if showDiff && diff}
          <div class="mb-6 border-2 border-cyan-700 rounded-lg overflow-hidden">
            <div class="bg-cyan-900/20 px-4 py-2 border-b border-cyan-700">
              <h4 class="text-sm font-semibold text-cyan-300">
                Comparison: v{compareVersion} → v{selectedVersion}
              </h4>
            </div>
            <div class="grid grid-cols-2 divide-x divide-slate-700">
              <div class="p-4 bg-red-900/10">
                <div class="text-xs text-red-400 font-semibold mb-2">v{compareVersion} (Old)</div>
                <div class="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {@html diff.old}
                </div>
              </div>
              <div class="p-4 bg-green-900/10">
                <div class="text-xs text-green-400 font-semibold mb-2">v{selectedVersion} (New)</div>
                <div class="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {@html diff.new}
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Version List -->
        <ul class="space-y-3">
          {#each versions as v, index}
            <!-- svelte-ignore a11y-no-noninteractive-element-to-interactive-role -->
            <li 
              class="bg-slate-800 border rounded-lg p-4 transition-all cursor-pointer
                {selectedVersion === v.version_number ? 'border-cyan-500 bg-cyan-900/20' : 
                 compareVersion === v.version_number ? 'border-yellow-500 bg-yellow-900/20' : 
                 'border-slate-700 hover:border-blue-500'}"
              on:click={() => selectVersion(v.version_number)}
              on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && selectVersion(v.version_number)}
              role="button"
              tabindex="0"
              aria-pressed={selectedVersion === v.version_number || compareVersion === v.version_number}
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <span class="text-xs font-mono bg-blue-900/40 text-blue-300 px-2 py-1 rounded">
                    v{v.version_number}
                  </span>
                  {#if index === 0}
                    <span class="text-xs bg-green-900/40 text-green-300 px-2 py-1 rounded">
                      Current
                    </span>
                  {/if}
                  {#if selectedVersion === v.version_number}
                    <span class="text-xs bg-cyan-900/40 text-cyan-300 px-2 py-1 rounded">
                      Selected
                    </span>
                  {/if}
                  {#if compareVersion === v.version_number}
                    <span class="text-xs bg-yellow-900/40 text-yellow-300 px-2 py-1 rounded">
                      Comparing
                    </span>
                  {/if}
                </div>
                {#if v.created_at}
                  <time class="text-xs text-slate-500">
                    {new Date(v.created_at).toLocaleDateString('en-US', { 
                      year: 'numeric', 
                      month: 'short', 
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </time>
                {/if}
              </div>
              
              <div class="text-sm text-slate-300 leading-relaxed">
                {v.main_text || v.text || "[No content]"}
              </div>
              
              {#if v.meaning}
                <div class="mt-2 text-xs text-slate-500 border-l-2 border-slate-700 pl-3">
                  {v.meaning}
                </div>
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  {/if}
</div>
