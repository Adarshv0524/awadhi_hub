<script lang="ts">
  import { onMount } from "svelte";
  import { getMe } from "../../lib/auth";
  import { getUserBookmarks, getUserLikes } from "../../lib/interactions";
  import { api } from "../../lib/api";

  let user: any = null;
  let submissions: any[] = [];
  let bookmarks: any[] = [];
  let likes: any[] = [];
  let loading = true;
  let error = "";
  
  // Engagement metrics
  let engagementMetrics = {
    totalViews: 0,
    totalLikes: 0,
    totalShares: 0,
    totalBookmarks: 0,
  };
  let metricsLoading = false;
  
  // Tab state
  let activeTab: "submissions" | "bookmarks" | "likes" = "submissions";
  
  // Submissions filters
  let statusFilter: string = "all"; // all, draft, pending, approved, rejected
  
  // Pagination
  let bookmarksPage = 0;
  let bookmarksLimit = 10;
  let bookmarksTotal = 0;

  let likesPage = 0;
  let likesLimit = 10;
  let likesTotal = 0;
  let likesLoaded = false;
  let likesLoading = false;
  
  // Helper to convert singular content_type to plural route
  function getContentRoute(contentType: string): string {
    const routes: Record<string, string> = {
      'idiom': 'idioms',
      'article': 'articles',
      'dictionary': 'dictionary',
      'doha': 'doha'
    };
    return routes[contentType] || contentType;
  }

  function getContentHref(item: any): string {
    if (item?.content_path) return item.content_path;
    return `/${getContentRoute(item?.content_type)}/${item?.content_id}`;
  }

  function isLegacyType(contentType: string): boolean {
    return contentType === "doha" || contentType === "dictionary" || contentType === "idiom" || contentType === "article";
  }

  onMount(async () => {
    loading = true;
    error = "";
    try {
      user = await getMe();
      if (!user) {
        error = "Not authenticated. Please log in.";
        return;
      }

      // Load independent dashboard datasets in parallel to avoid startup waterfall.
      await Promise.all([loadSubmissions(), loadBookmarks()]);

      // Engagement metrics depend on loaded submissions/bookmarks.
      await loadEngagementMetrics();

    } catch (e: any) {
      error = e?.message || "Failed to load dashboard";
      console.error("[Dashboard] Error:", e);
    } finally {
      loading = false;
    }
  });
  
  async function loadSubmissions() {
    try {
      const result = await api("/submissions/me?limit=100");
      submissions = Array.isArray(result) ? result : result?.results || [];
    } catch (e) {
      console.error("[Dashboard] Failed to load submissions:", e);
      submissions = [];
    }
  }
  
  async function loadBookmarks() {
    try {
      const response = await getUserBookmarks(user.id, bookmarksLimit, bookmarksPage * bookmarksLimit);
      bookmarks = response?.results || response || [];
      bookmarksTotal = response?.total_count ?? response?.count ?? bookmarks.length;
    } catch (e) {
      console.error("[Dashboard] Failed to load bookmarks:", e);
      bookmarks = [];
      bookmarksTotal = 0;
    }
  }

  async function loadLikes() {
    if (!user) return;
    likesLoading = true;
    try {
      const response = await getUserLikes(user.id, likesLimit, likesPage * likesLimit);
      likes = response?.results || response || [];
      likesTotal = response?.total_count ?? response?.count ?? likes.length;
      likesLoaded = true;
    } catch (e) {
      console.error("[Dashboard] Failed to load likes:", e);
      likes = [];
      likesTotal = 0;
      likesLoaded = true;
    } finally {
      likesLoading = false;
    }
  }
  
  async function loadEngagementMetrics() {
    metricsLoading = true;
    try {
      // Calculate metrics from approved submissions
      const approvedSubmissions = submissions.filter(s => s.status === "approved");
      
      // Sum up engagement stats from submissions
      // Note: These fields may not exist yet - backend needs to add them
      let totalViews = 0;
      let totalLikes = 0;
      let totalShares = 0;
      
      // Cap fan-out per dashboard render and run in parallel.
      const statsTargets = approvedSubmissions.slice(0, 20);
      const statsResponses = await Promise.all(
        statsTargets.map(async (sub) => {
          const contentType = sub.content_type;
          const contentId = sub.id;
          const route = getContentRoute(contentType);
          try {
            return await api(`/${route}/${contentId}`);
          } catch {
            return null;
          }
        })
      );

      for (const content of statsResponses) {
        if (!content) continue;
        totalViews += content.views_count || content.views || 0;
        totalLikes += content.likes_count || content.likes || 0;
        totalShares += content.shares_count || content.shares || 0;
      }
      
      engagementMetrics = {
        totalViews,
        totalLikes,
        totalShares,
        totalBookmarks: bookmarksTotal,
      };
    } catch (e) {
      console.error("[Dashboard] Failed to load engagement metrics:", e);
    } finally {
      metricsLoading = false;
    }
  }
  
  async function changeBookmarksPage(newPage: number) {
    bookmarksPage = newPage;
    await loadBookmarks();
  }

  async function changeLikesPage(newPage: number) {
    likesPage = newPage;
    await loadLikes();
  }
  
  function formatDate(dateStr: string) {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  }
  
  function getStatusBadgeClass(status: string) {
    const classes = {
      draft: "bg-slate-700 text-slate-300",
      pending: "bg-yellow-900 text-yellow-300 border-yellow-700",
      approved: "bg-green-900 text-green-300 border-green-700",
      rejected: "bg-red-900 text-red-300 border-red-700"
    };
    return classes[status as keyof typeof classes] || "bg-slate-700 text-slate-300";
  }
  
  $: filteredSubmissions = statusFilter === "all" 
    ? submissions 
    : submissions.filter(s => s.status === statusFilter);
    
  $: bookmarksTotalPages = Math.ceil(bookmarksTotal / bookmarksLimit);
  $: likesTotalPages = Math.ceil(likesTotal / likesLimit);

  $: if (activeTab === "likes" && user && !likesLoaded && !likesLoading) {
    loadLikes();
  }
</script>

<div class="max-w-5xl mx-auto px-4">
  {#if loading}
    <div class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
      <p class="text-cyan-400 text-lg mt-4">Loading your dashboard…</p>
    </div>
  {:else if error}
    <div class="bg-red-950 border border-red-800 rounded-lg p-6 text-center">
      <p class="text-red-300 font-semibold">{error}</p>
      <a href="/login" class="mt-4 inline-block text-cyan-400 hover:text-cyan-300 underline">
        Go to Login
      </a>
    </div>
  {:else if user}
    <!-- Welcome Header -->
    <div class="mb-8">
      <h2 class="text-4xl font-serif font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent mb-2">
        Welcome back, {user.username || user.email}
      </h2>
      <div class="flex items-center gap-4 flex-wrap">
        <span class="text-slate-400">Role:</span>
        <span 
          class="px-3 py-1 rounded-lg font-semibold text-sm border"
          class:bg-red-900={user.role === 'admin'}
          class:text-red-200={user.role === 'admin'}
          class:border-red-700={user.role === 'admin'}
          class:bg-purple-900={user.role === 'moderator'}
          class:text-purple-200={user.role === 'moderator'}
          class:border-purple-700={user.role === 'moderator'}
          class:bg-blue-900={user.role === 'contributor'}
          class:text-blue-200={user.role === 'contributor'}
          class:border-blue-700={user.role === 'contributor'}
          class:bg-slate-700={user.role === 'registered'}
          class:text-slate-200={user.role === 'registered'}
          class:border-slate-600={user.role === 'registered'}
        >
          {user.role}
        </span>
        <span class="text-slate-500">•</span>
        <span class="text-slate-400">
          Joined {user.created_at ? formatDate(user.created_at) : "recently"}
        </span>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mb-8 flex gap-3 flex-wrap">
      <a
        href="/submit"
        class="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white rounded-lg font-medium transition-all shadow-lg"
      >
        + New Submission
      </a>
      <a
        href="/me/edit"
        class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
      >
        Edit Profile
      </a>
      {#if user.role === "moderator" || user.role === "admin"}
        <a
          href="/moderation"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors"
        >
          Moderation Queue
        </a>
      {/if}
      {#if user.role === "admin"}
        <a
          href="/admin"
          class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg font-medium transition-colors"
        >
          Admin Panel
        </a>
      {/if}
    </div>

    <!-- Engagement Metrics KPI Cards -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold text-slate-200 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
        Your Engagement Stats
      </h3>
      
      {#if metricsLoading}
        <div class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-cyan-400 border-t-transparent"></div>
          <p class="text-sm text-slate-400 mt-2">Loading metrics...</p>
        </div>
      {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Total Views -->
          <div class="bg-gradient-to-br from-blue-900/50 to-blue-800/30 border border-blue-700/50 rounded-lg p-5 hover:scale-105 transition-transform">
            <div class="flex items-center justify-between mb-2">
              <div class="text-blue-300 text-sm font-medium uppercase tracking-wide">Views</div>
              <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
            </div>
            <div class="text-3xl font-bold text-blue-100">{engagementMetrics.totalViews.toLocaleString()}</div>
            <p class="text-xs text-blue-300/70 mt-1">Total content views</p>
          </div>

          <!-- Total Likes -->
          <div class="bg-gradient-to-br from-pink-900/50 to-pink-800/30 border border-pink-700/50 rounded-lg p-5 hover:scale-105 transition-transform">
            <div class="flex items-center justify-between mb-2">
              <div class="text-pink-300 text-sm font-medium uppercase tracking-wide">Likes</div>
              <svg class="w-6 h-6 text-pink-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <div class="text-3xl font-bold text-pink-100">{engagementMetrics.totalLikes.toLocaleString()}</div>
            <p class="text-xs text-pink-300/70 mt-1">Hearts received</p>
          </div>

          <!-- Total Shares -->
          <div class="bg-gradient-to-br from-green-900/50 to-green-800/30 border border-green-700/50 rounded-lg p-5 hover:scale-105 transition-transform">
            <div class="flex items-center justify-between mb-2">
              <div class="text-green-300 text-sm font-medium uppercase tracking-wide">Shares</div>
              <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
              </svg>
            </div>
            <div class="text-3xl font-bold text-green-100">{engagementMetrics.totalShares.toLocaleString()}</div>
            <p class="text-xs text-green-300/70 mt-1">Times shared</p>
          </div>

          <!-- Total Bookmarks (from other users) -->
          <div class="bg-gradient-to-br from-yellow-900/50 to-yellow-800/30 border border-yellow-700/50 rounded-lg p-5 hover:scale-105 transition-transform">
            <div class="flex items-center justify-between mb-2">
              <div class="text-yellow-300 text-sm font-medium uppercase tracking-wide">Saved</div>
              <svg class="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path>
              </svg>
            </div>
            <div class="text-3xl font-bold text-yellow-100">{engagementMetrics.totalBookmarks.toLocaleString()}</div>
            <p class="text-xs text-yellow-300/70 mt-1">Your bookmarks</p>
          </div>
        </div>
        
        <div class="mt-4 p-3 bg-cyan-900/20 border border-cyan-800/30 rounded-lg">
          <p class="text-xs text-cyan-300 flex items-start gap-2">
            <svg class="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>Engagement metrics show aggregated stats from your approved public content only. Private drafts and pending submissions are excluded.</span>
          </p>
        </div>
      {/if}
    </div>

    <!-- Tab Navigation -->
    <div class="mb-6 border-b border-slate-700">
      <div class="flex gap-1">
        <button
          on:click={() => activeTab = "submissions"}
          class="px-6 py-3 font-medium transition-all relative"
          class:text-cyan-400={activeTab === "submissions"}
          class:text-slate-400={activeTab !== "submissions"}
        >
          Submissions
          <span class="ml-2 px-2 py-0.5 bg-slate-700 rounded-full text-xs">
            {submissions.length}
          </span>
          {#if activeTab === "submissions"}
            <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
          {/if}
        </button>
        
        <button
          on:click={() => activeTab = "bookmarks"}
          class="px-6 py-3 font-medium transition-all relative"
          class:text-cyan-400={activeTab === "bookmarks"}
          class:text-slate-400={activeTab !== "bookmarks"}
        >
          Bookmarks
          <span class="ml-2 px-2 py-0.5 bg-slate-700 rounded-full text-xs">
            {bookmarksTotal}
          </span>
          {#if activeTab === "bookmarks"}
            <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
          {/if}
        </button>
        
        <button
          on:click={() => activeTab = "likes"}
          class="px-6 py-3 font-medium transition-all relative"
          class:text-cyan-400={activeTab === "likes"}
          class:text-slate-400={activeTab !== "likes"}
        >
          Likes
          <span class="ml-2 px-2 py-0.5 bg-slate-700 rounded-full text-xs">
            {likesTotal}
          </span>
          {#if activeTab === "likes"}
            <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
          {/if}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="bg-slate-800/50 border border-slate-700 rounded-lg p-6 min-h-[400px]">
      {#if activeTab === "submissions"}
        <!-- Submissions Tab -->
        <div class="mb-6 flex items-center justify-between flex-wrap gap-4">
          <h3 class="text-xl font-semibold text-cyan-400">My Submissions</h3>
          
          <!-- Status Filter -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-slate-400">Filter:</span>
            <select 
              bind:value={statusFilter}
              class="bg-slate-900 border border-slate-600 text-slate-200 px-3 py-1.5 rounded text-sm focus:border-cyan-400 focus:outline-none"
            >
              <option value="all">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="pending">Pending Review</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        {#if filteredSubmissions.length === 0}
          <!-- Empty State -->
          <div class="text-center py-16">
            <div class="text-6xl mb-4">📝</div>
            <h4 class="text-xl font-semibold text-slate-300 mb-2">
              {statusFilter === "all" ? "No submissions yet" : `No ${statusFilter} submissions`}
            </h4>
            <p class="text-slate-400 mb-6 max-w-md mx-auto">
              {statusFilter === "all" 
                ? "Start contributing to Awadhi New by creating your first submission." 
                : `You don't have any submissions with status "${statusFilter}".`}
            </p>
            <a
              href="/submit"
              class="inline-block px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white rounded-lg font-medium transition-all shadow-lg"
            >
              Create First Submission
            </a>
          </div>
        {:else}
          <!-- Submissions List -->
          <ul class="space-y-3">
            {#each filteredSubmissions as s}
              <li class="border border-slate-600 bg-slate-900 rounded-lg p-4 hover:border-cyan-500 transition-colors">
                <div class="flex justify-between items-start gap-4">
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <span class="px-3 py-1 bg-blue-900/50 text-blue-300 rounded text-xs font-semibold uppercase border border-blue-700">
                        {s.content_type}
                      </span>
                      <span 
                        class="px-3 py-1 rounded text-xs font-semibold uppercase border {getStatusBadgeClass(s.status)}"
                      >
                        {s.status}
                      </span>
                      {#if s.version && s.version > 1}
                        <span class="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-xs border border-purple-700" title="Version number">
                          v{s.version}
                        </span>
                      {/if}
                    </div>
                    
                    <p class="text-slate-200 text-sm mb-2 line-clamp-2">
                      {s.main_text || "(No text)"}
                    </p>
                    
                    {#if s.meaning}
                      <p class="text-slate-400 text-xs line-clamp-1">
                        {s.meaning}
                      </p>
                    {/if}
                    
                    <div class="mt-3 flex items-center gap-4 text-xs text-slate-500">
                      <span>Created: {s.created_at ? formatDate(s.created_at) : "—"}</span>
                      {#if s.updated_at && s.updated_at !== s.created_at}
                        <span>Updated: {formatDate(s.updated_at)}</span>
                      {/if}
                    </div>
                  </div>
                  
                  <a
                    href={`/submissions/${s.id}`}
                    class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-sm font-medium transition-colors whitespace-nowrap"
                  >
                    View Details
                  </a>
                </div>
              </li>
            {/each}
          </ul>
          
          <div class="mt-6 text-center text-sm text-slate-400">
            Showing {filteredSubmissions.length} of {submissions.length} submission{submissions.length !== 1 ? 's' : ''}
          </div>
        {/if}
        
      {:else if activeTab === "bookmarks"}
        <!-- Bookmarks Tab -->
        <h3 class="text-xl font-semibold text-cyan-400 mb-6">My Bookmarks</h3>

        {#if bookmarks.length === 0}
          <!-- Empty State -->
          <div class="text-center py-16">
            <div class="text-6xl mb-4">🔖</div>
            <h4 class="text-xl font-semibold text-slate-300 mb-2">No bookmarks yet</h4>
            <p class="text-slate-400 mb-6 max-w-md mx-auto">
              Start bookmarking content you want to save for later. Browse our collection to find interesting dohas, words, idioms, and articles.
            </p>
            <div class="flex justify-center gap-3 flex-wrap">
              <a href="/doha" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors">
                Browse Doha
              </a>
              <a href="/dictionary" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors">
                Browse Dictionary
              </a>
              <a href="/idioms" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors">
                Browse Idioms
              </a>
              <a href="/articles" class="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-sm font-medium transition-colors">
                Browse Articles
              </a>
            </div>
          </div>
        {:else}
          <!-- Bookmarks List -->
          <ul class="space-y-3">
            {#each bookmarks as b}
              <li class="border border-slate-600 bg-slate-900 rounded-lg p-4 hover:border-indigo-500 transition-colors">
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <a
                      href={getContentHref(b)}
                      class="text-cyan-400 hover:text-cyan-300 font-medium text-lg inline-block mb-2 hover:underline"
                    >
                      {b.content_title || `${b.content_type} #${b.content_id}`}
                    </a>
                    <div class="text-xs text-slate-500">
                      Bookmarked: {b.created_at ? formatDate(b.created_at) : "—"}
                    </div>
                  </div>
                  <span
                    class="px-3 py-1 rounded text-xs font-semibold uppercase border"
                    class:bg-cyan-900={b.content_type === 'doha'}
                    class:text-cyan-300={b.content_type === 'doha'}
                    class:border-cyan-700={b.content_type === 'doha'}
                    class:bg-blue-900={b.content_type === 'dictionary'}
                    class:text-blue-300={b.content_type === 'dictionary'}
                    class:border-blue-700={b.content_type === 'dictionary'}
                    class:bg-indigo-900={b.content_type === 'idiom'}
                    class:text-indigo-300={b.content_type === 'idiom'}
                    class:border-indigo-700={b.content_type === 'idiom'}
                    class:bg-purple-900={b.content_type === 'article'}
                    class:text-purple-300={b.content_type === 'article'}
                    class:border-purple-700={b.content_type === 'article'}
                    class:bg-emerald-900={!isLegacyType(b.content_type)}
                    class:text-emerald-300={!isLegacyType(b.content_type)}
                    class:border-emerald-700={!isLegacyType(b.content_type)}
                  >
                    {b.content_type}
                  </span>
                </div>
              </li>
            {/each}
          </ul>
          
          <!-- Pagination -->
          {#if bookmarksTotalPages > 1}
            <div class="mt-6 flex justify-center items-center gap-2">
              <button
                on:click={() => changeBookmarksPage(bookmarksPage - 1)}
                disabled={bookmarksPage === 0}
                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
              >
                Previous
              </button>
              
              <span class="text-sm text-slate-400">
                Page {bookmarksPage + 1} of {bookmarksTotalPages}
              </span>
              
              <button
                on:click={() => changeBookmarksPage(bookmarksPage + 1)}
                disabled={bookmarksPage >= bookmarksTotalPages - 1}
                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
              >
                Next
              </button>
            </div>
          {/if}
        {/if}
        
      {:else if activeTab === "likes"}
        <!-- Likes Tab -->
        <h3 class="text-xl font-semibold text-cyan-400 mb-6">My Likes</h3>

        {#if likesLoading}
          <div class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-pink-500 border-t-transparent"></div>
            <p class="text-pink-300 mt-3">Loading your likes...</p>
          </div>
        {:else if likes.length === 0}
          <div class="text-center py-16">
            <div class="text-6xl mb-4">❤️</div>
            <h4 class="text-xl font-semibold text-slate-300 mb-2">No likes yet</h4>
            <p class="text-slate-400 mb-6 max-w-md mx-auto">
              You haven't liked any content yet.
            </p>
            <a href="/search" class="px-4 py-2 bg-pink-600 hover:bg-pink-500 text-white rounded-lg text-sm font-medium transition-colors">
              Explore Content
            </a>
          </div>
        {:else}
          <ul class="space-y-3">
            {#each likes as l}
              <li class="border border-slate-600 bg-slate-900 rounded-lg p-4 hover:border-pink-500 transition-colors">
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <a
                      href={getContentHref(l)}
                      class="text-cyan-400 hover:text-cyan-300 font-medium text-lg inline-block mb-2 hover:underline"
                    >
                      {l.content_title || `${l.content_type} #${l.content_id}`}
                    </a>
                    {#if l.content_snippet}
                      <p class="text-slate-300 text-sm line-clamp-2 mb-2">{l.content_snippet}</p>
                    {/if}
                    <div class="text-xs text-slate-500">
                      Liked: {l.created_at ? formatDate(l.created_at) : "—"}
                    </div>
                  </div>
                  <span
                    class="px-3 py-1 rounded text-xs font-semibold uppercase border"
                    class:bg-cyan-900={l.content_type === 'doha'}
                    class:text-cyan-300={l.content_type === 'doha'}
                    class:border-cyan-700={l.content_type === 'doha'}
                    class:bg-blue-900={l.content_type === 'dictionary'}
                    class:text-blue-300={l.content_type === 'dictionary'}
                    class:border-blue-700={l.content_type === 'dictionary'}
                    class:bg-indigo-900={l.content_type === 'idiom'}
                    class:text-indigo-300={l.content_type === 'idiom'}
                    class:border-indigo-700={l.content_type === 'idiom'}
                    class:bg-purple-900={l.content_type === 'article'}
                    class:text-purple-300={l.content_type === 'article'}
                    class:border-purple-700={l.content_type === 'article'}
                    class:bg-emerald-900={!isLegacyType(l.content_type)}
                    class:text-emerald-300={!isLegacyType(l.content_type)}
                    class:border-emerald-700={!isLegacyType(l.content_type)}
                  >
                    {l.content_type}
                  </span>
                </div>
              </li>
            {/each}
          </ul>

          {#if likesTotalPages > 1}
            <div class="mt-6 flex justify-center items-center gap-2">
              <button
                on:click={() => changeLikesPage(likesPage - 1)}
                disabled={likesPage === 0}
                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
              >
                Previous
              </button>

              <span class="text-sm text-slate-400">
                Page {likesPage + 1} of {likesTotalPages}
              </span>

              <button
                on:click={() => changeLikesPage(likesPage + 1)}
                disabled={likesPage >= likesTotalPages - 1}
                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
              >
                Next
              </button>
            </div>
          {/if}
        {/if}
      {/if}
    </div>
  {/if}
</div>
