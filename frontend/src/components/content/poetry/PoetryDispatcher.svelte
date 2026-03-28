<script lang="ts">
  import { onMount } from "svelte";

  import { API_BASE } from "../../../lib/api";
  import ChaupaiRenderer from "./ChaupaiRenderer.svelte";
  import DohaRenderer from "./DohaRenderer.svelte";
  import GenericPoetryRenderer from "./GenericPoetryRenderer.svelte";
  import JhulanaRenderer from "./JhulanaRenderer.svelte";

  export let poetryNode: {
    id: number;
    poetry_type: string;
    sequence_no: number;
    main_text: string;
    chapter_id?: number | null;
    prosody_metadata?: Record<string, unknown> | null;
    text_devanagari?: string | null;
    text_romanized?: string | null;
    meaning?: string | null;
  };
  export let chapterId: number | null = null;

  const rendererMap: Record<string, typeof GenericPoetryRenderer> = {
    doha: DohaRenderer,
    chaupai: ChaupaiRenderer,
    jhulana: JhulanaRenderer,
  };

  $: normalizedType = String(poetryNode?.poetry_type || "other_poetry").toLowerCase();
  $: Renderer = rendererMap[normalizedType] || GenericPoetryRenderer;
  $: isFallbackRenderer = !rendererMap[normalizedType];

  function buildFallbackEventPayload() {
    return {
      event_name: "fallback_renderer_used",
      poetry_type: String(poetryNode?.poetry_type || "other_poetry"),
      chapter_id: chapterId ?? poetryNode?.chapter_id ?? null,
      sequence_no: Number(poetryNode?.sequence_no || 0),
    };
  }

  async function emitFallbackTelemetry() {
    const payload = buildFallbackEventPayload();
    if (import.meta.env.DEV) {
      console.warn("[poetry] fallback renderer used", payload);
      return;
    }

    const endpoint = `${API_BASE}/api/v1/telemetry/renderer-fallback`;
    const body = JSON.stringify(payload);
    try {
      if (typeof navigator !== "undefined" && typeof navigator.sendBeacon === "function") {
        navigator.sendBeacon(endpoint, new Blob([body], { type: "application/json" }));
        return;
      }
      await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        keepalive: true,
      });
    } catch {
      // Telemetry should never block rendering.
    }
  }

  onMount(() => {
    if (isFallbackRenderer) {
      emitFallbackTelemetry();
    }
  });
</script>

<svelte:component this={Renderer} poetryNode={poetryNode} />
