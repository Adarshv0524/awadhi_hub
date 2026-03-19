// hierarchyParser.ts - Utility to parse hierarchy_path into breadcrumbs
export interface BreadcrumbItem {
  name: string;
  slug: string;
  href: string;
}

/**
 * Parse hierarchy path from backend into breadcrumb items
 * @param path - Raw path like "/tulsidas/ramcharitmanas/ayodhyakand"
 * @returns Array of breadcrumb objects with name, slug, href
 */
export function parseHierarchyPath(path: string | null | undefined): BreadcrumbItem[] {
  if (!path || typeof path !== 'string') return [];
  
  const parts = path.split('/').filter(Boolean);
  
  return parts.map((slug, index) => {
    // Capitalize first letter and replace hyphens/underscores with spaces
    const name = slug
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    // Build hierarchical href on the real route tree (e.g., /tulsidas/ramcharitmanas)
    const href = `/${parts.slice(0, index + 1).join('/')}`;
    
    return { name, slug, href };
  });
}

/**
 * Format hierarchy path for display without links
 * @param path - Raw path like "/tulsidas/ramcharitmanas/ayodhyakand"
 * @returns Formatted string like "Tulsidas → Ramcharitmanas → Ayodhyakand"
 */
export function formatHierarchyPath(path: string | null | undefined): string {
  if (!path || typeof path !== 'string') return '';
  
  const breadcrumbs = parseHierarchyPath(path);
  return breadcrumbs.map(b => b.name).join(' → ');
}

/**
 * Get the last item from hierarchy path (most specific)
 * @param path - Raw path
 * @returns Last breadcrumb item or null
 */
export function getLastHierarchyItem(path: string | null | undefined): BreadcrumbItem | null {
  const breadcrumbs = parseHierarchyPath(path);
  return breadcrumbs.length > 0 ? breadcrumbs[breadcrumbs.length - 1] : null;
}

/**
 * Truncate long hierarchy paths for display
 * @param path - Raw path
 * @param maxItems - Maximum number of items to show
 * @returns Truncated breadcrumb array with ellipsis if needed
 */
export function truncateHierarchyPath(
  path: string | null | undefined,
  maxItems: number = 3
): BreadcrumbItem[] {
  const breadcrumbs = parseHierarchyPath(path);
  
  if (breadcrumbs.length <= maxItems) {
    return breadcrumbs;
  }
  
  // Show first, ellipsis, and last items
  return [
    breadcrumbs[0],
    { name: '...', slug: 'ellipsis', href: '#' },
    ...breadcrumbs.slice(-1)
  ];
}
