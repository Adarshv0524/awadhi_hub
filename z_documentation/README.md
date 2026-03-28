# Awadhi Hub Documentation

Last updated: March 28, 2026  
Status: Production-oriented documentation baseline for 2026

## 0) Document Mission

This README is the operational front door for the repository documentation set. It explains what Awadhi Hub is, how it is structured, how contributors should work, and where to find deep technical references.

## Awadhi Hub in One Line

Awadhi Hub is a universal literary engine for Awadhi heritage, designed to host mixed-form classical poetry in strict chapter order while preserving dictionary, idiom, and article modules as independent knowledge systems.

## 1) Platform Goals

Awadhi Hub is designed to satisfy four long-horizon goals:

1. Preserve classical literary context with hierarchy-aware data and navigation.
2. Support mixed poetic forms without repeated schema rewrites.
3. Provide modern, accessible reading and search experiences.
4. Enable community contribution with moderation, traceability, and quality controls.

## What Is Live Today

1. Hierarchical Poetry Expansion using poetry_nodes with poetry_type and chapter-level sequence navigation.
2. Dynamic poetry rendering in the frontend with specialized and fallback renderers.
3. Sitewide UI overhaul using shared tokens and reusable UI primitives.
4. Unified search experience across poetry, doha, dictionary, idiom, and article domains.
5. Centralized SEO metadata generation in the base layout.

## 2) Architecture Snapshot

System behavior is organized into two coordinated domains:

1. Poetry Domain
   Canonical chapter-sequenced nodes with type discrimination, stream APIs, and renderer dispatch.

2. Knowledge Domain
   Dictionary, idiom, and article modules retained with independent schemas and workflows.

Why this matters:

1. Poetry remains extensible without table-per-form growth.
2. Knowledge modules retain semantic clarity.
3. Frontend search and navigation can aggregate without flattening domain integrity.

## Product Model

Awadhi Hub runs two coordinated but separate content planes:

1. Poetry plane
   chapter-sequenced literary content including doha, chaupai, jhulana, sorath, and related forms.

2. Knowledge plane
   dictionary, idiom, and article content with module-specific schemas and moderation semantics.

This separation is deliberate and is part of the core architecture contract.

## 3) Repository Layout

Top-level structure (high signal paths):

1. backend/
   FastAPI app, SQLAlchemy models, services, and Alembic migrations.

2. frontend/
   Astro pages, Svelte components, shared UI primitives, and styling tokens.

3. z_documentation/
   Canonical architecture, issue tracking, runtime reports, and supporting guides.

4. backend/tests and backend/app/tests
   API and service-level testing coverage.

5. z_documentation/runtime
   Runtime sweep artifacts and operational diagnostic records.

## Technology Stack

1. Backend: FastAPI, SQLAlchemy, Alembic, MySQL.
2. Frontend: Astro plus Svelte and TypeScript.
3. Styling: Tailwind integration plus centralized CSS token system.
4. Search and navigation: API fan-out plus chapter-sequenced poetry APIs.

## 4) Runtime Contracts

Core runtime contracts contributors should assume:

1. Chapter navigation in poetry resolves by chapter_id plus sequence_no.
2. Search filter state determines which domain endpoints are called.
3. Shared layout owns canonical, OpenGraph, and Twitter metadata.
4. Shared UI primitives and CSS tokens are default for new UI work.
5. Content visibility and status rules apply across read paths.

## Documentation Index

1. Architecture.md
   canonical technical map of data layer, service contracts, and presentation architecture.

2. issues.md
   active issue and technical debt tracker (clean slate plus forward plan).

3. SYSTEM_ARCHITECTURE_2026.md
   infrastructure-level and broader platform architecture notes.

4. api/
   endpoint-level references.

5. audit/ and runtime/
   historical audits and runtime diagnostics.

## 5) Local Development Quick Start

Prerequisites:

1. Python environment for backend dependencies.
2. Node environment for frontend dependencies.
3. MySQL available locally or through container setup.

Typical workflow:

1. Install backend dependencies from backend/requirements.txt.
2. Run Alembic migrations to current head.
3. Start backend API server.
4. Install frontend dependencies from frontend/package.json.
5. Start frontend dev server.

Validation checks before pushing:

1. Run backend tests.
2. Run frontend build or type checks.
3. Smoke-test search, poetry chapter navigation, and submission flow.

## Contributor Flow

1. Read Architecture.md before implementation.
2. Pick a scoped task and confirm domain boundary:
   poetry expansion work or independent knowledge module work.
3. Implement with tests and run local checks.
4. Update documentation in the same change window.
5. Update issues.md by removing completed debt and adding only net-new items.

## 6) Pull Request Expectations

Each PR should include:

1. Problem statement and scope boundary.
2. Contract impact summary (API, schema, frontend behavior).
3. Test evidence.
4. Documentation updates.
5. Issue tracker updates for resolved or newly discovered debt.

PRs that change architecture-relevant behavior without documentation parity should be considered incomplete.

## Engineering Policy

Definition of done for architecture-impacting work:

1. Code is merged and validated.
2. Architecture.md reflects the new reality.
3. issues.md contains only unresolved items.

No change is complete without all three.

## 7) Quality Standards

Minimum quality bar:

1. No schema-model drift.
2. No silent contract-breaking response changes.
3. No page-level duplicate SEO metadata.
4. No inaccessible core controls in search/reader flows.
5. No domain-boundary violations between poetry and knowledge modules.

## 8) Security and Privacy Notes

1. Do not log sensitive auth material.
2. Keep error messaging user-safe and avoid raw internal traces in client surfaces.
3. Validate and sanitize submission payload fields before persistence.
4. Respect role-based access control for moderation and admin operations.

## 9) Release Readiness Checklist

Before release candidate sign-off:

1. Migration head is applied and validated.
2. Poetry stream/nav and search fan-out pass smoke tests.
3. Metadata and canonical URL behavior are verified on key routes.
4. Active issue tracker contains only unresolved items.
5. Architecture and README reflect current runtime behavior.

## Current Direction

Near-term direction is not another table-per-form rewrite. It is:

1. Extend poetry capabilities through discriminator-driven forms.
2. Improve chapter reading experience and observability.
3. Keep dictionary, idiom, and article domains stable and high quality.
4. Build forward features like realtime collaboration and engagement systems without violating domain boundaries.

## 10) Governance Reminder

The documentation set under z_documentation is the official source of truth for architecture and operational posture. Keep it current, concise, and implementation-anchored.
