<!-- Breadcrumbs.svelte - Hierarchical navigation breadcrumbs -->
<script lang="ts">
  import { parseHierarchyPath, type BreadcrumbItem } from '../../lib/hierarchyParser';

  export let path: string | null | undefined;
  export let maxItems: number = 5;
  export let showHome: boolean = true;

  $: breadcrumbs = parseHierarchyPath(path);
  $: displayCrumbs = breadcrumbs.length > maxItems
    ? [breadcrumbs[0], { name: '...', slug: 'ellipsis', href: '#' } as BreadcrumbItem, ...breadcrumbs.slice(-2)]
    : breadcrumbs;
</script>

{#if breadcrumbs.length > 0}
  <nav aria-label="Breadcrumb" class="breadcrumbs-wrap" role="navigation">
    <ol class="breadcrumbs-list">
    {#if showHome}
      <li class="crumb-item">
        <a href="/" class="crumb-link">Home</a>
      </li>
    {/if}

    {#each displayCrumbs as crumb, index}
      {#if crumb.slug === 'ellipsis'}
        <li class="crumb-item" aria-hidden="true">
          <span class="crumb-ellipsis">…</span>
        </li>
      {:else}
        <li class="crumb-item">
          <a
            href={crumb.href}
            class="crumb-link"
            class:crumb-current={index === displayCrumbs.length - 1}
            aria-current={index === displayCrumbs.length - 1 ? 'page' : undefined}
            title={crumb.name}
          >
            {crumb.name}
          </a>
        </li>
      {/if}
    {/each}
    </ol>
  </nav>
{/if}

<style>
  .breadcrumbs-wrap {
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: thin;
    scrollbar-color: rgba(148, 163, 184, 0.25) transparent;
  }

  .breadcrumbs-wrap::-webkit-scrollbar {
    height: 4px;
  }

  .breadcrumbs-wrap::-webkit-scrollbar-track {
    background: transparent;
  }

  .breadcrumbs-wrap::-webkit-scrollbar-thumb {
    background-color: rgba(148, 163, 184, 0.25);
    border-radius: 2px;
  }

  .breadcrumbs-list {
    margin: 0;
    padding: 0;
    list-style: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    white-space: nowrap;
    font-size: 0.82rem;
    color: rgb(148 163 184);
    min-height: 1.5rem;
  }

  .crumb-item {
    display: inline-flex;
    align-items: center;
    max-width: 13rem;
  }

  .crumb-item:not(:last-child)::after {
    content: "/";
    color: rgb(100 116 139);
    margin-left: 0.5rem;
  }

  .crumb-link {
    color: inherit;
    text-decoration: none;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: color 120ms ease;
  }

  .crumb-link:hover {
    color: rgb(226 232 240);
  }

  .crumb-current {
    color: rgb(226 232 240);
    font-weight: 500;
    pointer-events: none;
  }

  .crumb-ellipsis {
    color: rgb(100 116 139);
    letter-spacing: 0.08em;
  }
</style>
