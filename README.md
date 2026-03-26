# Awadhi New

Awadhi New is a digital preservation and publication platform for Awadhi language knowledge systems: classical poetry, lexical knowledge, idioms, and scholarly writing.

This repository contains the full stack implementation:
- FastAPI backend as source of truth
- Astro + Svelte frontend for public discovery and contributor workflows
- MySQL + Alembic for persistence and schema evolution

## Project Aim

The platform is built to do four things well:
1. Preserve canonical Awadhi content in a structured, queryable hierarchy.
2. Enable contribution with moderation and auditability.
3. Present content in SEO-friendly public pages with rich metadata.
4. Support scholarly workflows: versioning, provenance, and engagement analytics.

Primary content domains:
- Doha (canonical poetic couplets)
- Dictionary entries
- Idioms
- Articles
- Classical hierarchy (author -> work -> chapter)

## High-Level Architecture

Backend:
- FastAPI app and routers in `backend/app/api/v1`
- SQLAlchemy models in `backend/app/db/models.py`
- Business logic services in `backend/app/services`
- Auth/JWT/OAuth in `backend/app/api/v1/auth.py`
- Migrations in `backend/alembic/versions`

Frontend:
- Astro routes in `frontend/src/pages`
- API client and data helpers in `frontend/src/lib`
- Svelte islands for interactive components in `frontend/src/components`

Core operational flows:
1. User submits content
2. Moderator reviews/approves/rejects
3. Approved content materializes into canonical tables
4. Public pages read canonical content and render SEO metadata

## Data Model: Hierarchy and Content

### Hierarchy tables
- `classical_authors`
- `classical_works`
- `work_chapters`

These are managed through:
- Public browsing APIs in `backend/app/api/v1/hierarchy_public.py`
- Admin CRUD APIs in `backend/app/api/v1/hierarchy_admin.py`

### Canonical content tables
- `doha_entries`
- `dictionary_entries`
- `idiom_entries`
- `article_entries`

Cross-link fields used by content items:
- `author_id`
- `work_id`
- `chapter_id`
- `number_in_chapter`
- `hierarchy_path` (for deep path resolution)

This allows one chapter to contextually contain multiple content types, even though doha is currently the strongest fully-wired hierarchical content flow.

## How Author, Work, Chapter, and Chapter Content Are Used

Current implemented navigation patterns:
1. Browse authors: `GET /authors`
2. Browse works for author: `GET /authors/{author_slug}/works`
3. Browse chapters for work: `GET /authors/{author_slug}/works/{work_slug}/chapters`
4. Resolve canonical leaf by path: `GET /content/by-path/{hierarchy_path}`
5. Search by hierarchy filters: `GET /search?author=&work=&chapter=`

Frontend routes reflecting this:
- `/authors`
- `/{author}`
- `/{author}/{work}`
- `/{author}/{work}/{chapter}`
- `/doha/{id}`

### Important: next/previous verse sequencing status

The project stores chapter-level ordering metadata (`number_in_chapter`) but does not yet expose a dedicated navigation API for adjacent verses.

For a Hanuman Chalisa style reading flow, desired behavior is:
- current line: "raam dut atulit baldhaama anjani putra pawansut nama"
- next line: "mahavir vikram bajrangai kumati nivar sumati ke sangi"
- previous line: "jai hanuman gyan gun sagar, jai kapees tihun lok ujagar"

Current state:
- A dedicated `next` and `prev` endpoint is not implemented.
- Chapter page currently falls back to filtered search results instead of a strict ordered chapter-content API.

Implication:
- Reader experience is functional but not truly sequence-native for chant/paath style content navigation.

## Auth and Roles

Auth stack:
- Email/password registration and login
- Access + refresh tokens
- Forgot/reset password
- Google OAuth callback endpoint on backend

Roles and access:
- registered
- contributor
- moderator
- admin

Current implementation note:
- Backend OAuth callback exists.
- Frontend login currently does not expose Google sign-in UI yet.

## What Works Well Today

1. Clear backend API modularization (auth, hierarchy, content, submissions, moderation, analytics, interactions).
2. Strong submission lifecycle with optimistic locking and moderation workflow.
3. Public hierarchy browsing and canonical doha retrieval are operational.
4. SEO foundations in frontend are present (structured data, canonical links, sitemap flow).
5. Migration includes schema drift reconciliation for known runtime-critical mismatches.

## Current Gaps and Risks

1. No first-class chapter sequencing API (next/prev not implemented).
2. Moderator inline metadata editing for submissions is currently limited.
3. Frontend-dashboard likes and user stats rely on missing backend endpoints.
4. OAuth flow is backend-ready but frontend-incomplete.
5. Dynamic route fallback path is robust but can be inefficient and less deterministic than dedicated chapter-content APIs.

Detailed issue-style analysis and module task plan:
- See `z_documentation/MASTER_PROJECT_AUDIT_AND_TASKS.md`

## Run and Develop

Backend:
- Use `backend/requirements.txt` or `backend/pyproject.toml`
- Start API server and DB (Docker compose supported)

Frontend:
- Use `frontend/package.json`
- Astro dev server serves SSR pages and Svelte islands

Top-level orchestration:
- `docker-compose.yml`

## Migration Safety Checks (Local)

To prevent model/migration drift (for example `references` vs `external_references`), run these backend checks before pushing:

1. Apply migrations from base to head and verify runtime-critical reconciliations:
	- `python backend/scripts/migration_smoke_test.py`
2. Verify SQLAlchemy metadata and Alembic head are in sync (no pending autogenerate ops):
	- `python backend/scripts/schema_contract_check.py`

Optional guard validation (expected failure):
- `python backend/scripts/schema_contract_check.py --simulate-drift`

The optional drift simulation injects an in-memory metadata mismatch and must fail. If it passes, your schema-contract gate is not working.

Environment variables used by these checks:
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

These checks assume Alembic `target_metadata` points to `Base.metadata` in `backend/alembic/env.py`.

## Recommended Next Milestones

1. Implement chapter ordered retrieval and next/previous navigation endpoints.
2. Upgrade chapter and doha pages to sequence-native reading UX.
3. Complete missing dashboard APIs (likes, user stats).
4. Enable Google login button and callback initiation flow in frontend.
5. Add missing tests specifically for chapter navigation and adjacency behavior.
