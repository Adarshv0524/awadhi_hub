<script lang="ts">
  export let title: string = "Awadhi New";
  export let text: string = "Check this out";
  export let url: string = "";

  let showCopyMenu = false;
  let copied = false;

  function copyToClipboard() {
    navigator.clipboard.writeText(url).then(() => {
      copied = true;
      setTimeout(() => {
        copied = false;
      }, 2000);
    });
  }

  async function handleShare() {
    if (navigator.share) {
      try {
        await navigator.share({ title, text, url });
      } catch (err: any) {
        if (err.name !== "AbortError") {
          console.error("Share failed:", err);
        }
      }
    } else {
      showCopyMenu = !showCopyMenu;
    }
  }

  function shareOnX() {
    const xUrl = `https://x.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
    window.open(xUrl, "_blank", "width=550,height=420");
  }

  function shareOnFacebook() {
    const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(fbUrl, "_blank", "width=550,height=420");
  }

  function shareOnLinkedIn() {
    const liUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
    window.open(liUrl, "_blank", "width=550,height=420");
  }
</script>

<div class="relative">
  <button
    on:click={handleShare}
    class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all font-medium flex items-center gap-2"
    title="Share this profile"
  >
    <svg
      class="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M8.684 13.342C9.322 10.923 11.85 9 14.5 9c.133 0 .263-.013.391-.027m0 0a8.996 8.996 0 00-7.641 3.574m0 0L2.457 5.457m6.364 13.213L2.457 18.543m6.364-2.107l6.364 6.364"
      ></path>
    </svg>
    Share
  </button>

  {#if showCopyMenu}
    <div
      class="absolute top-full right-0 mt-2 w-56 bg-slate-800 border border-slate-700 rounded-lg shadow-lg z-10"
    >
      <div class="p-3">
        <p class="text-xs text-slate-400 mb-3">Share this profile:</p>
        <div class="space-y-2">
          <button
            on:click={copyToClipboard}
            class="w-full text-left px-3 py-2 hover:bg-slate-700 text-slate-200 text-sm rounded transition-colors flex items-center gap-2"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              ></path>
            </svg>
            {copied ? "Copied!" : "Copy Link"}
          </button>
          <button
            on:click={shareOnX}
            class="w-full text-left px-3 py-2 hover:bg-slate-700 text-slate-200 text-sm rounded transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path
                d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.6l-5.165-6.748L2.881 21.75H-.675l7.73-8.835L.391 2.25h6.774l4.823 6.378 5.736-6.378zM17.15 19.128h2.013L5.55 5.08H3.432l13.718 14.048z"
              />
            </svg>
            Share on X
          </button>
          <button
            on:click={shareOnFacebook}
            class="w-full text-left px-3 py-2 hover:bg-slate-700 text-slate-200 text-sm rounded transition-colors flex items-center gap-2"
          >
            <svg
              class="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
              />
            </svg>
            Share on Facebook
          </button>
          <button
            on:click={shareOnLinkedIn}
            class="w-full text-left px-3 py-2 hover:bg-slate-700 text-slate-200 text-sm rounded transition-colors flex items-center gap-2"
          >
            <svg
              class="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M20.447 20.452h-3.554v-5.569c0-1.328-.475-2.236-1.986-2.236-1.081 0-1.722.728-2.004 1.431-.103.25-.129.599-.129.948v5.426h-3.554s.05-8.807 0-9.728h3.554v1.375c.428-.659 1.191-1.595 2.897-1.595 2.117 0 3.704 1.385 3.704 4.362v5.586zM5.337 9.433c-1.144 0-1.915-.758-1.915-1.704 0-.951.768-1.703 1.96-1.703 1.188 0 1.913.752 1.938 1.703 0 .946-.75 1.704-1.983 1.704zm1.946 11.019H3.39V9.724h3.893v10.728zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z"
              />
            </svg>
            Share on LinkedIn
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
