<!-- src/components/user/UserStats.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../../lib/api";

  export let username: string;
  export let isOwnProfile: boolean = false;

  let loading = true;
  let error: string | null = null;
  let stats: any = null;

  async function loadStats() {
    loading = true;
    error = null;
    try {
      // Try to fetch user stats from API
      stats = await api(`/users/${username}/stats`);
    } catch (e: any) {
      // If endpoint doesn't exist yet, use dummy data
      if (e?.status === 404) {
        stats = {
          approved_submissions: 0,
          pending_submissions: 0,
          total_submissions: 0,
          likes_received: 0,
          contributions_by_type: {
            doha: 0,
            dictionary: 0,
            idiom: 0,
            article: 0
          }
        };
      } else {
        error = "Failed to load stats";
        console.error("[UserStats] Error:", e);
      }
    } finally {
      loading = false;
    }
  }

  onMount(loadStats);
</script>

<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
  {#if loading}
    {#each Array(4) as _}
      <div class="bg-slate-800 border border-slate-700 rounded-lg p-4 animate-pulse">
        <div class="h-4 bg-slate-700 rounded w-20 mb-2"></div>
        <div class="h-8 bg-slate-700 rounded w-12"></div>
      </div>
    {/each}
  {:else if error}
    <div class="col-span-2 sm:col-span-4 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-400 text-sm">
      {error}
    </div>
  {:else if stats}
    <!-- Approved Submissions (Public) -->
    <div class="bg-gradient-to-br from-green-900/30 to-green-800/20 border border-green-700 rounded-lg p-4">
      <div class="text-xs text-green-400 mb-1 flex items-center gap-1">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        <span>Approved</span>
      </div>
      <div class="text-2xl font-bold text-green-400">{stats.approved_submissions || 0}</div>
    </div>

    <!-- Pending Submissions (Private - only show to owner) -->
    {#if isOwnProfile && stats.pending_submissions !== undefined}
      <div class="bg-gradient-to-br from-yellow-900/30 to-yellow-800/20 border border-yellow-700 rounded-lg p-4">
        <div class="text-xs text-yellow-400 mb-1 flex items-center gap-1">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>
          <span>Pending</span>
        </div>
        <div class="text-2xl font-bold text-yellow-400">{stats.pending_submissions || 0}</div>
      </div>
    {/if}

    <!-- Total Submissions (Public) -->
    <div class="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700 rounded-lg p-4">
      <div class="text-xs text-blue-400 mb-1">Total</div>
      <div class="text-2xl font-bold text-blue-400">{stats.total_submissions || 0}</div>
    </div>

    <!-- Likes Received (Public) -->
    <div class="bg-gradient-to-br from-pink-900/30 to-pink-800/20 border border-pink-700 rounded-lg p-4">
      <div class="text-xs text-pink-400 mb-1 flex items-center gap-1">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
        </svg>
        <span>Likes</span>
      </div>
      <div class="text-2xl font-bold text-pink-400">{stats.likes_received || 0}</div>
    </div>

    <!-- Contributions by Type (if available) -->
    {#if stats.contributions_by_type}
      <div class="col-span-2 sm:col-span-4 bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h3 class="text-sm font-semibold text-slate-400 mb-3">Contributions by Type</h3>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {#each Object.entries(stats.contributions_by_type) as [type, count]}
            <div class="text-center">
              <div class="text-lg font-bold text-cyan-400">{count}</div>
              <div class="text-xs text-slate-500 capitalize">{type}</div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>
