// src/pages/sitemap.xml.ts
import type { APIRoute } from "astro";
import { api } from "../lib/api";

interface SitemapUrl {
  loc: string;
  lastmod?: string;
  changefreq: "always" | "hourly" | "daily" | "weekly" | "monthly" | "yearly" | "never";
  priority: string;
}

type AnyRecord = Record<string, any>;

const PAGE_SIZE = 200;
const MAX_PAGES = 30;

function getArrayPayload(payload: unknown): AnyRecord[] {
  if (Array.isArray(payload)) return payload as AnyRecord[];
  if (payload && typeof payload === "object" && Array.isArray((payload as AnyRecord).results)) {
    return (payload as AnyRecord).results;
  }
  return [];
}

async function fetchPaginated(pathFactory: (offset: number, limit: number) => string): Promise<AnyRecord[]> {
  const all: AnyRecord[] = [];
  for (let page = 0; page < MAX_PAGES; page += 1) {
    const offset = page * PAGE_SIZE;
    const payload = await api(pathFactory(offset, PAGE_SIZE));
    const rows = getArrayPayload(payload);
    if (rows.length === 0) break;
    all.push(...rows);
    if (rows.length < PAGE_SIZE) break;
  }
  return all;
}

function isPublicVisibility(value: unknown): boolean {
  return value === undefined || value === null || value === "public";
}

export const GET: APIRoute = async () => {
  const baseUrl = (import.meta.env.SITE || "https://awadhi.new").replace(/\/$/, "");
  const urls: SitemapUrl[] = [];
  const seenLocs = new Set<string>();
  const now = new Date().toISOString();

  const pushUrl = (entry: SitemapUrl) => {
    if (seenLocs.has(entry.loc)) return;
    seenLocs.add(entry.loc);
    urls.push(entry);
  };

  try {
    // Static routes with proper priorities
    [
      { loc: "/", lastmod: now, changefreq: "daily", priority: "1.0" },
      { loc: "/search", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/doha", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/dictionary", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/idioms", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/articles", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/authors", lastmod: now, changefreq: "weekly", priority: "0.8" },
      { loc: "/about", lastmod: now, changefreq: "monthly", priority: "0.6" },
    ].forEach(pushUrl);

    // Dynamic content - Doha entries
    try {
      const dohaArray = await fetchPaginated((offset, limit) => `/content/doha?offset=${offset}&limit=${limit}&visibility=public`);
      dohaArray.forEach((d: AnyRecord) => {
        if (d.id && isPublicVisibility(d.visibility)) {
          pushUrl({
            loc: `/doha/${d.id}`,
            lastmod: d.updated_at || d.created_at || now,
            changefreq: "weekly",
            priority: "0.8",
          });
        }
      });
    } catch (e) {
      console.error("[Sitemap] Failed to fetch dohas:", e);
    }

    // Dynamic content - Dictionary entries
    try {
      const dictArray = await fetchPaginated((offset, limit) => `/dictionary?offset=${offset}&limit=${limit}&visibility=public`);
      dictArray.forEach((d: AnyRecord) => {
        if (d.id && isPublicVisibility(d.visibility)) {
          pushUrl({
            loc: `/dictionary/${d.id}`,
            lastmod: d.updated_at || d.created_at || now,
            changefreq: "weekly",
            priority: "0.8",
          });
        }
      });
    } catch (e) {
      console.error("[Sitemap] Failed to fetch dictionary entries:", e);
    }

    // Dynamic content - Idioms
    try {
      const idiomsArray = await fetchPaginated((offset, limit) => `/idioms?offset=${offset}&limit=${limit}&visibility=public`);
      idiomsArray.forEach((i: AnyRecord) => {
        if (i.id && isPublicVisibility(i.visibility)) {
          pushUrl({
            loc: `/idioms/${i.id}`,
            lastmod: i.updated_at || i.created_at || now,
            changefreq: "weekly",
            priority: "0.8",
          });
        }
      });
    } catch (e) {
      console.error("[Sitemap] Failed to fetch idioms:", e);
    }

    // Dynamic content - Articles
    try {
      const articlesArray = await fetchPaginated((offset, limit) => `/articles?offset=${offset}&limit=${limit}&visibility=public`);
      articlesArray.forEach((a: AnyRecord) => {
        if (a.id && isPublicVisibility(a.visibility)) {
          pushUrl({
            loc: `/articles/${a.id}`,
            lastmod: a.updated_at || a.created_at || now,
            changefreq: "weekly",
            priority: "0.8",
          });
        }
      });
    } catch (e) {
      console.error("[Sitemap] Failed to fetch articles:", e);
    }

    // Author/work/chapter hierarchy routes
    try {
      const authorsPayload = await api("/authors");
      const authors = getArrayPayload(authorsPayload);

      for (const author of authors) {
        const authorSlug = author?.slug;
        if (!authorSlug) continue;

        pushUrl({
          loc: `/${authorSlug}`,
          lastmod: author.updated_at || author.created_at || now,
          changefreq: "weekly",
          priority: "0.7",
        });

        try {
          const worksPayload = await api(`/authors/${encodeURIComponent(authorSlug)}/works?offset=0&limit=500`);
          const works = getArrayPayload(worksPayload);

          for (const work of works) {
            const workSlug = work?.slug;
            if (!workSlug) continue;

            pushUrl({
              loc: `/${authorSlug}/${workSlug}`,
              lastmod: work.updated_at || work.created_at || now,
              changefreq: "weekly",
              priority: "0.7",
            });

            try {
              const chaptersPayload = await api(
                `/authors/${encodeURIComponent(authorSlug)}/works/${encodeURIComponent(workSlug)}/chapters?offset=0&limit=500`
              );
              const chapters = getArrayPayload(chaptersPayload);

              for (const chapter of chapters) {
                const chapterSlug = chapter?.slug;
                if (!chapterSlug) continue;
                pushUrl({
                  loc: `/${authorSlug}/${workSlug}/${chapterSlug}`,
                  lastmod: chapter.updated_at || chapter.created_at || now,
                  changefreq: "weekly",
                  priority: "0.7",
                });
              }
            } catch (e) {
              console.error(`[Sitemap] Failed to fetch chapters for ${authorSlug}/${workSlug}:`, e);
            }
          }
        } catch (e) {
          console.error(`[Sitemap] Failed to fetch works for ${authorSlug}:`, e);
        }
      }
    } catch (e) {
      console.error("[Sitemap] Failed to fetch author hierarchy:", e);
    }

    // Generate XML with proper formatting
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${urls
  .map(
    (entry) => `  <url>
    <loc>${baseUrl}${entry.loc}</loc>
    ${entry.lastmod ? `<lastmod>${formatDate(entry.lastmod)}</lastmod>` : ""}
    <changefreq>${entry.changefreq}</changefreq>
    <priority>${entry.priority}</priority>
  </url>`
  )
  .join("\n")}
</urlset>`;

    return new Response(xml, {
      status: 200,
      headers: {
        "Content-Type": "application/xml; charset=utf-8",
        "Cache-Control": "public, max-age=3600, s-maxage=7200",
        "X-Robots-Tag": "all",
      },
    });
  } catch (error) {
    console.error("[Sitemap] Fatal error:", error);
    
    // Fallback minimal sitemap
    const fallbackXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${baseUrl}/</loc>
    <lastmod>${now}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>`;

    return new Response(fallbackXml, {
      status: 200,
      headers: {
        "Content-Type": "application/xml; charset=utf-8",
      },
    });
  }
};

// Helper function to format dates to W3C format (ISO 8601)
function formatDate(date: string | Date): string {
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) {
      return new Date().toISOString().split("T")[0];
    }
    return d.toISOString().split("T")[0]; // YYYY-MM-DD format
  } catch {
    return new Date().toISOString().split("T")[0];
  }
}
