// src/pages/sitemap.xml.ts
import type { APIRoute } from "astro";
import { api } from "../lib/api";

interface SitemapUrl {
  loc: string;
  lastmod?: string;
  changefreq: "always" | "hourly" | "daily" | "weekly" | "monthly" | "yearly" | "never";
  priority: string;
}

export const GET: APIRoute = async () => {
  const baseUrl = (import.meta.env.SITE || "https://awadhi.new").replace(/\/$/, "");
  const urls: SitemapUrl[] = [];
  const now = new Date().toISOString();

  try {
    // Static routes with proper priorities
    urls.push(
      { loc: "/", lastmod: now, changefreq: "daily", priority: "1.0" },
      { loc: "/search", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/doha", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/dictionary", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/idioms", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/articles", lastmod: now, changefreq: "daily", priority: "0.9" },
      { loc: "/submit", lastmod: now, changefreq: "monthly", priority: "0.7" },
    );

    // Dynamic content - Doha entries
    try {
      const dohas = await api("/content/doha?limit=1000&visibility=public");
      const dohaArray = Array.isArray(dohas) ? dohas : dohas?.results || [];
      dohaArray.forEach((d: any) => {
        if (d.id && d.visibility === "public") {
          urls.push({
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
      const dictEntries = await api("/dictionary?limit=1000&visibility=public");
      const dictArray = Array.isArray(dictEntries) ? dictEntries : dictEntries?.results || [];
      dictArray.forEach((d: any) => {
        if (d.id && d.visibility === "public") {
          urls.push({
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
      const idioms = await api("/idioms?limit=1000&visibility=public");
      const idiomsArray = Array.isArray(idioms) ? idioms : idioms?.results || [];
      idiomsArray.forEach((i: any) => {
        if (i.id && i.visibility === "public") {
          urls.push({
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
      const articles = await api("/articles?limit=1000&visibility=public");
      const articlesArray = Array.isArray(articles) ? articles : articles?.results || [];
      articlesArray.forEach((a: any) => {
        if (a.id && a.visibility === "public") {
          urls.push({
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
