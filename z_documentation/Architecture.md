# Awadhi New Content Architecture

Last updated: March 31, 2026  
Scope: Author to Work to Chapter to Content node delivery, pointer logic, and chapter page behavior

## 1. System Map

Awadhi New currently runs two parallel canonical content lines:

1. Legacy canonical doha line via doha_entries.
2. Polymorphic chapter line via poetry_nodes.

Both are hierarchy-linked using the same parent entities:

1. classical_authors
2. classical_works
3. work_chapters

## 2. Hierarchical Mapping

### 2.1 Entity Chain

Author to Work to Chapter to Node is implemented through foreign keys.

1. classical_works.author_id -> classical_authors.id
2. work_chapters.work_id -> classical_works.id
3. poetry_nodes.chapter_id -> work_chapters.id
4. poetry_nodes.work_id and poetry_nodes.author_id kept for direct filtering and denormalized safety

Legacy path form is still present on doha_entries.hierarchy_path and has the shape:

author_slug/work_slug/chapter_slug/number_in_chapter

### 2.2 Runtime Read Paths

1. /authors, /authors/{author}/works, /authors/{author}/works/{work}/chapters provide parent hierarchy browsing.
2. /{author}/{work}/{chapter} renders chapter stream from poetry_nodes.
3. /poetry/{id} renders one node detail with previous or next summary.
4. /content/doha/{id}/navigation is still used by legacy doha flow.

## 3. Architecture Diagram (ASCII)

```text
						+-------------------+
						|  classical_authors|
						| id, slug, name    |
						+---------+---------+
								  |
								  | 1:N
								  v
						+-------------------+
						|  classical_works  |
						| id, author_id,    |
						| slug, title       |
						+---------+---------+
								  |
								  | 1:N
								  v
						+-------------------+
						|   work_chapters   |
						| id, work_id,      |
						| slug, number      |
						+---------+---------+
								  |
					+-------------+-------------+
					|                           |
					| 1:N                       | 1:N (legacy)
					v                           v
		 +-------------------------+   +-----------------------+
		 |      poetry_nodes       |   |      doha_entries     |
		 | id, chapter_id,         |   | id, chapter_id,       |
		 | poetry_type, sequence_no|   | number_in_chapter,    |
		 | main_text, meaning      |   | hierarchy_path        |
		 +------------+------------+   +-----------------------+
					  |
					  | previous/next resolved by
					  | nearest sequence_no in same chapter
					  v
		 +-------------------------+
		 |   /api/v1/poetry/nav    |
		 | current, previous, next |
		 +-------------------------+
```

## 4. Linked-List Logic (Previous and Next)

There is no stored pointer column today.  
Pointer behavior is computed at query time using ordered neighbors.

### 4.1 Implemented Resolver

In poetry service, next and previous are selected as:

1. Previous: max sequence_no smaller than current in same chapter.
2. Next: min sequence_no greater than current in same chapter.
3. Tie-breaker: id ordering.

This is functionally equivalent to an implicit doubly linked list over sequence_no.

### 4.2 Example Validation Requirement (Hanuman Chalisa)

Expected chapter-local chain should satisfy:

1. Jai Hanuman ... -> Ram dut atulit ... -> Mahavir vikram ...
2. For Ram dut atulit ...:
previous should be Jai Hanuman ...
next should be Mahavir vikram ...

Audit result:

1. Algorithm supports this correctly if sequence numbers are correct.
2. Repository test fixtures currently use synthetic lines such as Doha One and Doha Two.
3. A production-like fixture for these exact Hanuman Chalisa lines is missing and should be added.

## 5. Polymorphic Chapter Presentation

Chapter page uses a dispatcher that maps poetry_type to renderer:

1. doha -> DohaRenderer
2. chaupai -> ChaupaiRenderer
3. jhulana -> JhulanaRenderer
4. unknown type -> GenericPoetryRenderer plus telemetry event

This supports mixed forms in one chapter stream while preserving sequence order.

### 5.1 Chapter Page Flow

1. Resolve chapter_id from slug chain.
2. Fetch /api/v1/poetry/chapters/{chapter_id}/stream for initial batch.
3. Render each node by poetry_type via dispatcher.
4. Load more appends stream chunk.
5. Optional nav endpoint refines previous or next metadata for current position.

## 6. Current Schema And Logic Gaps

### 6.1 Pointer Representation Gap

There are no explicit prev_node_id or next_node_id columns.  
Computed pointers are correct for ordering but cannot represent editorial jumps.

### 6.2 Dual Canonical Sources

doha_entries and poetry_nodes both represent canonical doha-adjacent content.  
This increases migration and contract complexity across APIs and docs.

### 6.3 Performance Hotspot

Chapter stream serialization currently resolves engagement rows per node, producing N+1 behavior.

## 7. Chapter Page Contract

Minimum chapter payload needed by frontend reader:

1. hierarchy.author, hierarchy.work, hierarchy.chapter
2. items[].id
3. items[].poetry_type
4. items[].sequence_no
5. items[].main_text
6. items[].meaning

Current implementation meets this contract and degrades safely to empty chapter state.

## 8. Recommended Next Architecture Steps

1. Add canonical fixture tests for Hanuman Chalisa sequence examples.
2. Decide on long-term canonical source strategy between doha_entries and poetry_nodes.
3. Add optional explicit pointer columns for editorially non-linear chapter navigation.
4. Remove N+1 engagement aggregation in chapter stream path with batched joins.
5. Keep chapter page keyboard navigation scoped to focused reader container only.

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

## 4.4.2 Admin operations and moderation UX integration

Admin and moderation dashboards expose deeper operational flows through dedicated API integrations.

Admin settings and audit capabilities:

1. System settings screen renders full configuration table from GET /admin/system_settings.
2. Settings import uses POST /admin/system_settings/import with schema_version, dry_run preview, validation report, and atomic apply.
3. Critical setting keys require explicit confirmation text before apply.
4. Audit logs support CSV export through GET /admin/audit_logs/export/csv.
5. Audit rows expose modal detail inspection via GET /admin/audit_logs/{id} for before/after payloads and metadata.

Admin user and audit contract guardrails:

1. User role and activation changes must use PATCH /admin/users/{user_id}; there are no /role or /deactivate sub-routes.
2. Audit list/detail contracts are actor-centric and expose actor_user_id, before, after, and metadata as canonical fields.
3. Frontend admin wrapper paths are validated by an automated contract test against FastAPI route inventory to prevent stale route drift.
4. Frontend admin audit responses are validated at the response boundary using runtime schema checks.

Hierarchy and analytics contract guardrails:

1. Chapter contracts are standardized on number in backend and frontend wrappers; legacy order_num payloads are invalid.
2. Admin analytics primary contract is /admin/analytics/v2/* for top, growth, demand, and summary.
3. Legacy analytics endpoints remain fallback-only and are considered deprecated contract paths.
4. Frontend cutover uses feature flag PUBLIC_ADMIN_ANALYTICS_V2 with fallback telemetry emitted to /api/v1/telemetry/admin-analytics-cutover.

Hierarchy management behavior:

1. Inline edits for authors, works, and chapters use PATCH endpoints under /admin/hierarchy.
2. UI applies optimistic updates and rolls back on failed save.
3. Author, work, and chapter grids remain in-page without hard page reload navigation.

Moderation detail behavior:

1. Queue row selection opens dedicated moderation detail panel.
2. Panel fetches full context with GET /moderation/submissions/{submission_id} before showing decision actions.
3. Approve and reject actions are executed from the detail panel with explicit moderator notes.

## 4.5 Frontend Design System & Stacking Context

This section defines non-negotiable UI layering and styling rules for Astro and Svelte surfaces.

### 4.5.1 Global Z-Index Scale

All layered UI must use the shared scale to prevent random z-index collisions:

1. Base content: z-0
2. Floating controls and mobile sheets: z-30
3. Dropdowns and popovers: z-40
4. Sticky/fixed header and navigation shell: z-50
5. Blocking overlays/modals/error boundaries: z-100

Implementation note:

1. Global CSS variables define this scale and utility classes map to each layer.
2. New components must consume shared layer classes rather than inline arbitrary values.

### 4.5.2 Stacking Context Rules

1. Header shell must be isolated and overflow-visible so menu/popover layers can render above page content.
2. Main content area must remain at base layer and avoid creating unnecessary high-z positioned wrappers.
3. Dropdown containers must render within the designated dropdown layer and never rely on ad hoc z-[9999] patches.
4. Overlays (modals, blockers, global error boundaries) must always use the overlay layer.

### 4.5.3 Semantic Color and Typography Tokens

1. Colors must be sourced from semantic tokens (surface, border, foreground, accent) rather than scattered hardcoded hex values.
2. Interactive states (hover, active, focus-visible) must preserve contrast and remain visible in low-light backgrounds.
3. Typography hierarchy must use shared headline and body token families.
4. Reusable primitives (Button, Card, Badge, Nav link) are the default style entry point for new UI.

### 4.5.4 Responsive Overflow Safety Rules

1. Core reading containers must set min-width: 0 and max-width: 100% semantics to avoid mobile overflow.
2. Long text surfaces must use break-word/overflow-wrap safeguards.
3. Wide content blocks must use horizontal scroll wrappers on narrow viewports.
4. Mobile menus must expand as overlays/sheets, not push root layout width beyond viewport.

### 4.5.5 Visual Regression Guardrails

Before merging UI changes:

1. Validate dropdown, mobile menu, and overlay stacking on at least one content-heavy page.
2. Verify no horizontal scrollbar appears on common mobile breakpoints.
3. Confirm nav, buttons, cards, and auth menus use tokenized classes only.

Admin layout maintainability baseline:

1. Admin layout styling is scoped via tokenized classes (admin-shell, admin-nav-link, admin-main, admin-topbar) and must not use blanket :global element selectors.
2. Avoid !important in admin layout styling except for narrowly-justified third-party compatibility fixes.
3. Core admin page visual snapshots are maintained under frontend/tests/visual to catch style regressions before merge.

## 4.6 Content discovery and cross-recommendation UX

The reader experience includes cross-module discovery for article, dictionary, idiom, and work pages.

1. Work landing pages hydrate author and work context from GET /authors/{author_slug} and GET /authors/{author_slug}/works/{work_slug}.
2. Work chapter lists continue to load from GET /authors/{author_slug}/works/{work_slug}/chapters with chapter and poetry node counts.
3. Dictionary, idiom, and article detail pages consume /content/{type}/{entry_id}/navigation for previous and next controls.
4. Related content blocks at the bottom of dictionary, idiom, and article pages consume GET /recommendations/{content_type}/{content_id}.
5. Recommendation rendering is non-blocking and degrades gracefully when the endpoint returns empty or partial data.

## 4.7 Chapter Reading UX Contracts

Chapter reading and deep-link behavior are standardized as follows:

1. Chapter pages render in chapter-flow mode using typographic continuity, not stacked card blocks.
2. Each poetry node in chapter stream has a direct deep link to /poetry/{id}.
3. Poetry detail pages expose chapter-local previous and next navigation using backend chapter-scope ordering.
4. Chapter pages retain explicit separators between adjacent entries to preserve readability for mixed poetry forms.

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
