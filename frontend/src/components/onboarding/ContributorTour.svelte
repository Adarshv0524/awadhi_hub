<script lang="ts">
  import { onMount } from "svelte";
  import { getMe } from "../../lib/auth";

  const TOUR_KEY = "awadhi_contributor_tour_v1";

  const steps = [
    {
      title: "Welcome to Awadhi New",
      description: "Start by submitting your first contribution. Drafts are saved while you work.",
      cta: { label: "Open Submit", href: "/submit" },
    },
    {
      title: "Track your progress",
      description: "Use your dashboard to monitor review status, bookmarks, and engagement metrics.",
      cta: { label: "Open Dashboard", href: "/dashboard" },
    },
    {
      title: "Climb the leaderboard",
      description: "Earn likes, approvals, and reputation points to rise in the community ranking.",
      cta: { label: "View Leaderboard", href: "/leaderboard" },
    },
  ];

  let visible = false;
  let stepIndex = 0;

  onMount(async () => {
    try {
      const done = localStorage.getItem(TOUR_KEY);
      if (done) return;
      const me = await getMe();
      if (!me) return;
      if (me.role === "registered" || String(me.role) === "contributor") {
        visible = true;
      }
    } catch {
      // Do nothing; tour is optional.
    }
  });

  function nextStep() {
    if (stepIndex < steps.length - 1) {
      stepIndex += 1;
      return;
    }
    complete();
  }

  function complete() {
    localStorage.setItem(TOUR_KEY, "done");
    visible = false;
  }

  function dismiss() {
    complete();
  }
</script>

{#if visible}
  <div class="fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-sm p-4">
    <div class="mx-auto mt-12 max-w-xl rounded-2xl border border-cyan-700/50 bg-slate-900 shadow-2xl">
      <div class="border-b border-slate-700 px-6 py-4">
        <p class="text-xs uppercase tracking-wider text-cyan-300">Contributor onboarding</p>
        <h3 class="mt-1 text-2xl font-semibold text-slate-100">{steps[stepIndex].title}</h3>
      </div>
      <div class="px-6 py-5">
        <p class="text-slate-300">{steps[stepIndex].description}</p>
        <div class="mt-5 rounded-lg border border-slate-700 bg-slate-950/70 p-4 text-sm text-slate-400">
          Step {stepIndex + 1} of {steps.length}
        </div>
      </div>
      <div class="flex items-center justify-between gap-3 border-t border-slate-700 px-6 py-4">
        <button class="rounded-md border border-slate-600 px-4 py-2 text-slate-200 hover:bg-slate-800" on:click={dismiss}>Skip</button>
        <div class="flex items-center gap-2">
          <a class="rounded-md border border-cyan-700/60 bg-cyan-900/40 px-4 py-2 text-cyan-100 hover:bg-cyan-800/50" href={steps[stepIndex].cta.href}>
            {steps[stepIndex].cta.label}
          </a>
          <button class="rounded-md bg-cyan-500 px-4 py-2 font-medium text-slate-950 hover:bg-cyan-400" on:click={nextStep}>
            {stepIndex === steps.length - 1 ? "Finish" : "Next"}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
