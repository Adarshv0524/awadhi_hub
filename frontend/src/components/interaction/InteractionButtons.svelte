<!-- src/components/interaction/InteractionButtons.svelte -->
<script>
  import { onMount } from "svelte";
  import { api, ApiError } from "../../lib/api";

  export let contentType; // e.g. "doha" | "dictionary" | "idiom"
  export let contentId;
  export let initialLikes = 0;
  export let initialBookmarks = 0;
  export let initialShares = 0;
  export let activeLike = false;
  export let activeBookmark = false;

  let likes = initialLikes;
  let bookmarks = initialBookmarks;
  let shares = initialShares;
  let likeLoading = false;
  let bookmarkLoading = false;
  let shareLoading = false;
  let reportLoading = false;
  let lastError = null;
  
  // Modal states
  let showShareModal = false;
  let showReportModal = false;
  let shareLink = "";
  let shareCopied = false;
  let reportReason = "spam";
  let reportNote = "";

  // ✅ LocalStorage keys for persisting interaction state
  const getStorageKey = (interaction) => `interaction_${contentType}_${contentId}_${interaction}`;

  // ✅ Load interaction state from localStorage on mount
  onMount(() => {
    if (typeof window !== 'undefined') {
      try {
        const likeKey = getStorageKey('like');
        const bookmarkKey = getStorageKey('bookmark');
        const countsKey = `interaction_${contentType}_${contentId}_counts`;
        
        // Load active states from localStorage
        const storedLike = localStorage.getItem(likeKey);
        const storedBookmark = localStorage.getItem(bookmarkKey);
        const storedCounts = localStorage.getItem(countsKey);
        
        if (storedLike !== null) activeLike = storedLike === 'true';
        if (storedBookmark !== null) activeBookmark = storedBookmark === 'true';
        
        // Load counts if available
        if (storedCounts) {
          const counts = JSON.parse(storedCounts);
          likes = counts.likes ?? initialLikes;
          bookmarks = counts.bookmarks ?? initialBookmarks;
          shares = counts.shares ?? initialShares;
        }
      } catch (e) {
        console.error('[InteractionButtons] Failed to load from localStorage:', e);
      }
    }
  });

  // ✅ Save interaction state to localStorage
  function saveInteractionState() {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(getStorageKey('like'), String(activeLike));
        localStorage.setItem(getStorageKey('bookmark'), String(activeBookmark));
        localStorage.setItem(`interaction_${contentType}_${contentId}_counts`, JSON.stringify({
          likes,
          bookmarks,
          shares
        }));
      } catch (e) {
        console.error('[InteractionButtons] Failed to save to localStorage:', e);
      }
    }
  }

  async function toggleInteraction(interaction) {
    if (!contentType || !contentId) return;
    const isLike = interaction === "like";
    if (isLike) likeLoading = true;
    else bookmarkLoading = true;
    lastError = null;

    // optimistic update
    if (interaction === "like") activeLike = !activeLike;
    if (interaction === "bookmark") activeBookmark = !activeBookmark;

    try {
      const payload = {
        content_type: contentType,
        content_id: Number(contentId),
        interaction,
        metadata: { /* optional client metadata */ },
      };
      const res = await api("/interactions/toggle", { method: "POST", body: payload });

      // server returns updated counts & active
      if (res) {
        if (res.likes_count != null) likes = res.likes_count;
        if (res.bookmarks_count != null) bookmarks = res.bookmarks_count;
        if (typeof res.active === "boolean") {
          if (interaction === "like") activeLike = res.active;
          if (interaction === "bookmark") activeBookmark = res.active;
        }
        
        // ✅ Persist to localStorage after successful toggle
        saveInteractionState();
      }
    } catch (e) {
      // revert optimistic update on failure
      if (interaction === "like") activeLike = !activeLike;
      if (interaction === "bookmark") activeBookmark = !activeBookmark;
      lastError = e instanceof ApiError ? e.message : String(e);
      console.error("[interaction.toggle] error", e);
    } finally {
      likeLoading = false;
      bookmarkLoading = false;
    }
  }

  function openShareModal() {
    shareLink = `${location.origin}/${contentType}/${contentId}`;
    shareCopied = false;
    showShareModal = true;
  }

  async function copyShareLink() {
    try {
      await navigator.clipboard.writeText(shareLink);
      shareCopied = true;
      setTimeout(() => shareCopied = false, 2000);
    } catch (e) {
      console.error("Copy failed", e);
    }
  }

  async function doShare(channel = "copy") {
    shareLoading = true;
    lastError = null;
    try {
      const payload = {
        content_type: contentType,
        content_id: Number(contentId),
        metadata: { channel }
      };
      const res = await api("/interactions/share", { method: "POST", body: payload });
      if (res && res.shares_count != null) {
        shares = res.shares_count;
        // ✅ Persist share count to localStorage
        saveInteractionState();
      }
      
      // Close modal after recording share
      showShareModal = false;
    } catch (e) {
      lastError = e instanceof ApiError ? e.message : String(e);
      console.error("[interaction.share] error", e);
    } finally {
      shareLoading = false;
    }
  }

  function openReportModal() {
    reportReason = "spam";
    reportNote = "";
    showReportModal = true;
  }

  async function submitReport() {
    reportLoading = true;
    lastError = null;
    try {
      const payload = {
        content_type: contentType,
        content_id: Number(contentId),
        reason: reportReason,
        note: reportNote,
        metadata: {}
      };
      const res = await api("/interactions/report", { method: "POST", body: payload });
      if (res && res.report_id) {
        lastError = `Report submitted successfully (ID: ${res.report_id})`;
        showReportModal = false;
        setTimeout(() => (lastError = null), 4000);
      }
    } catch (e) {
      lastError = e instanceof ApiError ? e.message : String(e);
      console.error("[interaction.report] error", e);
    } finally {
      reportLoading = false;
    }
  }
</script>

<div class="flex items-center gap-3 flex-wrap">
  <button class="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:border-cyan-400 transition-all shadow-sm"
    on:click={() => toggleInteraction("like")}
    class:opacity-60={likeLoading}
    class:border-pink-400={activeLike}
    class:bg-pink-900={activeLike}
    aria-pressed={activeLike}
  >
    <span class="text-lg">{activeLike ? "♥" : "♡"}</span>
    <span class="text-sm font-medium">{likes}</span>
  </button>

  <button class="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:border-blue-400 transition-all shadow-sm"
    on:click={() => toggleInteraction("bookmark")}
    class:opacity-60={bookmarkLoading}
    class:border-blue-400={activeBookmark}
    class:bg-blue-900={activeBookmark}
    aria-pressed={activeBookmark}
  >
    <span class="text-lg">{activeBookmark ? "🔖" : "📑"}</span>
    <span class="text-sm font-medium">{bookmarks}</span>
  </button>

  <div class="relative">
    <button class="px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:border-indigo-400 transition-all shadow-sm text-sm font-medium" on:click={openShareModal}>
      Share ({shares})
    </button>
  </div>

  <button class="px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:border-red-400 transition-all shadow-sm text-sm font-medium" on:click={openReportModal}>
    Report
  </button>

  {#if lastError}
    <div class="text-sm text-cyan-400 ml-3 font-medium">{lastError}</div>
  {/if}
</div>

<!-- Share Modal -->
{#if showShareModal}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" on:click={() => showShareModal = false}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="bg-slate-800 border border-slate-600 rounded-lg p-6 max-w-md w-full mx-4 shadow-2xl" on:click|stopPropagation>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Share this {contentType}</h3>
        <button class="text-slate-400 hover:text-slate-200" on:click={() => showShareModal = false}>✕</button>
      </div>
      
      <div class="mb-4">
        <div class="text-sm text-slate-300 mb-2">Copy link:</div>
        <div class="flex gap-2">
          <input 
            type="text" 
            readonly 
            value={shareLink} 
            class="flex-1 bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded text-sm"
          />
          <button 
            on:click={copyShareLink}
            class="px-4 py-2 rounded bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white font-medium text-sm transition-all"
          >
            {shareCopied ? '✓ Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div class="flex gap-3">
        <button 
          on:click={() => doShare('twitter')}
          disabled={shareLoading}
          class="flex-1 px-4 py-2 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 font-medium text-sm transition-all disabled:opacity-50"
        >
          {shareLoading ? 'Sharing...' : 'Share'}
        </button>
        <button 
          on:click={() => showShareModal = false}
          class="px-4 py-2 rounded border border-slate-600 text-slate-300 hover:bg-slate-700 text-sm"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Report Modal -->
{#if showReportModal}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" on:click={() => showReportModal = false}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="bg-slate-800 border border-slate-600 rounded-lg p-6 max-w-md w-full mx-4 shadow-2xl" on:click|stopPropagation>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">Report Content</h3>
        <button class="text-slate-400 hover:text-slate-200" on:click={() => showReportModal = false}>✕</button>
      </div>
      
      <div class="mb-4">
        <div class="text-sm text-slate-300 mb-2">Reason:</div>
        <select 
          bind:value={reportReason}
          class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded"
        >
          <option value="spam">Spam</option>
          <option value="abuse">Abuse or harassment</option>
          <option value="copyright">Copyright violation</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="mb-4">
        <div class="text-sm text-slate-300 mb-2">Additional details (optional):</div>
        <textarea 
          bind:value={reportNote}
          rows="3"
          placeholder="Provide more context..."
          class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded text-sm resize-none"
        ></textarea>
      </div>

      <div class="flex gap-3">
        <button 
          on:click={submitReport}
          disabled={reportLoading}
          class="flex-1 px-4 py-2 rounded bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-400 hover:to-orange-400 text-white font-medium transition-all disabled:opacity-50"
        >
          {reportLoading ? 'Submitting...' : 'Submit Report'}
        </button>
        <button 
          on:click={() => showReportModal = false}
          class="px-4 py-2 rounded border border-slate-600 text-slate-300 hover:bg-slate-700 text-sm"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}
