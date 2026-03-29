<script lang="ts">
  import { onMount } from "svelte";
  import { API_BASE, api } from "../../lib/api";

  type LeaderboardEntry = {
    user_id: number;
    username: string;
    likes_given: number;
    bookmarks_given: number;
    approved_submissions: number;
    score: number;
  };

  type LeaderboardPayload = {
    generated_at: string;
    results: LeaderboardEntry[];
  };

  let loading = true;
  let error = "";
  let generatedAt = "";
  let rows: LeaderboardEntry[] = [];
  let reconnectTimer: number | null = null;
  let pollTimer: number | null = null;
  let socket: WebSocket | null = null;
  let wsRetryCount = 0;
  let mode: "websocket" | "polling" = "polling";

  function buildWsUrl(path: string): string {
    const base = API_BASE || window.location.origin;
    const url = new URL(base);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    url.pathname = path;
    url.search = "";
    return url.toString();
  }

  async function loadInitial() {
    const payload = await api<LeaderboardPayload>("/analytics/leaderboard?limit=20");
    applyPayload(payload);
    loading = false;
  }

  async function loadByPolling() {
    try {
      const payload = await api<LeaderboardPayload>("/analytics/leaderboard?limit=20");
      applyPayload(payload);
      error = "";
    } catch (e: any) {
      error = e?.message || "Polling failed";
    }
  }

  function applyPayload(payload: LeaderboardPayload) {
    rows = payload.results || [];
    generatedAt = payload.generated_at;
  }

  function stopPolling() {
    if (pollTimer) {
      window.clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function startPolling() {
    mode = "polling";
    stopPolling();
    void loadByPolling();
    pollTimer = window.setInterval(() => {
      void loadByPolling();
    }, 30000);
  }

  function closeSocket() {
    if (socket && socket.readyState <= 1) {
      socket.close();
    }
    socket = null;
  }

  function connectSocket() {
    closeSocket();
    stopPolling();
    const wsUrl = buildWsUrl("/analytics/ws/leaderboard");
    try {
      socket = new WebSocket(wsUrl);
    } catch {
      error = "Live updates unavailable, switched to polling.";
      startPolling();
      return;
    }

    socket.onopen = () => {
      wsRetryCount = 0;
      mode = "websocket";
      error = "";
    };

    socket.onmessage = (ev) => {
      try {
        const payload: LeaderboardPayload = JSON.parse(ev.data);
        applyPayload(payload);
        error = "";
      } catch {
        // Ignore malformed messages.
      }
    };

    socket.onerror = () => {
      error = "Live updates disconnected, falling back to polling.";
    };

    socket.onclose = () => {
      startPolling();
      wsRetryCount += 1;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      reconnectTimer = window.setTimeout(() => {
        connectSocket();
      }, Math.min(15000, 2000 * wsRetryCount));
    };
  }

  function formatTime(ts: string): string {
    try {
      return new Date(ts).toLocaleTimeString();
    } catch {
      return ts;
    }
  }

  onMount(() => {
    (async () => {
      try {
        await loadInitial();
        connectSocket();
      } catch (e: any) {
        loading = false;
        error = e?.message || "Failed to load leaderboard";
        startPolling();
      }
    })();

    return () => {
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      stopPolling();
      closeSocket();
    };
  });
</script>

<section class="space-y-4">
  <div class="flex items-center justify-between gap-3 flex-wrap">
    <h2 class="text-2xl font-semibold text-slate-100">Community Leaderboard</h2>
    <div class="text-sm text-slate-400">
      {#if generatedAt}
        Updated at {formatTime(generatedAt)}
      {/if}
      <span class="ml-2 rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-300">
        Mode: {mode === "websocket" ? "Live WS" : "Polling (30s)"}
      </span>
    </div>
  </div>

  {#if loading}
    <div class="rounded-lg border border-slate-700 bg-slate-900/60 p-6 text-slate-300">Loading leaderboard...</div>
  {:else if error}
    <div class="rounded-lg border border-amber-700 bg-amber-900/20 p-4 text-amber-200">{error}</div>
  {/if}

  <div class="overflow-x-auto rounded-xl border border-slate-700 bg-slate-950/70">
    <table class="min-w-full text-sm">
      <thead>
        <tr class="bg-slate-900/80 text-slate-300">
          <th class="px-4 py-3 text-left">Rank</th>
          <th class="px-4 py-3 text-left">Contributor</th>
          <th class="px-4 py-3 text-right">Likes</th>
          <th class="px-4 py-3 text-right">Bookmarks</th>
          <th class="px-4 py-3 text-right">Approved</th>
          <th class="px-4 py-3 text-right">Score</th>
        </tr>
      </thead>
      <tbody>
        {#if rows.length === 0}
          <tr>
            <td colspan="6" class="px-4 py-6 text-center text-slate-400">No leaderboard data yet.</td>
          </tr>
        {:else}
          {#each rows as row, idx}
            <tr class="border-t border-slate-800 text-slate-100">
              <td class="px-4 py-3 font-semibold">#{idx + 1}</td>
              <td class="px-4 py-3">{row.username}</td>
              <td class="px-4 py-3 text-right">{row.likes_given}</td>
              <td class="px-4 py-3 text-right">{row.bookmarks_given}</td>
              <td class="px-4 py-3 text-right">{row.approved_submissions}</td>
              <td class="px-4 py-3 text-right font-semibold text-cyan-300">{row.score}</td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</section>
