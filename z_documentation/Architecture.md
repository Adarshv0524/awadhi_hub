# Awadhi Hub Architecture

Last updated: March 28, 2026  
Status: Verified against implementation  
Scope: Hierarchical Poetry Expansion plus Sitewide UI Overhaul

## 0) Purpose and Audience

This document is the canonical technical map for Awadhi Hub. It is written for:

1. Backend engineers designing schema, API, and service behavior.
2. Frontend engineers implementing rendering, interaction, and accessibility patterns.
3. QA engineers validating cross-layer contracts.
4. Technical writers and maintainers synchronizing public and internal documentation.

When this document and code disagree, code is the current runtime truth and this document must be updated in the same change window.

## 0.1 Architecture Principles

Awadhi Hub implementation follows these principles:

1. Hierarchy first: author -> work -> chapter anchors all literary context.
2. Deterministic sequencing: chapter_id plus sequence_no is the poetry navigation source of truth.
3. Domain separation: poetry expansion does not collapse dictionary, idiom, or article into one schema.
4. Progressive rendering: unknown poetry types must still render safely.
5. Contract stability: API schema changes must be explicit, versioned, and tested.
6. Documentation parity: architectural claims are valid only when verifiable in source.

## 1) System Map

Awadhi Hub is implemented as a dual-domain platform:

1. Poetry domain: chapter-sequenced, polymorphic literary nodes backed by poetry_nodes.
2. Knowledge domain: dictionary, idiom, and article modules preserved as separate canonical entities.

This is an intentional architecture boundary. Poetry expansion and navigation are unified. Knowledge modules remain isolated by schema and workflow.

## 1.1 Runtime Topology

1. Frontend application: Astro pages with Svelte interactive islands.
2. API layer: FastAPI route modules grouped by domain.
3. Service layer: business logic for search, moderation, poetry navigation, and content operations.
4. Data access layer: SQLAlchemy ORM models plus Alembic migrations.
5. Storage: MySQL relational schema with JSON fields for bounded flexible metadata.

## 1.2 Layer Ownership

1. Route handlers validate input/output contracts and authorization.
2. Services enforce ordering, domain rules, and side effects.
3. ORM entities define persistence shape and cross-entity relationships.
4. Migrations are the authoritative historical schema evolution log.

No business rule should be enforced only in UI.

## 2) Data Layer

### 2.1 Canonical hierarchy

All chapter-bound literary navigation depends on:

1. classical_authors
2. classical_works
3. work_chapters

This graph is the source of route context and ordering scope.

### 2.2 Polymorphic poetry model

Poetry is implemented in poetry_nodes with a value discriminator:

1. poetry_type identifies the form, including doha, chaupai, jhulana, sorath, savaiya, ghanakshari, chappay, and other_poetry.
2. sequence_no provides deterministic order inside each chapter.
3. UniqueConstraint(chapter_id, sequence_no) enforces one sequence slot per chapter.
4. poetry_type_registry provides active form metadata for UI discovery.

Important note: the discriminator is column-based, not SQLAlchemy class polymorphism. Form-specific schema differences are modeled through shared fields plus prosody_metadata JSON.

## 2.2.1 Poetry node canonical fields

Core fields carry these responsibilities:

1. author_id, work_id, chapter_id: hierarchy linkage and route context.
2. poetry_type: presentation and filter classification.
3. sequence_no: deterministic chapter order.
4. main_text: canonical display payload.
5. text_devanagari, text_romanized: script and transliteration support.
6. meaning: optional interpretive context.
7. prosody_metadata: optional meter/form metadata.
8. status, visibility, is_deleted: publication and lifecycle controls.

## 2.2.2 Registry model behavior

poetry_type_registry supports:

1. Human-readable display_name.
2. Family classification for grouping.
3. Active toggle without code deploy.
4. Optional renderer hints for future dispatch automation.

### 2.3 Migration posture

Migration 0016_poetry_nodes_foundation is active and performs:

1. Table creation for poetry_nodes and poetry_type_registry.
2. Canonical doha backfill into poetry_nodes.
3. Poetry type seed insertion, including other_poetry.

## 2.3.1 Data migration guarantees

Migration and backfill guarantees:

1. Canonical doha entries migrate into poetry_nodes with poetry_type=doha.
2. Sequence assignment is chapter-local and deterministic.
3. Backfill verifies expected count parity and fails closed on mismatch.
4. Source lineage metadata remains available for moderation/audit traceability.

### 2.4 Knowledge modules remain independent

The following modules are not merged into poetry_nodes:

1. dictionary_entries
2. idiom_entries
3. article_entries

Reason: these are semantic knowledge resources, not chapter-sequenced poetic units.

## 2.5 Data integrity and indexing

Expected database integrity controls:

1. Unique constraint on chapter_id and sequence_no.
2. Supporting indexes on chapter sequence, work/chapter, and poetry_type.
3. Foreign keys from poetry_nodes to hierarchy entities.
4. Optional source_submission_id uniqueness for canonicalization mapping.

Expected query shape:

1. Chapter streams: indexed chapter + sequence scan.
2. Navigation: chapter-filtered nearest sequence lookup.
3. Search: filtered text matching with bounded limit and offset.

## 3) Service and API Layer

### 3.1 Poetry navigation contract

Poetry navigation is implemented using chapter_id plus sequence_no as the single canonical resolver.

Primary endpoints:

1. GET /api/v1/poetry/chapters/{chapter_id}/stream
2. GET /api/v1/poetry/chapters/{chapter_id}/nav?sequence_no={n}
3. GET /api/v1/poetry/{poetry_node_id}
4. GET /api/v1/poetry/types
5. GET /api/v1/poetry/search

Navigation behavior:

1. Locate current node by exact chapter and sequence.
2. Resolve previous and next by nearest lower and higher sequence in chapter scope.
3. Return hierarchy context (author, work, chapter) with current and nav summaries.

## 3.1.1 API contract notes

1. chapter stream endpoint returns hierarchy context plus paginated items.
2. nav endpoint returns current plus optional previous and next summaries.
3. detail endpoint returns current node contract for direct linking.
4. types endpoint returns active poetry type metadata for UI controls.
5. search endpoint supports author/work/chapter filtering and optional poetry_type narrowing.

### 3.2 Search fan-out model

The frontend search experience selectively fans out to:

1. doha search
2. poetry search
3. dictionary
4. idiom
5. article

Fan-out is conditional on active filter state, not unconditional multi-request spam.

## 3.2.1 Search request lifecycle

1. Build shared query parameters from user input.
2. Spawn domain-specific requests only for eligible filters.
3. Resolve all requests with per-section failure isolation.
4. Render available sections even when one section fails.

This behavior avoids full-page failure due to one downstream endpoint error.

### 3.3 Submission and moderation data consistency

Idiom submission payloads require romanized text in metadata for both create and edit flows.
Backend idiom validation enforces external_references.text_roman parity across lifecycle updates.

## 3.3.1 Moderation and canonicalization flow

1. User submits draft payload with content-specific metadata.
2. Moderation queue validates and reviews submission.
3. Approved submissions materialize into canonical module entities.
4. For poetry submissions, canonical data is represented in poetry_nodes and surfaced through chapter stream APIs.

## 3.4 Security and policy boundaries

1. Auth-protected write endpoints require valid user identity.
2. Role checks gate moderator/admin actions.
3. Visibility and status filters prevent accidental exposure of non-public content.
4. Rate limiting and bounded pagination reduce abuse surface for search-heavy routes.

## 4) Presentation Layer

### 4.1 Sitewide design system

The UI overhaul is live with shared primitives and tokens:

1. Global style tokens are centralized in frontend/src/styles/global.css.
2. Reusable primitives are in frontend/src/components/ui (Button, Badge, ContentCard).
3. Shared motion, surface, spacing, and typography rules are applied across search and content pages.

## 4.1.1 Design token intent

Global tokens centralize:

1. Color roles (background, surface, foreground, accent, semantic cues).
2. Spacing scale for layout consistency.
3. Radius and shadow system for visual hierarchy.
4. Typographic families for brand-consistent reading experience.

Component authors should consume tokens instead of introducing one-off values.

### 4.2 Poetry renderer dispatcher

Poetry rendering uses a dispatcher component:

1. Normalize poetry_type.
2. Select specialized renderer when mapped.
3. Fall back to GenericPoetryRenderer for unmapped forms.

This enables immediate rendering for newly approved forms before dedicated visual treatment is shipped.

## 4.2.1 Renderer strategy

1. Specialized renderers exist for priority forms.
2. Generic renderer protects delivery continuity for new or rare forms.
3. Renderer map updates are additive and do not require route rewrites.
4. Unknown types should never hard-fail user reading flow.

## 4.2.2 Observability and telemetry

Fallback rendering emits a structured telemetry event to make unmapped poetry types measurable.

Event contract:

1. event_name: fallback_renderer_used
2. poetry_type: unresolved poetry type that triggered GenericPoetryRenderer
3. chapter_id: chapter context when available
4. sequence_no: chapter-local sequence number of the rendered item

Runtime behavior:

1. Development mode logs the payload through console.warn for local diagnostics.
2. Production mode sends a non-blocking POST request to /api/v1/telemetry/renderer-fallback.
3. Telemetry emission is best-effort and never blocks content rendering.

## 4.2.3 Other category for unknown poetry

The other_poetry type supports bounded rich media through prosody_metadata.

Allowed payload contract:

1. prosody_metadata.media.type: image or audio.
2. prosody_metadata.media.url: non-empty URL string.
3. prosody_metadata.media.alt_text: required for image, optional for audio.

Reference shape:

1. {
2.   "media": {
3.     "type": "image" | "audio",
4.     "url": "https://cdn.example/media/file",
5.     "alt_text": "Descriptive text for image or audio context"
6.   }
7. }

Rendering policy:

1. Generic fallback renderer attempts media rendering only when contract fields are valid.
2. Image media uses responsive lazy-loaded rendering and preserves alt text semantics.
3. Audio media uses native controls with non-blocking preload behavior.
4. Malformed or missing media payload never crashes the reader and gracefully degrades to text-only rendering.

### 4.3 Search UX implementation

Search is implemented with production-grade interaction behavior:

1. Debounced input updates.
2. AbortController-based cancellation of stale requests.
3. Dynamic poetry type options loaded from /api/v1/poetry/types.
4. Conditional section rendering based on selected content filter and result presence.
5. URL state synchronization for query and filters.

## 4.3.3 Frontend State & Hydration Strategy

This section defines mandatory client-side strategy rules for Astro plus Svelte.

Hydration directive rules:

1. Use client:load only for above-the-fold, immediately interactive controls.
2. Use client:visible for below-the-fold modules that can defer JS until viewport entry.
3. Use client:idle for non-critical enhancements that do not block first interaction.
4. Prefer SSR/static Astro markup when no client interactivity is required.

State management rules:

1. Shared auth/session state must be store-based and deduplicated across component instances.
2. Avoid repeated auth/me fetches from multiple mounted components.
3. Keep local component state local; promote to shared store only when cross-component synchronization is required.
4. Use explicit loading and error states in stores for predictable rendering.

Client fetch and concurrency rules:

1. Use AbortController for cancellable queries and unmount-safe fetch flows.
2. Use Promise.all for independent requests to avoid avoidable waterfalls.
3. Cap fan-out where aggregate endpoints are unavailable.
4. Guard response normalization with defensive type checks before rendering.

Error-handling rules:

1. Component-level failures must degrade gracefully instead of crashing page-level rendering.
2. Unknown content metadata must render via safe fallbacks.
3. Surface user-safe errors in UI and reserve diagnostic detail for development logs.

## 4.3.1 Accessibility behavior expectations

Search and reader surfaces must maintain:

1. Keyboard-reachable controls.
2. Visible focus states.
3. Proper labels on inputs and selectors.
4. Live region support for loading and result updates where needed.

## 4.3.2 Error handling expectations

1. Avoid exposing raw backend internals in client error messages.
2. Keep section-level fallback states for partial failures.
3. Preserve prior user context (filters/query) after recoverable failures.

### 4.4 SEO and metadata system

SEO tags are centralized in BaseLayout.astro with canonical, OpenGraph, and Twitter metadata generated once per page render. The duplicate page-level tag pattern has been removed from current Astro pages.

## 4.4.1 Metadata contract

All pages should pass title and description through shared layout props to avoid duplicate tags and inconsistent SEO behavior.

## 5) Boundary Contracts

### 5.1 Poetry boundary

Poetry expansion applies only to chapter-sequenced forms. Adding a new form should not require a new content table.

### 5.2 Knowledge boundary

Dictionary, idiom, and article modules keep dedicated storage and workflows. They may link to hierarchy metadata but are not part of the chapter-sequenced poetry stream.

## 5.3 Anti-patterns to avoid

1. Creating new table-per-poetry-form schemas for chapter-sequenced content.
2. Mixing dictionary or idiom semantics into poetry_nodes.
3. Encoding critical navigation logic only in frontend state.
4. Bypassing status/visibility filters in read APIs.

## 6) Verified Risks and Technical Debt

The architecture is aligned with code and there are currently no active technical debt items in the tracker.

## 6.1 Operational risks under growth

1. Chapter size growth can pressure stream payload and render cost.
2. Search fan-out across domains increases network concurrency and retry complexity.
3. Registry and renderer drift can occur if new types are added without renderer governance.

Mitigation posture:

1. Keep stream pagination bounded.
2. Track fallback-rendered type counts.
3. Add targeted integration tests for new type onboarding.

## 7) Definition of Done for Future Architecture Changes

Every architecture-impacting merge must:

1. Update this document and endpoint references in the same change window.
2. Add or update automated tests for contract behavior.
3. Update active issue tracker by removing completed items and adding only net-new debt.

## 8) Validation Matrix

Minimum validation required before merge for architecture-impacting changes:

1. Backend unit tests for service ordering and contract behavior.
2. API tests for response shape and filter semantics.
3. Frontend interaction tests for search filter, debounce, and conditional rendering.
4. Migration verification for schema and backfill integrity.
5. Manual smoke pass for chapter navigation and SEO metadata rendering.

## 9) Change Log Guidance

When editing this architecture document:

1. Record only current-state truth and active technical debt.
2. Move historical details to archive notes, not primary architecture baseline.
3. Keep endpoint names and invariants synchronized with source code.
