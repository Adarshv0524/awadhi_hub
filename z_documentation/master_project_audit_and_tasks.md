# Master Project Audit and Tasks

## Resolved

- [COMPLETED] Schema Guardrail (DATA-002): Added CI schema contract validation via `backend/scripts/schema_contract_check.py` and integrated it in `.github/workflows/test.yml` before the main backend test suite.
- [ARCHIVED/OPTIMIZED] OPTIMIZATION-001: Chapter bulk slug endpoint proposal archived after timing audit; current path-based chapter endpoint is stable and sub-100ms.
- [ARCHIVED/OPTIMIZED] OPTIMIZATION-002: Doha eager navigation embedding archived for now; retained as future `DohaDetailOut` option to preserve lean list payloads.
- [COMPLETED] LOGICAL-001: Moderator/admin can now update submission hierarchy metadata inline (`author_slug`, `work_slug`, `chapter_slug`, `number_in_chapter`, `is_classical`) with hierarchy validation and role-gated access control.
- [COMPLETED] LOGICAL-002: Likes retrieval endpoint (`GET /interactions/users/{user_id}/likes`) now matches bookmarks parity with owner/admin access control, paginated response, and content previews from joined content tables.
- [COMPLETED] LOGICAL-003: Universal chapter-scoped navigation is implemented with `ContentNavigationOut` and endpoints for doha/dictionary/idiom/article, using deterministic ordering by `number_in_chapter` with `created_at`/`id` fallback.
- [COMPLETED] LOGICAL-004: Public user stats endpoint (`GET /users/{username}/stats`) now aggregates approved contributions, KPI likes received, most-liked content id, average engagement score, and joined date for profile display.
- [COMPLETED] STYLING-003: `NavigationControls` is now enabled across dictionary/idiom/article detail pages using type-aware routing, contextual labels (for example, Next Definition/Next Article), and consistent sticky placement.
- [COMPLETED - CRITICAL] CRIT-001: Article router static-first ordering enforced in `backend/app/api/v1/article.py`; static endpoints (`/tags/list`, `/recent/list`, `/by-tag/{tag}`) now resolve before dynamic `/{article_id}` to prevent integer-validation shadowing.
- [COMPLETED - CRITICAL] CRIT-002: Idiom submission contract aligned end-to-end; frontend now captures Romanized Text (`text_roman`) and passes it in `external_references`, while moderation canonicalization maps it into `idiom_entries.text_roman`.
- [COMPLETED - HIGH] HIGH-001: Search filter chips now drive functional request fan-out in `frontend/src/pages/search.astro`; filtered mode calls only the selected content endpoint and renders only that category section.
- [COMPLETED - SECURITY] HIGH-002: Search SSR logging sanitized in `frontend/src/pages/search.astro`; raw user query and response payload logging removed, with development-only guarded high-level error/status logs.
- [COMPLETED - ACCESSIBILITY] HIGH-003: `frontend/src/components/interaction/InteractionBar.svelte` now uses semantic button interactions, labeled form controls in modal dialogs, and keyboard-focus-safe modal behavior.
- [COMPLETED - SEO] HIGH-004: Metadata generation is centralized in `frontend/src/layouts/BaseLayout.astro` with prop-driven `title`, `description`, and `canonicalURL`; detail pages now pass SEO props instead of emitting duplicate head tags.
- [COMPLETED - PERFORMANCE] HIGH-005: Chapter listing moved to hybrid pagination; `frontend/src/pages/[author]/[work]/[chapter].astro` now SSR-fetches only first page and `frontend/src/components/content/ChapterList.svelte` incrementally appends additional pages via observer/load-more.
- [COMPLETED - CONSISTENCY] MED-001: List endpoints for doha/article/dictionary/idiom now expose explicit `sort` and `order` query params with `created_at desc` as the universal default ordering policy.
- [COMPLETED - CONSISTENCY] MED-002: Public user stats now use one approved+public canonical scope for `contributions_count`, `likes_received`, and `average_engagement_score`, with explicit field-level scope descriptions in `UserStatsOut`.
- [COMPLETED - MAINTENANCE] MED-003: Frontend submission form updated with technical contract notes referencing current idiom submission alignment (CRIT-002). Stale comments removed and replaced with precise documentation pointing to Architecture.md Section 3.4.
- [COMPLETED - OPTIMIZATION] MED-004: Search page optimization verified and documented; filter logic already implements conditional API fan-out (only calls requested content type endpoints when filter is active, calls all endpoints when filter is 'all'). Added explanatory comments to `frontend/src/pages/search.astro`.
- [COMPLETED - MAINTENANCE] LOW-001: Documentation consolidation completed; single source of truth established in `z_documentation/issues/Issues.md` with governance notices added to README.md, RUNTIME_ANALYSIS.md, and MODULE_STATUS_REPORT.md to prevent status drift across multiple files.

## Linked Dependencies

- STYLING-003 has been removed from active issues in `z_documentation/issues/Issues.md`.
