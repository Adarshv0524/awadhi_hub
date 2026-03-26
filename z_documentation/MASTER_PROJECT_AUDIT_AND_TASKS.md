# Master Project Audit and Module Task Plan

Date: 2026-03-26
Scope: End-to-end functional and structural audit (backend, frontend, data model, auth, hierarchy-content wiring, UX, testing)

## 1) Executive Snapshot

Overall status: Functional core with strong foundations, but incomplete sequence-navigation and a few key backend-frontend contract gaps.

Top priorities:
1. Build chapter-sequenced content APIs with next/previous navigation.
2. Complete moderation metadata editing support.
3. Finish missing user dashboard APIs (likes and public stats).
4. Wire frontend Google OAuth login trigger.

## 2) How Hierarchy Uses Doha/Chaupai-like Content

Implemented relationship model:
- Author -> Work -> Chapter lives in hierarchy tables.
- Canonical content (doha, dictionary, idiom, article) can store hierarchy links through author_id, work_id, chapter_id, and number_in_chapter.
- Doha is the most complete hierarchy-linked content flow in current APIs.

Current rendering behavior:
- Work/chapter pages are browsed via hierarchy APIs.
- Chapter page attempts a leaf fetch via path first, then falls back to search filtered by author/work/chapter.
- This means chapter display is available, but it is not guaranteed to be served from a strict chapter-ordered endpoint.

Hanuman Chalisa-style sequencing gap:
- Desired behavior for a verse should include prev/current/next adjacency.
- Data supports ordering through number_in_chapter.
- Missing piece is dedicated API + frontend navigation wiring for adjacency.

## 3) Confirmed Findings (Issue Style)

### ISSUE-001: Missing next/prev verse navigation API
Severity: Critical
Type: Logical + UX

Problem:
- No endpoint currently returns adjacent doha nodes (previous and next) based on chapter and number_in_chapter.

Impact:
- Reader cannot move verse-by-verse in paath order.
- Hanuman Chalisa style guided reading is incomplete.

Evidence:
- backend/app/api/v1/content.py: only list/get/history/by-path for doha.
- grep across backend/app shows no navigation endpoint for next/prev.

Improvement:
1. Add GET /content/doha/{id}/navigation.
2. Resolve current doha -> chapter_id + number_in_chapter.
3. Query previous and next by chapter_id ordered around number_in_chapter.
4. Return minimal cards for prev/current/next.

---

### ISSUE-002: Chapter page relies on fallback search, not dedicated chapter-content API
Severity: High
Type: Wiring + Optimization

Problem:
- frontend/src/pages/[author]/[work]/[chapter].astro fetches path leaf and then search fallback.

Impact:
- Extra API round trips.
- Potential ordering inconsistency for chapter listing context.

Evidence:
- frontend/src/pages/[author]/[work]/[chapter].astro uses:
  - /content/by-path/{encodedHierarchy}
  - /search?author=&work=&chapter=

Improvement:
1. Add GET /content/chapters/{chapter_id}/dohas?offset=&limit= sorted by number_in_chapter.
2. Optionally add slug-based endpoint variant.
3. Update chapter page to prefer dedicated endpoint and render sequence index.

---

### ISSUE-003: Moderator inline edit cannot update hierarchy metadata
Severity: High
Type: Workflow + Moderation

Problem:
- SubmissionUpdateIn excludes author_slug/work_slug/chapter_slug/number_in_chapter/is_classical.

Impact:
- Moderators can fix text but cannot correct structural metadata directly.
- Causes unnecessary rejection-resubmission loop.

Evidence:
- backend/app/api/v1/submissions.py SubmissionUpdateIn
- Existing docs in BACKEND_ISSUE_moderator_inline_editing_metadata.md and BACKEND_FIX_moderator_editing.txt

Improvement:
1. Extend SubmissionUpdateIn with optional metadata fields.
2. Enforce moderator/admin-only metadata modifications.
3. Re-run classical validation when metadata fields are changed.

---

### ISSUE-004: Missing likes endpoint for dashboard tab
Severity: High
Type: Feature parity

Problem:
- Dashboard likes tab is placeholder; endpoint absent.

Impact:
- User profile/dashboard incomplete.

Evidence:
- backend/app/api/v1/interactions.py includes bookmarks endpoint only.
- frontend/src/components/dashboard/DashboardClient.svelte includes explicit TODO text for likes endpoint.

Improvement:
1. Add GET /interactions/users/{user_id}/likes.
2. Return count + paginated result records.
3. Apply owner-or-admin access policy.

---

### ISSUE-005: Missing public user stats endpoint
Severity: High
Type: Product completeness

Problem:
- Public profile stats endpoint is missing.

Impact:
- User pages cannot show real contribution stats.

Evidence:
- backend/app/api/v1/users.py currently exposes only GET /users/{username}.
- Spec already written in z_documentation/BACKEND_TODO_user_stats.md.

Improvement:
1. Add GET /users/{username}/stats.
2. Return approved/public contributions and aggregate engagement.

---

### ISSUE-006: Backend OAuth callback exists, but frontend login still email-only
Severity: Medium
Type: Auth UX

Problem:
- OAuth callback endpoint is implemented, but login UI keeps Google login as TODO.

Impact:
- OAuth capability is not reachable by users.

Evidence:
- backend/app/api/v1/auth.py has /auth/oauth/google/callback.
- frontend/src/pages/login.astro comments out Google button.

Improvement:
1. Add Google sign-in CTA to login page.
2. Implement start-auth redirect flow and callback handling in frontend.

---

### ISSUE-007: Model/migration drift required corrective migration
Severity: Medium
Type: Data integrity

Problem:
- Runtime-critical column naming mismatches previously existed.

Impact:
- Production/runtime instability risk if drift recurs.

Evidence:
- backend/alembic/versions/0014_reconcile_schema_drift_runtime_critical.py handles:
  - submissions.references -> submissions.external_references
  - system_settings.key -> system_settings.setting_key
  - alembic_version.version_num widening

Improvement:
1. Add schema-contract CI check against ORM metadata.
2. Add migration smoke test in CI against clean DB + upgrade path.

---

### ISSUE-008: Chapter sequence tests are missing
Severity: Medium
Type: Test coverage

Problem:
- Current tests cover hierarchy, auth, submissions, search, etc., but not explicit chapter adjacency behavior.

Impact:
- Regressions in sequence logic may go undetected.

Evidence:
- backend/tests has no dedicated test for doha next/prev chapter navigation.

Improvement:
1. Add test_content_navigation.py.
2. Cover previous/current/next edge cases:
   - first node has no previous
   - last node has no next
   - gaps in number_in_chapter

## 4) Module-by-Module Task Plan (Do One by One)

### Module A: Data and Hierarchy Contract
Status: Not Started
Tasks:
- [ ] A1: Define canonical ordering rules for chapter content by content type.
- [ ] A2: Specify primary/secondary ordering fields (number_in_chapter, created_at fallback).
- [ ] A3: Define path and slug normalization rules for hierarchy_path.

### Module B: Content Navigation APIs
Status: Not Started
Tasks:
- [ ] B1: Add endpoint to list chapter dohas in strict order.
- [ ] B2: Add endpoint for doha adjacency (prev/current/next).
- [ ] B3: Add response DTO with chapter metadata and sequence index.
- [ ] B4: Add query constraints for visibility/status/is_deleted.

### Module C: Submission and Moderation Editing
Status: Not Started
Tasks:
- [ ] C1: Extend SubmissionUpdateIn for metadata fields.
- [ ] C2: Add role guard for metadata editing.
- [ ] C3: Re-validate classical references on metadata update.
- [ ] C4: Add regression tests for moderator edits.

### Module D: User Dashboard API Completion
Status: Not Started
Tasks:
- [ ] D1: Implement user likes endpoint.
- [ ] D2: Implement user public stats endpoint.
- [ ] D3: Add pagination and authorization checks.
- [ ] D4: Integrate into dashboard/profile frontend views.

### Module E: Frontend Navigation and Presentation
Status: Not Started
Tasks:
- [ ] E1: Update chapter route to use chapter-content endpoint first.
- [ ] E2: Add visible ordered verse list with sequence number badges.
- [ ] E3: Add prev/next controls on doha detail page.
- [ ] E4: Add graceful fallback when adjacency is missing.

### Module F: Auth UX Completion
Status: Not Started
Tasks:
- [ ] F1: Add Google sign-in button and auth-init route.
- [ ] F2: Parse callback result and persist tokens safely.
- [ ] F3: Add error states for OAuth cancellation/failure.

### Module G: Testing and CI Hardening
Status: Not Started
Tasks:
- [ ] G1: Add chapter navigation unit/integration tests.
- [ ] G2: Add API contract tests for all content response fields.
- [ ] G3: Add migration drift smoke tests.
- [ ] G4: Add end-to-end happy path test (author -> work -> chapter -> doha -> next/prev).

## 5) Suggested Build Order

1. Module A (contract)
2. Module B (APIs)
3. Module E (frontend wiring)
4. Module C (moderation metadata)
5. Module D (dashboard API completion)
6. Module F (OAuth UX)
7. Module G (tests and CI)

## 6) Definition of Done for Sequenced Reading

For a chapter-linked doha item, the system is complete when:
1. API returns current + previous + next nodes deterministically.
2. Frontend displays adjacent verse links/buttons.
3. Sequence reflects number_in_chapter consistently.
4. Edge cases are handled (first/last/missing nodes).
5. Tests prove this behavior on both SQLite test env and MySQL runtime env.
