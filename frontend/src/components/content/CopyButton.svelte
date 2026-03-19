<!-- src/components/content/CopyButton.svelte -->
<!-- Reusable copy-to-clipboard button with visual feedback -->
<script lang="ts">
  export let text: string;
  export let label: string = "Copy";
  export let color: string = "cyan"; // cyan, blue, indigo, purple
  
  let copied = false;

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(text);
      copied = true;
      setTimeout(() => {
        copied = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback: try to select text
      alert('📋 Copy failed. Please select and copy manually.');
    }
  }

  const colorMap: Record<string, { hover: string; text: string; copiedBg: string; copiedText: string }> = {
    cyan: { 
      hover: "hover:text-cyan-400", 
      text: "text-slate-500",
      copiedBg: "bg-cyan-900/50",
      copiedText: "text-cyan-300"
    },
    blue: { 
      hover: "hover:text-blue-400", 
      text: "text-slate-500",
      copiedBg: "bg-blue-900/50",
      copiedText: "text-blue-300"
    },
    indigo: { 
      hover: "hover:text-indigo-400", 
      text: "text-slate-500",
      copiedBg: "bg-indigo-900/50",
      copiedText: "text-indigo-300"
    },
    purple: { 
      hover: "hover:text-purple-400", 
      text: "text-slate-500",
      copiedBg: "bg-purple-900/50",
      copiedText: "text-purple-300"
    },
  };

  const colors = colorMap[color] || colorMap.cyan;
</script>

<button
  on:click={copyToClipboard}
  class="flex items-center gap-2 px-3 py-2 rounded-lg border transition-all group"
  class:border-slate-600={!copied}
  class:bg-slate-800={!copied}
  class:border-green-600={copied}
  class:bg-green-900={copied}
  aria-label={copied ? "Copied!" : `Copy ${label}`}
  title={copied ? "Copied!" : `Copy ${label} to clipboard`}
>
  {#if copied}
    <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
    </svg>
    <span class="text-sm font-medium text-green-300">Copied!</span>
  {:else}
    <svg class="w-4 h-4 {colors.text} {colors.hover} transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
    </svg>
    <span class="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">Copy {label}</span>
  {/if}
</button>
