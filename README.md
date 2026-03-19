# Awadhi New

**A comprehensive digital repository for Awadhi language literature, cultural heritage, and linguistic preservation.**

## Summary

Awadhi New serves as the authoritative platform for preserving and sharing Awadhi literary works, including classical dohas (couplets), dictionary entries, idioms, and scholarly articles. The platform empowers community contribution through a moderation-first workflow while maintaining scholarly rigor through version control and canonical content management. Target audiences include language researchers, cultural historians, native Awadhi speakers, and linguistic scholars seeking authentic source material.

## Technical Overview

Built on a **Backend-as-Truth architecture**, the system uses FastAPI (Python 3.11+) as the immutable data authority with MySQL 8.0 for relational integrity and full-text search. Authentication leverages JWT with refresh tokens and OAuth 2.0 (Google) integration. The moderation pipeline implements atomic batch operations with role-based access control (RBAC) across four tiers: registered, contributor, moderator, and admin.

The frontend prioritizes **God-Level SEO** via Astro's server-side rendering with Svelte islands for interactive components. Every public page implements JSON-LD structured data (CreativeWork, DefinedTerm, Article, BreadcrumbList schemas), canonical URLs, OpenGraph metadata, and semantic HTML5. Dynamic sitemaps auto-generate from backend content with proper priority weights. The architecture guarantees zero JavaScript requirements for core content consumption while enabling rich interactions (likes, bookmarks, shares) as progressive enhancements.

Core infrastructure includes Alembic migrations for database versioning, rate limiting per endpoint, engagement KPI tracking with weighted scoring, content version history, and comprehensive audit logging. Deployment uses Docker multi-stage builds with nginx for static assets and uvicorn for API serving. All responses follow REST conventions with Pydantic validation and standardized error formatting.

## Production Status

✅ **READY** with minor manual steps required (see audit report).
