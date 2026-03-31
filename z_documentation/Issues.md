# Awadhi New Issue Log

Last updated: March 31, 2026  
Source: End-to-end audit across backend, frontend, and documentation

## Audit Scope Notes

1. Requested source file master_project_audit_and_tasks.md is not present in this workspace.
2. Resolved status below is derived from implementation and existing tests.

## Resolved From Prior Audits

1. RESOLVED: Gapped sequence navigation no longer requires n+1 consecutive numbering in legacy doha navigation tests.
2. RESOLVED: Chapter schema contract now uses number on frontend admin type definitions.
3. RESOLVED: Poetry dispatcher fallback exists and prevents rendering hard-fail on unknown poetry types.

## Active Issues By Category

## Frontend Deep Iteration (Detailed)

### FE-001: Dashboard status filter value mismatch hides pending_review entries
- Severity: High
- Area: Dashboard UX and logic
- Evidence: dashboard status filter uses value pending while backend status uses pending_review.
- Impact: users cannot filter pending submissions reliably and may assume queue loss.
- Fix direction: align filter value set with backend enums and add regression test for each status bucket.

### FE-002: Dashboard content-link routing breaks for non-doha poetry types
- Severity: High
- Area: Dashboard navigation
- Evidence: route mapper handles doha -> poetry but other poetry types can fall through to /{type}/{id} paths that do not exist.
- Impact: broken links from likes/bookmarks to content detail pages.
- Fix direction: centralize content route resolver using a shared poetry type set across dashboard, interaction bar, recommendations, and search.

### FE-003: Audit table leaks sensitive before/after/metadata payloads in hover title attributes
- Severity: High
- Area: Admin audit frontend
- Evidence: JSON payloads are placed in title attributes on list rows.
- Impact: PII and sensitive diffs are exposed in client UI beyond explicit detail view intent.
- Fix direction: remove payload-in-title pattern; show only explicit masked preview with click-to-open details.

### FE-004: Recommendations component uses runtime Tailwind class interpolation that can fail in production builds
- Severity: High
- Area: Recommendations UI rendering
- Evidence: class names are built as text-{color}-400 and hover:border-{color}-500 patterns at runtime.
- Impact: missing styles in production due to non-static class extraction, causing unreadable or unstyled cards.
- Fix direction: replace dynamic utility interpolation with static class maps or CSS variables.

### FE-005: Report and delete modals lack consistent a11y contract across app
- Severity: Medium
- Area: Dialog accessibility
- Evidence: some dialogs have role and Escape handling, others rely only on click-outside with no focus trap or initial focus.
- Impact: keyboard and assistive users face inconsistent modal behavior and escape paths.
- Fix direction: adopt one shared modal primitive enforcing focus trap, ESC close, labelledby/description, and return-focus.

### FE-006: Global keyboard event listeners still used for local UI behavior in multiple surfaces
- Severity: Medium
- Area: Keyboard interaction scope
- Evidence: chapter reader and other components bind to window/document keydown for local navigation and menus.
- Impact: cross-feature key collisions and accidental action triggers outside intended focus context.
- Fix direction: move keyboard handlers to scoped containers with explicit focus ownership.

### FE-007: Search page can produce high request fan-out under rapid typing on multi-section mode
- Severity: Medium
- Area: Search performance and UX
- Evidence: every debounced query can trigger multiple section fetches with no minimum query-length guard.
- Impact: backend load amplification, noisy partial errors, and unstable perceived responsiveness.
- Fix direction: enforce min query length, request budget by section priority, and adaptive throttling for repeated keystrokes.

### FE-008: Chapter breadcrumb truncation still compresses critical context on small screens
- Severity: Medium
- Area: Chapter page information architecture
- Evidence: strict max-width truncation on each breadcrumb segment.
- Impact: similar chapter/work names become indistinguishable in mobile navigation.
- Fix direction: add expandable breadcrumb drawer or middle-ellipsis with tap-to-expand full labels.

### FE-009: Admin desktop and mobile nav parity is inconsistent
- Severity: Low
- Area: Admin layout navigation
- Evidence: mobile nav includes analytics link while desktop sidebar omits it.
- Impact: discoverability differs by device and role, causing navigation confusion.
- Fix direction: define one source-of-truth nav config rendered in both desktop and mobile containers.

### FE-010: Console logging of admin and moderation payload errors remains in production paths
- Severity: Low
- Area: Frontend observability hygiene
- Evidence: audit, moderation, dashboard, and recommendations still emit console logs with raw error objects in several flows.
- Impact: noisy logs and potential accidental data exposure in shared machines.
- Fix direction: route logs through sanitized logger with DEV-only verbose mode.

### FE-011: Dashboard engagement KPI computation uses N-request fan-out and may not align to canonical IDs
- Severity: Medium
- Area: Dashboard data accuracy and performance
- Evidence: approved submissions are mapped into per-item content requests and use submission id assumptions.
- Impact: inaccurate totals and unnecessary latency under larger contributor histories.
- Fix direction: replace client fan-out with backend aggregate endpoint keyed by contributor and canonical content IDs.

### FE-012: Moderation board combines dense controls and data cards without explicit keyboard order cues
- Severity: Low
- Area: Moderation UX accessibility
- Evidence: mixed table/card actions, filters, and report panel updates with no documented tab-order or landmarks.
- Impact: reduced operator efficiency and keyboard-only fatigue in long sessions.
- Fix direction: add landmark headings, roving focus plan for row actions, and shortcut hints scoped to board focus.

## Admin Specific Iteration

### AD-001: Admin pages still depend on unprefixed legacy endpoints in multiple components
- Severity: High
- Area: Admin frontend API contract
- Evidence: admin components call unprefixed paths like /admin/users, /admin/system_settings, /admin/audit_logs, /auth/me, and /health directly via fetch.
- Impact: admin pages can fail when canonical-only route mode is enabled and legacy unprefixed aliases are disabled.
- Fix direction: route all admin requests through shared API wrappers that enforce /api/v1 prefix normalization.

### AD-002: Audit access policy mismatch between frontend role gate and backend authorization
- Severity: High
- Area: Admin RBAC contract
- Evidence: admin layout enforces minRole=admin while backend audit endpoints authorize moderator and apply row-level restrictions for non-admin users.
- Impact: moderators who are contractually allowed to access their own audit rows are blocked by frontend navigation and guard policy.
- Fix direction: align role policy across frontend and backend by either restricting backend to admin or exposing a moderator-safe audit surface and navigation path.

### AD-003: Admin API client behavior is fragmented across raw fetch, lib/api, and lib/admin
- Severity: Medium
- Area: Admin frontend reliability
- Evidence: some admin components use raw fetch, others use api(), and others use admin.ts wrappers with different auth, retry, and error semantics.
- Impact: inconsistent token refresh handling, inconsistent error UX, and higher chance of endpoint drift across admin modules.
- Fix direction: standardize admin data access on a single typed client layer and ban direct endpoint strings in Svelte admin components.

### AD-004: Hierarchy chapter select change handler calls loadChapters with wrong arguments
- Severity: High
- Area: Admin hierarchy editor
- Evidence: create chapter work selector triggers loadChapters(newChapter.work_id) while loadChapters requires authorSlug and workSlug.
- Impact: malformed chapter list requests and broken chapter preview/loading flow during chapter creation.
- Fix direction: wire selector change to resolved author and work slugs (or id-based endpoint) and add regression test for create-chapter work selection.

### AD-005: Admin health/status panel bypasses canonical auth and route helpers
- Severity: Medium
- Area: Admin observability panel
- Evidence: SystemStatus component performs direct fetch calls with ad hoc base fallback and localStorage token checks instead of shared wrappers.
- Impact: duplicated network logic, inconsistent diagnostics, and silent drift from canonical API behavior.
- Fix direction: migrate SystemStatus probes to shared api/admin client helpers with normalized base handling.

## Moderation Specific Iteration

### MOD-001: Frontend batch moderation endpoints do not match backend contracts
- Severity: High
- Area: Moderation frontend and backend API contract
- Evidence: queue calls /moderation/batch-approve and /moderation/batch-reject, while backend exposes /moderation/batch and /moderation/batch_approve.
- Impact: batch approve and reject actions from moderation queue can fail at runtime with 404 or contract errors.
- Fix direction: align on one canonical batch contract (prefer /moderation/batch with action enum), update frontend calls, and add endpoint contract test.

### MOD-002: Contributor enrichment fallback uses unsupported admin users query shape
- Severity: Medium
- Area: Moderation queue data enrichment
- Evidence: moderation UI fallback calls /admin/users?ids={id}, but admin users API supports q, limit, and offset instead of ids.
- Impact: contributor identity labels degrade to id-only more often and increase operator friction during triage.
- Fix direction: use /users/id/{id} as canonical lookup with typed fallback, or extend backend with explicit ids query support.

### MOD-003: Queue assignment filters allow conflicting state with ambiguous backend behavior
- Severity: Medium
- Area: Moderation queue UX and query semantics
- Evidence: UI allows both My Queue and Unassigned toggles simultaneously; backend applies assigned_to_me first and ignores unassigned_only when both are true.
- Impact: moderators can assume both filters are active while results are silently narrowed to one mode.
- Fix direction: enforce mutual exclusivity in UI and backend validation for conflicting filters.

### MOD-004: Moderation page lacks explicit route guard unlike admin surfaces
- Severity: Medium
- Area: Moderation access control UX
- Evidence: moderation pages are rendered without frontend role guard, relying only on backend 403 responses.
- Impact: non-moderator users can access moderation route shell, then hit noisy error states instead of clean redirect or denial UX.
- Fix direction: add shared AuthGuard minimum moderator role for moderation routes.

### MOD-005: Exception path in moderation detail endpoint references undefined logger
- Severity: High
- Area: Moderation backend reliability
- Evidence: get_submission_for_moderation except block calls logger.exception without module-level logger binding.
- Impact: internal retrieval errors can cascade into NameError, obscuring root cause and degrading incident diagnostics.
- Fix direction: define module logger once and use consistently across endpoint handlers.

### MOD-006: Moderation detail edit path bypasses moderation-scoped API client conventions
- Severity: Low
- Area: Moderation frontend consistency
- Evidence: moderation detail performs direct api calls to /submissions/{id} update while queue actions use moderation-specific wrappers.
- Impact: mixed client patterns increase drift risk for auth, error handling, and future schema evolution.
- Fix direction: consolidate moderation detail actions under shared typed moderation client functions.

## User Specific Iteration

### USR-001: Dashboard status filter uses pending while backend status is pending_review
- Severity: High
- Area: User dashboard submissions UX
- Evidence: dashboard submissions filter option value is pending, but backend submission status enum and query filtering use pending_review.
- Impact: users cannot reliably filter pending-review submissions from dashboard and may assume missing items.
- Fix direction: align dashboard filter values with backend status constants and add status filter regression coverage.

### USR-002: Published link from submissions list can route to invalid paths for approved content
- Severity: High
- Area: User submissions navigation
- Evidence: approved submission link uses /{content_type}/{submission_id}, which does not match canonical content routes for types like doha (served via /poetry/{id}) and can mismatch canonical content ids.
- Impact: contributors click View Published and land on 404 or wrong content page.
- Fix direction: use canonical content_path from backend, or resolve route and canonical content id via typed mapping API.

### USR-003: Profile editor bypasses shared API client and canonical path normalization
- Severity: Medium
- Area: User profile frontend contract
- Evidence: profile editor uses raw fetch calls to /auth/me and /users/me with manual token handling instead of shared api/auth helpers.
- Impact: inconsistent refresh/auth error handling and higher risk when canonical-only prefixed routing is enforced.
- Fix direction: migrate profile editor network calls to shared lib/api or lib/auth helpers with normalized /api/v1 behavior.

### USR-004: User-surface implementation is fragmented between active dashboard components and legacy user components
- Severity: Medium
- Area: User frontend maintainability and styling consistency
- Evidence: live pages use dashboard components while separate user folder contains older dashboard/submission/bookmark components with stale routes (for example /profile/edit) and mixed light-theme stone palette classes.
- Impact: maintenance drift, style inconsistency, and risk of reintroducing deprecated paths if old components are reused.
- Fix direction: retire unused user components or refactor them to current route and design contracts, then enforce dead-code checks.

### USR-005: User dashboard engagement metrics rely on submission-id fan-out assumptions
- Severity: Medium
- Area: User analytics correctness and performance
- Evidence: dashboard metrics fan out detail fetches using submission ids mapped as content ids and type-derived routes.
- Impact: inaccurate engagement totals and avoidable latency spikes for heavy contributor accounts.
- Fix direction: replace client fan-out with backend aggregate endpoint keyed by contributor and canonical content ids.

### USR-006: Public profile and dashboard lack dedicated frontend integration test coverage
- Severity: Medium
- Area: Test coverage
- Evidence: frontend test suite has extensive admin coverage but no user profile/dashboard/submissions integration scenarios.
- Impact: regressions in user-critical journeys can ship unnoticed.
- Fix direction: add integration and E2E tests for profile load/edit, dashboard filters, canonical published links, and bookmarks/likes pagination.

## Data Collection Specific Iteration

### DC-001: Governance checklist API contract mismatches frontend consumer fields
- Severity: High
- Area: Governance telemetry UI contract
- Evidence: backend checklist returns keys like row_level_access and model_governance_trail, while frontend expects row_level_controls, immutable_model_trail, and review_ready.
- Impact: mission-control governance readiness can render incorrect states or undefined values, weakening trust in governance reporting.
- Fix direction: define one versioned checklist schema and enforce it through shared types and contract tests.

### DC-002: SLO failure breakdown type drift hides failure class labels
- Severity: Medium
- Area: Admin observability dashboard
- Evidence: backend SLO summary returns top_failure_classes entries with error_code, while frontend type and rendering expect failure_class.
- Impact: failure breakdown labels can appear blank or misleading even when backend has valid error-class data.
- Fix direction: align frontend type/render keys to backend payload and add schema assertion in integration tests.

### DC-003: Frontend telemetry emitter coverage is very narrow for collection requirements
- Severity: Medium
- Area: Collection completeness and attribution
- Evidence: frontend emits telemetry only for auth-policy and poetry renderer fallback; no broad client instrumentation for admin-events ingest path.
- Impact: behavioral analytics under-samples real operator journeys and weakens root-cause correlation across UI actions.
- Fix direction: expand standardized client event emitters for high-value admin and moderation actions using shared telemetry utility.

### DC-004: Completeness metric treats optional telemetry attributes as required
- Severity: Medium
- Area: Data quality KPI logic
- Evidence: completeness ratio requires fields such as error_code, before_state_hash, after_state_hash, and latency_ms for every event even when contextually not applicable.
- Impact: completeness percentage can be artificially low or gamed, reducing decision quality for observability SLOs.
- Fix direction: split required vs conditional fields by event_type/result and compute weighted completeness by applicability rules.

### DC-005: Moderation triage recommendation logging is append-heavy on read path
- Severity: Medium
- Area: Model governance data pipeline
- Evidence: each moderation-triage read request appends recommendation events for returned rows, without dedupe idempotency across polling cycles.
- Impact: model governance event table can accumulate noisy duplicates, inflating storage and obscuring true decision lineage.
- Fix direction: introduce recommendation idempotency window keyed by submission and model version, or log only on state-change.

### DC-006: Retention execution is manual-only with no scheduled enforcement path
- Severity: Low
- Area: Data lifecycle governance
- Evidence: retention job is exposed through governance endpoint but no recurring scheduler or startup orchestration invokes it automatically.
- Impact: stale telemetry and governance data may persist beyond policy windows if operators do not trigger retention manually.
- Fix direction: add scheduled retention runner (cron/worker) with run history auditing and alerting on missed windows.

## Code Clarity And Reusability Iteration

### CR-001: API base resolution is duplicated across many frontend pages and components
- Severity: High
- Area: Frontend code clarity and reduction
- Evidence: repeated API_BASE declarations exist across auth pages, admin pages, submission pages, and multiple Svelte components, while centralized helpers already exist in lib/api and lib/auth.
- Impact: inconsistent base-path behavior, harder refactors, and high maintenance overhead for one conceptual concern.
- Fix direction: enforce one canonical API base source (lib/api), remove local API_BASE declarations, and codemod remaining direct declarations.

### CR-002: Auth-header helper logic is copy-pasted in multiple components
- Severity: Medium
- Area: Frontend reusability
- Evidence: getAuthHeader is reimplemented in admin and submission components instead of using shared auth utilities.
- Impact: token-handling behavior drifts over time and increases bug surface for auth edge cases.
- Fix direction: expose one shared authenticated-request helper and replace component-local auth-header builders.

### CR-003: Content route mapping logic is duplicated in dashboard and user components
- Severity: Medium
- Area: Frontend code reuse
- Evidence: getContentRoute mapping appears in multiple components with parallel route dictionaries.
- Impact: route updates require multi-file edits and can introduce inconsistent published-link behavior.
- Fix direction: move content-type to route resolution into one shared utility with typed canonical mapping.

### CR-004: Role-rank comparison logic exists in multiple frontend modules
- Severity: Medium
- Area: Frontend clarity and policy consistency
- Evidence: role-rank maps are defined separately in auth guard and admin role helpers.
- Impact: subtle RBAC drift risk and duplicated policy maintenance.
- Fix direction: centralize role-rank and min-role evaluation in one shared role-policy module.

### CR-005: Moderation approve and reject flows duplicate large backend and frontend logic blocks
- Severity: Medium
- Area: Moderation code simplification
- Evidence: approve and reject handlers contain repeated validation, logging, and model-event append patterns in backend and mirrored payload handling in frontend admin client.
- Impact: high change cost and increased chance of asymmetric bug fixes between approve and reject paths.
- Fix direction: extract shared moderation transition helper with action strategy parameter and reuse in both single and batch flows.

### CR-006: Router mounting in backend bootstrap is highly repetitive for prefixed and legacy modes
- Severity: Medium
- Area: Backend maintainability
- Evidence: main app includes long duplicated include_router blocks for canonical and legacy route registration.
- Impact: onboarding friction and high risk of missed router registration changes when new modules are added.
- Fix direction: define a router registry list and iterate through it for both canonical and legacy mounting paths.

### CR-007: Legacy user component stack remains beside active dashboard stack
- Severity: Low
- Area: Frontend code reduction and styling consistency
- Evidence: user folder still contains alternate dashboard/submission/bookmark implementations while active routes use dashboard components.
- Impact: dead or near-dead code increases cognitive load and can reintroduce stale routes or style regressions during future edits.
- Fix direction: remove deprecated user components or formally migrate them to active routes, then enforce dead-code detection in CI.

## SEO Specific Iteration

### SEO-001: Search result pages are indexable and can create high-volume low-value URL variants
- Severity: High
- Area: Crawl budget and index quality
- Evidence: search route is renderable and query-driven while remaining indexable, allowing many near-duplicate query URLs to be crawled and indexed.
- Impact: crawl budget is diluted away from canonical content pages and search-result URLs can compete with destination pages in rankings.
- Fix direction: set noindex, follow on query-result views and keep canonical pointing to stable content hubs instead of query variants.

### SEO-002: Sitemap generation is capped and may not cover full long-tail inventory
- Severity: High
- Area: Discovery coverage
- Evidence: sitemap builders use fixed fetch limits for dynamic collections, which can omit deeper content once corpus size exceeds page caps.
- Impact: older or lower-frequency pages may never be discovered or refreshed by crawlers.
- Fix direction: move to cursor-based full export or sitemap index splitting with deterministic pagination until exhaustion.

### SEO-003: Canonical strategy is inconsistent across filter or pagination states in listing routes
- Severity: High
- Area: Canonicalization
- Evidence: list pages define static canonical targets while runtime state can vary by query or page context.
- Impact: duplicate URL variants can remain indexable without a strong canonical consolidation signal.
- Fix direction: define canonical rules per state class (default list, filtered list, paginated list) and enforce with a shared helper.

### SEO-004: Structured data coverage is sparse across major listing and hub pages
- Severity: Medium
- Area: Rich results and entity understanding
- Evidence: only a small subset of routes import structured-data components relative to total page count, leaving key hubs without schema signals.
- Impact: reduced eligibility for rich snippets and weaker machine understanding of site entity relationships.
- Fix direction: add route-class schema minimums (WebSite, CollectionPage, BreadcrumbList, ItemList) and validate in CI.

### SEO-005: Catch-all slug routing increases duplicate-index risk without strict canonical and index policy guardrails
- Severity: High
- Area: Dynamic routing and deduplication
- Evidence: catch-all route resolves multiple content forms and relies on runtime content resolution where alias paths can emerge.
- Impact: semantically identical content may be reachable through multiple URLs, weakening ranking consolidation.
- Fix direction: enforce single canonical path resolution, redirect non-canonical aliases, and apply defensive noindex for unresolved ambiguous states.

### SEO-006: Robots directives are broad and not explicitly aligned to non-content utility surfaces
- Severity: Medium
- Area: Crawl governance
- Evidence: robots generation allows broad crawling while several utility, auth, and dashboard-like surfaces are separately controlled mainly by page-level logic.
- Impact: bot requests can over-target low-value paths, increasing crawl noise and server load.
- Fix direction: harden robots disallow rules for non-public utility patterns and keep allow-list focus on index-worthy public content paths.

### SEO-007: Hreflang output defaults to x-default without language alternates strategy
- Severity: Low
- Area: International SEO readiness
- Evidence: layout emits x-default relation but does not define alternate locale URLs or strategy guardrails.
- Impact: international expansion can launch with incomplete hreflang clusters and cause geo-language misrouting.
- Fix direction: implement locale-aware alternate generation when multilingual routes exist, otherwise avoid partial hreflang signaling.

### SEO-008: SEO contract enforcement is missing in automated tests for route classes
- Severity: Medium
- Area: Regression prevention
- Evidence: existing manual checks include some SEO cases, but there is no route-class contract suite systematically verifying canonical, robots, and schema presence.
- Impact: metadata regressions can ship silently during page refactors.
- Fix direction: add automated SEO contract tests per route archetype (detail, list, search, catch-all, auth/system) and gate CI on failures.

## API Surface Simplification (Second Hard Iteration)

### API-001: Analytics endpoint duplication between insights and legacy v2 tree
- Severity: High
- Area: Backend API contract
- Evidence: /api/v1/admin/analytics/insights already multiplexes summary, top, growth, demand, engagement-summary, throughput, cycle-time, rbac-denials, events, and 3d views, while /api/v1/admin/analytics/v2/* endpoints still exist as parallel aliases.
- Impact: Larger contract surface, duplicate client adapters, increased test and docs maintenance.
- Fix direction: Make insights the canonical read endpoint and move v2 endpoints behind staged deprecation with compatibility sunset dates.

### API-002: Interactions API has both action router and verb-specific endpoints
- Severity: High
- Area: Backend API contract
- Evidence: /api/v1/interactions/master supports toggle/share/report/list actions while /api/v1/interactions/toggle, /share, /report, /users/{id}/bookmarks, and /users/{id}/likes still mirror the same operations.
- Impact: Redundant route inventory and dual client paths for identical logic.
- Fix direction: Keep one canonical style (action endpoint or resource endpoints), mark the other as compatibility-only, and remove duplicate docs exposure.

### API-003: Legacy naming aliases for poetry and doha remain duplicated
- Severity: Medium
- Area: Backend content API
- Evidence: multiple dual-route declarations map both poetry and doha names to the same handlers, including list/detail/navigation/history/chapter routes.
- Impact: Naming drift and unnecessary OpenAPI complexity for new clients.
- Fix direction: Standardize canonical poetry naming with documented doha compatibility aliases and explicit deprecation policy.

### API-004: Type-specific navigation endpoints can be unified by content_type parameter
- Severity: Medium
- Area: Backend content API
- Evidence: /content/dictionary/{id}/navigation, /content/idiom/{id}/navigation, and /content/article/{id}/navigation execute the same navigation service with only content_type differences.
- Impact: Repeated route code and wider endpoint learning surface.
- Fix direction: Introduce /content/{content_type}/{id}/navigation as canonical path and retain specific endpoints as backward-compatible aliases.

### API-005: Legacy unprefixed route mode enabled by default outside production
- Severity: Medium
- Area: Backend bootstrap and contract governance
- Evidence: ENABLE_LEGACY_UNPREFIXED_ROUTES defaults true for non-production, causing both prefixed and unprefixed route sets to be mounted.
- Impact: Environment-dependent behavior and accidental client dependence on non-canonical paths.
- Fix direction: Default legacy mode to false in all environments and enable only in explicit compatibility test runs.

### API-006: Public read endpoints for dictionary, idiom, article, and poetry search are split despite similar query semantics
- Severity: Low
- Area: Backend read APIs
- Evidence: separate modules expose near-identical paging/filter patterns with partial overlap in search and sorting semantics.
- Impact: Increased frontend branching and inconsistent filtering UX.
- Fix direction: Add a canonical multi-type search/read gateway with content_type parameter, then keep module routes for deep detail only.

## Wiring

### WR-001: Split canonical delivery path between doha_entries and poetry_nodes
- Severity: High
- Area: Backend API, frontend route strategy
- Evidence: content endpoints still serve doha_entries while chapter and poetry detail pages serve poetry_nodes.
- Impact: Duplicate logic, migration ambiguity, contract drift risk between old and new clients.
- Fix direction: Define one canonical read model for chapter-bound poetry; keep the other as compatibility layer with explicit deprecation timeline.

### WR-002: API reference usage mapping appears globally over-broadened
- Severity: Medium
- Area: Documentation generation
- Evidence: many operations list identical unrelated frontend references.
- Impact: Integrators cannot trust endpoint-to-consumer mapping.
- Fix direction: tighten usage scanner to endpoint-specific call graph extraction.

### WR-003: Environment-level route mode can hide contract drift until production
- Severity: Medium
- Area: Backend runtime wiring
- Evidence: development defaults mount compatibility routes that production may not mount.
- Impact: frontend integrations can pass locally and break when legacy mode is disabled.
- Fix direction: run default local stack with canonical routes only and execute compatibility mode in dedicated regression jobs.

## Styling

### ST-001: Chapter reader visual hierarchy weak for long sessions
- Severity: Medium
- Area: Frontend chapter UX
- Evidence: chapter entry cards are visually similar; active item signal is subtle and easy to lose in long chapters.
- Impact: Reader fatigue, poor orientation in dense scripture-like chapters.
- Fix direction: stronger active marker, sticky sequence rail, and reduced visual noise for non-current entries.

### ST-002: Breadcrumb and chapter title truncation can hide semantic context
- Severity: Medium
- Area: Frontend responsive layout
- Evidence: narrow max-width truncation in breadcrumb list can collapse meaningful titles.
- Impact: Users lose orientation inside similarly named chapters.
- Fix direction: progressive reveal tooltip and responsive wrapping strategy for medium screens.

### ST-003: Form color language inconsistent across poetry types and generic fallback
- Severity: Low
- Area: Frontend renderer consistency
- Evidence: each renderer uses independent accent tone; fallback tone can look unrelated.
- Impact: weak type recognition and inconsistent chapter reading rhythm.
- Fix direction: define poetry type color tokens and unify badge treatment.

## Data Structure

### DS-001: No explicit prev_node_id or next_node_id in poetry_nodes
- Severity: Medium
- Area: Database model
- Evidence: pointers are computed from sequence_no only.
- Impact: cannot support editorial non-linear links without custom logic.
- Fix direction: add optional explicit pointers with invariant checks and fallback to sequence-based navigation.

### DS-002: Dual canonical stores for doha content semantics
- Severity: High
- Area: Backend data model
- Evidence: doha_entries and poetry_nodes both hold doha-like canonical content.
- Impact: synchronization burden, duplicate moderation materialization pathways, reporting inconsistency.
- Fix direction: staged consolidation plan with compatibility adapters.

### DS-003: Hanuman Chalisa real-text fixture missing
- Severity: Medium
- Area: Test data quality
- Evidence: tests use synthetic lines and do not assert expected religious-text pointer chain.
- Impact: business-critical semantic examples are not regression-protected.
- Fix direction: add seeded fixture with line-level assertions for Jai Hanuman -> Ram dut atulit -> Mahavir vikram.

## Optimization

### OP-001: N+1 engagement aggregation in chapter stream
- Severity: High
- Area: Backend poetry service
- Evidence: current serializer queries engagement rows per node during stream response.
- Impact: latency spikes under large chapters and high traffic.
- Fix direction: batch query engagement by content_id list and merge in memory once per response.

### OP-002: View recording on streamed chapter responses can amplify write load
- Severity: Medium
- Area: Backend analytics write path
- Evidence: per-item view events are recorded during stream fetch.
- Impact: read-heavy chapter browsing creates high write amplification.
- Fix direction: aggregate client-side read events with debounce and server-side batch ingestion.

### OP-003: Chapter lookup path does multiple sequential requests in SSR
- Severity: Medium
- Area: Frontend chapter page data loading
- Evidence: chapter slug resolution then stream request chain.
- Impact: extra request latency before first meaningful paint.
- Fix direction: add single backend endpoint resolving author/work/chapter by slug and returning initial stream.

## Logical Flow

### LF-001: Global arrow key handling hijacks navigation outside reader context
- Severity: High
- Area: Frontend accessibility and UX
- Evidence: chapter reader binds window-level arrow handlers.
- Impact: interferes with expected browser and assistive navigation behavior.
- Fix direction: scope keyboard controls to focused reader region and visible controls.

### LF-002: Previous and Next button enablement tied to loaded window, not chapter total
- Severity: Medium
- Area: Frontend chapter navigation logic
- Evidence: canGoNext depends on loadedItems length and current index before async load completion.
- Impact: transient navigation confusion at chunk boundaries.
- Fix direction: explicit hasNextByTotal state and loading transition guard.

### LF-003: Position label uses sequence_no/total semantics that may mislead with sparse numbering
- Severity: Low
- Area: Frontend reader semantics
- Evidence: display uses sequence_no as if it were ordinal index.
- Impact: in gapped sequences, user may infer missing content as bug.
- Fix direction: show both sequence number and list position when numbering is sparse.

## Module-By-Module Summary

1. Hierarchy module
Stable parent-child mapping. Main risk is dual canonical child stores.

2. Poetry service module
Correct neighbor resolution logic but has performance and analytics write amplification issues.

3. Content service module
Legacy doha navigation works; long-term maintenance risk remains due to split model.

4. Chapter page module
Good baseline rendering for mixed forms, but keyboard scope and dense-layout readability need improvement.

5. Documentation module
Previously fragmented and partially stale; now consolidated but API consumer mapping generator needs correction.

6. API contract module
Functionally rich but over-expanded through alias layers; simplification via parameterized canonical endpoints is the highest leverage reduction for long-term maintenance.
