<!-- src/components/interaction/InteractionBar.svelte -->
<!-- Lightweight, reusable interaction bar for all content types -->
<script lang="ts">
  import { onMount, onDestroy, tick } from "svelte";
  import {
    toggleInteraction,
    shareContent,
    reportContent,
    type InteractionType,
  } from "../../lib/interactions";

  // Props: content identification
  export let contentType: string; // poetry types, dictionary, idiom, article
  export let contentId: number;
  export let content:
    | {
        likes_count?: number;
        views_count?: number;
        shares_count?: number;
        bookmarks_count?: number;
      }
    | null = null;

  // Props: initial counts from SSR
  export let likes = 0;
  export let views = 0;
  export let bookmarks = 0;
  export let shares = 0;

  function applyContentCounts() {
    likes = content?.likes_count ?? likes ?? 0;
    views = content?.views_count ?? views ?? 0;
    shares = content?.shares_count ?? shares ?? 0;
    bookmarks = content?.bookmarks_count ?? bookmarks ?? 0;
  }

  // Local state: user's interaction status
  let liked = false;
  let bookmarked = false;
  let busy = false;
  let error: string | null = null;
  let showShareMenu = false;
  let showReportModal = false;
  let reportReason = "";
  let reportNote = "";
  let copySuccess = false;
  let shareLink = "";
    const poetryTypes = new Set([
      "poetry",
      "poetry_node",
      "doha",
      "chaupai",
      "sorath",
      "jhulana",
      "savaiya",
      "ghanakshari",
      "chappay",
      "other_poetry",
    ]);

    function contentLabel(type: string): string {
      if (poetryTypes.has((type || "").toLowerCase())) return "poetry";
      return (type || "content").toLowerCase();
    }

    function contentRoute(type: string): string {
      const normalized = (type || "").toLowerCase();
      if (poetryTypes.has(normalized)) return "poetry";
      if (normalized === "idiom") return "idioms";
      if (normalized === "article") return "articles";
      return normalized || "content";
    }

  let reportDialogEl: HTMLDivElement | null = null;
  let reportReasonSelectEl: HTMLSelectElement | null = null;
  let lastFocusedElement: HTMLElement | null = null;

  function safeLog(context: string, err: any) {
    if (!import.meta.env.DEV) return;
    const status = err?.status || err?.code || "unknown";
    console.warn(`[InteractionBar] ${context} (status=${status})`);
  }

  // ✅ Save state to localStorage
  function saveState() {
    if (typeof window !== "undefined") {
      const key = `int_${contentType}_${contentId}`;
      localStorage.setItem(
        key,
        JSON.stringify({ liked, bookmarked, likes, views, bookmarks, shares })
      );
    }
  }

  // ✅ Toggle like or bookmark
  async function toggle(kind: InteractionType) {
    busy = true;
    error = null;

    // Optimistic update
    const wasActive = kind === "like" ? liked : bookmarked;
    if (kind === "like") {
      liked = !liked;
      likes += liked ? 1 : -1;
    } else {
      bookmarked = !bookmarked;
      bookmarks += bookmarked ? 1 : -1;
    }

    try {
      const res = await toggleInteraction(contentType, contentId, kind);

      // Server response is source of truth
      if (kind === "like") {
        liked = res.active;
        likes = res.likes_count;
      } else {
        bookmarked = res.active;
        bookmarks = res.bookmarks_count;
      }

      saveState();
    } catch (e: any) {
      // Revert on error
      if (kind === "like") {
        liked = wasActive;
        likes += wasActive ? 1 : -1;
      } else {
        bookmarked = wasActive;
        bookmarks += wasActive ? 1 : -1;
      }
      error = e.message || "Failed to update";
      safeLog("Toggle failed", e);
    } finally {
      busy = false;
    }
  }

  // ✅ Share content
  async function share(channel: string) {
    showShareMenu = false; // Close menu after selection
    
    try {
      // Map content types to correct routes (some are plural)
      const route = contentRoute(contentType);
      const link = `${window.location.origin}/${route}/${contentId}`;
      const title = document.title;
      const text = `Check out this ${contentLabel(contentType)} on Awadhi New`;

      // Platform-specific sharing
      if (channel === "native" && navigator.share) {
        // Use Web Share API if available (mobile browsers)
        await navigator.share({
          title: title,
          text: text,
          url: link,
        });
      } else if (channel === "whatsapp") {
        window.open(`https://wa.me/?text=${encodeURIComponent(text + " " + link)}`, "_blank");
      } else if (channel === "twitter") {
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(link)}`, "_blank");
      } else if (channel === "facebook") {
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(link)}`, "_blank");
      } else if (channel === "telegram") {
        window.open(`https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent(text)}`, "_blank");
      } else if (channel === "linkedin") {
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(link)}`, "_blank");
      } else if (channel === "email") {
        window.location.href = `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(text + "\n\n" + link)}`;
      } else if (channel === "copy") {
        // Copy link
        await navigator.clipboard.writeText(link);
        copySuccess = true;
        setTimeout(() => { copySuccess = false; }, 2000);
      }

      // Track share on backend
      const res = await shareContent(contentType, contentId, channel);
      shares = res.shares_count ?? shares + 1;
      saveState();
      
    } catch (e: any) {
      // If share fails, at least copy the link
      if (channel !== "copy") {
        try {
          const route = contentRoute(contentType);
          const link = `${window.location.origin}/${route}/${contentId}`;
          await navigator.clipboard.writeText(link);
          copySuccess = true;
          setTimeout(() => { copySuccess = false; }, 2000);
        } catch {
          error = e.message || "Share failed";
        }
      } else {
        error = e.message || "Failed to copy link";
      }
      safeLog("Share failed", e);
    }
  }

  // Toggle share menu and generate link
  function toggleShareMenu() {
    if (!showShareMenu) {
      // Generate share link when opening menu
      const route = contentRoute(contentType);
      shareLink = `${window.location.origin}/${route}/${contentId}`;
    }
    showShareMenu = !showShareMenu;
  }

  // Close share menu when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest(".share-container")) {
      showShareMenu = false;
    }
  }

  onMount(() => {
    if (typeof window !== "undefined") {
      // Restore state
      const key = `int_${contentType}_${contentId}`;
      applyContentCounts();
      const stored = localStorage.getItem(key);
      if (stored) {
        try {
          const data = JSON.parse(stored);
          liked = data.liked ?? false;
          bookmarked = data.bookmarked ?? false;
          likes = data.likes ?? likes;
          views = data.views ?? views;
          bookmarks = data.bookmarks ?? bookmarks;
          shares = data.shares ?? shares;
        } catch (e) {
          safeLog("Failed to restore state", e);
        }
      }

      // Add click outside listener
      document.addEventListener("click", handleClickOutside);
      document.addEventListener("keydown", handleModalKeydown);
    }
  });

  onDestroy(() => {
    if (typeof window !== "undefined") {
      document.removeEventListener("click", handleClickOutside);
      document.removeEventListener("keydown", handleModalKeydown);
    }
  });

  // ✅ Report content
  function openReportModal() {
    if (typeof document !== "undefined") {
      lastFocusedElement = document.activeElement as HTMLElement | null;
    }
    showReportModal = true;
    reportReason = "";
    reportNote = "";
  }

  function closeReportModal() {
    showReportModal = false;
    reportReason = "";
    reportNote = "";
    if (lastFocusedElement) {
      lastFocusedElement.focus();
      lastFocusedElement = null;
    }
  }

  function handleModalKeydown(event: KeyboardEvent) {
    if (!showReportModal || !reportDialogEl) return;

    if (event.key === "Escape") {
      event.preventDefault();
      closeReportModal();
      return;
    }

    if (event.key !== "Tab") return;

    const focusable = Array.from(
      reportDialogEl.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );

    if (focusable.length === 0) {
      event.preventDefault();
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement as HTMLElement | null;

    if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    } else if (event.shiftKey && active === first) {
      event.preventDefault();
      last.focus();
    }
  }

  $: if (showReportModal) {
    tick().then(() => {
      reportReasonSelectEl?.focus();
    });
  }

  async function submitReport() {
    if (!reportReason) {
      alert("Please select a reason");
      return;
    }

    try {
      await reportContent(contentType, contentId, reportReason, reportNote || undefined);
      alert("✅ Report submitted. Thank you!");
      closeReportModal();
    } catch (e: any) {
      error = e.message || "Report failed";
      safeLog("Report failed", e);
    }
  }
</script>

<div class="flex items-center gap-4 text-sm mt-4 flex-wrap">
  <div
    class="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-300"
    aria-label="Views"
    title="Views"
  >
    <span class="text-lg leading-none">👁</span>
    <span class="font-medium leading-none">{views ?? 0}</span>
  </div>

  <!-- Like button -->
  <button
    type="button"
    disabled={busy}
    on:click={() => toggle("like")}
    class="flex items-center gap-2 px-3 py-2 rounded-lg border transition-all hover:scale-105"
    class:border-pink-400={liked}
    class:bg-pink-900={liked}
    class:text-pink-200={liked}
    class:border-slate-600={!liked}
    class:bg-slate-800={!liked}
    class:text-slate-300={!liked}
    class:opacity-50={busy}
    aria-label={liked ? `Unlike this ${contentType}` : `Like this ${contentType}`}
  >
    <span class="text-lg">{liked ? "❤️" : "🤍"}</span>
    <span class="font-medium">{likes}</span>
  </button>

  <!-- Bookmark button -->
  <button
    type="button"
    disabled={busy}
    on:click={() => toggle("bookmark")}
    class="flex items-center gap-2 px-3 py-2 rounded-lg border transition-all hover:scale-105"
    class:border-blue-400={bookmarked}
    class:bg-blue-900={bookmarked}
    class:text-blue-200={bookmarked}
    class:border-slate-600={!bookmarked}
    class:bg-slate-800={!bookmarked}
    class:text-slate-300={!bookmarked}
    class:opacity-50={busy}
    aria-label={bookmarked ? `Remove bookmark from this ${contentType}` : `Bookmark this ${contentType}`}
  >
    <span class="text-lg">{bookmarked ? "🔖" : "📑"}</span>
    <span class="font-medium">{bookmarks}</span>
  </button>

  <!-- Share button with dropdown menu -->
  <div class="relative share-container">
    <button
      type="button"
      on:click={toggleShareMenu}
      class="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-300 transition-all hover:border-indigo-400 hover:scale-105"
      class:border-indigo-400={showShareMenu}
      class:bg-indigo-900={showShareMenu}
      aria-label={`Share this ${contentType}`}
      aria-expanded={showShareMenu}
    >
      <span class="text-lg">🔗</span>
      <span class="font-medium">Share</span>
      <span class="text-xs ml-1">{shares > 0 ? shares : ""}</span>
    </button>

    {#if showShareMenu}
      <div class="absolute bottom-full mb-2 left-0 bg-slate-800 border border-slate-600 rounded-lg shadow-xl p-2 min-w-[280px] z-50 animate-fadeIn">
        <!-- Link Preview Section -->
        <div class="px-3 py-2 mb-2 bg-slate-900/50 rounded border border-slate-700">
          <div class="text-xs text-slate-400 mb-1.5 font-medium">Share Link:</div>
          <div class="flex items-center gap-2">
            <input 
              type="text" 
              readonly 
              value={shareLink}
              class="flex-1 bg-slate-900 text-slate-300 text-xs px-2 py-1.5 rounded border border-slate-700 font-mono select-all"
              on:click={(e) => e.currentTarget.select()}
            />
            <button
              type="button"
              on:click={() => share("copy")}
              class:bg-green-900={copySuccess}
              class:border-green-600={copySuccess}
              class:bg-slate-800={!copySuccess}
              class:border-slate-600={!copySuccess}
              class="px-2 py-1.5 border rounded text-xs font-medium transition-all"
              class:text-green-300={copySuccess}
              class:text-slate-300={!copySuccess}
            >
              {copySuccess ? '✓ Copied' : 'Copy'}
            </button>
          </div>
        </div>
        
        <div class="text-xs text-slate-400 px-3 py-2 font-medium uppercase tracking-wide border-t border-slate-700">Share via</div>
        
        <!-- Native share (mobile) -->
        {#if typeof navigator !== "undefined" && typeof navigator.share === "function"}
          <button
            type="button"
            on:click={() => share("native")}
            class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-700 transition-colors text-left"
          >
            <span class="text-xl">📱</span>
            <span class="text-slate-200">Share...</span>
          </button>
        {/if}

        <!-- WhatsApp -->
        <button
          type="button"
          on:click={() => share("whatsapp")}
          class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-green-900/30 transition-colors text-left"
        >
          <svg class="w-5 h-5" fill="#25D366" viewBox="0 0 24 24">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
          </svg>
          <span class="text-slate-200">WhatsApp</span>
        </button>

        <!-- Twitter/X -->
        <button
          type="button"
          on:click={() => share("twitter")}
          class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-blue-900/30 transition-colors text-left"
        >
          <svg class="w-5 h-5" fill="#1DA1F2" viewBox="0 0 24 24">
            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
          </svg>
          <span class="text-slate-200">Twitter / X</span>
        </button>

        <!-- Facebook -->
        <button
          type="button"
          on:click={() => share("facebook")}
          class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-blue-900/30 transition-colors text-left"
        >
          <svg class="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          <span class="text-slate-200">Facebook</span>
        </button>

        <!-- Telegram -->
        <button
          type="button"
          on:click={() => share("telegram")}
          class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-blue-900/30 transition-colors text-left"
        >
          <svg class="w-5 h-5" fill="#0088cc" viewBox="0 0 24 24">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
          </svg>
          <span class="text-slate-200">Telegram</span>
        </button>

        <!-- LinkedIn -->
        <button
          type="button"
          on:click={() => share("linkedin")}
          class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-blue-900/30 transition-colors text-left"
        >
          <svg class="w-5 h-5" fill="#0A66C2" viewBox="0 0 24 24">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
          </svg>
          <span class="text-slate-200">LinkedIn</span>
        </button>

        <!-- Email -->
        <button
          type="button"
          on:click={() => share("email")}
          class="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-slate-700 transition-colors text-left"
        >
          <span class="text-xl">📧</span>
          <span class="text-slate-200">Email</span>
        </button>
      </div>
    {/if}
  </div>

  <!-- Report button -->
  <button
    type="button"
    on:click={openReportModal}
    class="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-600 bg-slate-800 text-slate-300 transition-all hover:border-red-400 hover:scale-105"
    aria-label={`Report this ${contentType}`}
  >
    <span class="text-lg">⚠️</span>
    <span class="font-medium">Report</span>
  </button>

  {#if error}
    <div class="text-xs text-red-400 ml-2">{error}</div>
  {/if}
</div>

<!-- Report Modal -->
{#if showReportModal}
  <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
    <button
      type="button"
      class="absolute inset-0 w-full h-full cursor-default"
      aria-label="Close report dialog"
      on:click={closeReportModal}
    ></button>
    <div
      class="bg-slate-800 rounded-lg shadow-2xl max-w-md w-full border border-slate-600 relative"
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-modal-title"
      aria-describedby="report-modal-description"
      bind:this={reportDialogEl}
    >
      <div class="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
        <h3 id="report-modal-title" class="text-lg font-semibold text-slate-100">Report Content</h3>
        <button type="button" on:click={closeReportModal} class="text-slate-400 hover:text-slate-200 text-2xl leading-none" aria-label="Close report dialog">&times;</button>
      </div>
      
      <div class="px-6 py-4 space-y-4">
        <p id="report-modal-description" class="text-sm text-slate-400">
          Report inappropriate or incorrect content. This action is reviewed by moderators.
        </p>
        <div>
          <label for="report-reason" class="block text-sm font-medium text-slate-300 mb-2">Reason for reporting</label>
          <select id="report-reason" bind:value={reportReason} bind:this={reportReasonSelectEl} class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-cyan-400 focus:outline-none">
            <option value="">Select a reason...</option>
            <option value="spam">Spam or misleading</option>
            <option value="abuse">Abusive or harmful</option>
            <option value="copyright">Copyright violation</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div>
          <label for="report-note" class="block text-sm font-medium text-slate-300 mb-2">Additional details (optional)</label>
          <textarea 
            id="report-note"
            bind:value={reportNote} 
            placeholder="Provide more context..." 
            rows="3"
            class="w-full bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 rounded focus:border-cyan-400 focus:outline-none resize-none"
          ></textarea>
        </div>
      </div>

      <div class="px-6 py-4 border-t border-slate-700 flex gap-3 justify-end">
        <button 
          type="button"
          on:click={closeReportModal}
          class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded transition-colors"
        >
          Cancel
        </button>
        <button 
          type="button"
          on:click={submitReport}
          class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded transition-colors font-medium"
        >
          Submit Report
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  button:disabled {
    cursor: not-allowed;
  }

  button:not(:disabled):hover {
    cursor: pointer;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.2s ease-out;
  }
</style>
