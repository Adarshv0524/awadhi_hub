// src/pages/robots.txt.ts
export async function GET() {
  const robotsTxt = `
# Awadhi New - Robots.txt
# Allow crawling of public content, disallow private areas

User-agent: *

# Allow public content
Allow: /
Allow: /doha
Allow: /doha/*
Allow: /dictionary
Allow: /dictionary/*
Allow: /idioms
Allow: /idioms/*
Allow: /articles
Allow: /articles/*
Allow: /authors
Allow: /search
Allow: /about

# Disallow private/user areas
Disallow: /login
Disallow: /register
Disallow: /forgot-password
Disallow: /reset-password
Disallow: /dashboard
Disallow: /dashboard/*
Disallow: /me
Disallow: /me/*
Disallow: /submit
Disallow: /submissions
Disallow: /submissions/*

# Disallow admin/moderation
Disallow: /admin
Disallow: /admin/*
Disallow: /moderation
Disallow: /moderation/*

# Disallow API endpoints (if exposed)
Disallow: /api
Disallow: /api/*

# Sitemap
Sitemap: https://awadhi.new/sitemap.xml
`.trim();

  return new Response(robotsTxt, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}
