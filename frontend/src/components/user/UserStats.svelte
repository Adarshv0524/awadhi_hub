<!-- src/components/user/UserStats.svelte -->
<script lang="ts">
  export let username: string = "";
  export let isOwnProfile: boolean = false;
  export let error: string | null = null;
  export let stats:
    | {
        username: string;
        contributions_count: number;
        likes_received: number;
        most_liked_content_id: number | null;
        average_engagement_score: number;
        joined_date: string;
      }
    | null = null;

  $: void username;
  $: void isOwnProfile;
  $: avgEngagement = Number(stats?.average_engagement_score ?? 0).toFixed(2);
</script>

<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
  {#if error}
    <div class="col-span-2 sm:col-span-4 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-400 text-sm">
      {error}
    </div>
  {:else if stats}
    <div class="bg-gradient-to-br from-green-900/30 to-green-800/20 border border-green-700 rounded-lg p-4">
      <div class="text-xs text-green-400 mb-1">Contributions</div>
      <div class="text-2xl font-bold text-green-400">{stats.contributions_count}</div>
    </div>

    <div class="bg-gradient-to-br from-pink-900/30 to-pink-800/20 border border-pink-700 rounded-lg p-4">
      <div class="text-xs text-pink-400 mb-1">Likes Received</div>
      <div class="text-2xl font-bold text-pink-400">{stats.likes_received}</div>
    </div>

    <div class="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700 rounded-lg p-4">
      <div class="text-xs text-blue-400 mb-1">Avg Engagement</div>
      <div class="text-2xl font-bold text-blue-400">{avgEngagement}</div>
    </div>

    <div class="bg-gradient-to-br from-indigo-900/30 to-indigo-800/20 border border-indigo-700 rounded-lg p-4">
      <div class="text-xs text-indigo-400 mb-1">Most Liked Content</div>
      <div class="text-2xl font-bold text-indigo-400">
        {#if stats.most_liked_content_id !== null}
          #{stats.most_liked_content_id}
        {:else}
          -
        {/if}
      </div>
    </div>
  {:else}
    <div class="col-span-2 sm:col-span-4 p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-400 text-sm">
      No public statistics available.
    </div>
  {/if}
</div>
