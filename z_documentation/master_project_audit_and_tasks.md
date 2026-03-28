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

## Linked Dependencies

- STYLING-003 has been removed from active issues in `z_documentation/issues/Issues.md`.
