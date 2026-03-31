# Flutter Blueprint: Minimal but Complete Admin + Moderator App

## 1) Objective

Build a single Flutter app that can execute all admin and moderator capabilities exposed by the backend, with minimal architecture and no feature creep.

Primary goals:
- Full role-aware access to admin and moderator workflows.
- Stable API integration with explicit endpoint contracts.
- Small, maintainable codebase with fast implementation velocity.

Non-goals:
- Public content browsing app features.
- Experimental UX layers, plugin-heavy architecture, offline sync complexity.

---

## 2) Backend Architecture Audit (Admin/Moderator Focus)

## 2.1 Auth and RBAC

Role hierarchy (higher can do lower-role actions):
- guest
- registered
- moderator
- senior_moderator
- admin

Enforcement pattern:
- JWT bearer token -> `get_current_user` dependency.
- RBAC gate -> `require_role(Role.X)`.
- Fine-grained permission bits/ABAC structures exist but are not primary gatekeepers in current admin/mod routes.

## 2.2 Router Mounting and Prefixes

Canonical app mounting includes `/api/v1` prefix on routers in main app.
Legacy unprefixed aliases are also mounted when `ENABLE_LEGACY_UNPREFIXED_ROUTES=true`.

Important nuance:
- Most routers define local prefixes like `/admin/...`, `/moderation`, `/analytics` and map cleanly to `/api/v1/...`.
- `ai_ops` and `telemetry` routers are internally declared with `/api/v1/...` prefixes, then mounted again under `/api/v1`, which can result in `/api/v1/api/v1/...` paths in strict canonical mode.
- In dev/non-prod, legacy aliasing may still expose expected `/api/v1/ai/*`, `/api/v1/governance/*`, `/api/v1/telemetry/*` routes.

Practical client strategy:
- Default to standard paths documented below.
- Add endpoint fallback resolver for AI/governance/telemetry groups if deployment uses strict canonical mount.

---

## 3) Complete Admin + Moderator Endpoint Inventory

All paths below are listed in their expected client-facing form.

## 3.1 Authentication + Session

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Used for:
- Login, token refresh, logout, role resolution.

## 3.2 Moderator Workflows

Moderation queue and actions:
- `GET /api/v1/moderation/submissions`
  - Query: `assigned_to_me`, `unassigned_only`, `offset`, `limit`
- `GET /api/v1/moderation/submissions/{submission_id}`
- `POST /api/v1/moderation/submissions/{submission_id}/approve`
- `POST /api/v1/moderation/submissions/{submission_id}/reject`
- `POST /api/v1/moderation/batch`
- `POST /api/v1/moderation/batch_approve`

Moderator analytics:
- `GET /api/v1/analytics/summary`

AI-assist and governance exports (moderator+):
- `GET /api/v1/ai/moderation-triage`
- `POST /api/v1/ai/model-decision`
- `GET /api/v1/governance/export/audit`
- `GET /api/v1/governance/export/telemetry`

## 3.3 Admin Workflows

User administration:
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/users/{user_id}`
- `POST /api/v1/admin/users`
- `PATCH /api/v1/admin/users/{user_id}`

System settings:
- `GET /api/v1/admin/system_settings`
- `GET /api/v1/admin/system_settings/{key}`
- `PUT /api/v1/admin/system_settings/{key}`
- `DELETE /api/v1/admin/system_settings/{key}`
- `POST /api/v1/admin/system_settings/import`

Audit logs:
- `GET /api/v1/admin/audit_logs`
- `GET /api/v1/admin/audit_logs/{id}`

Hierarchy management:
- `POST /api/v1/admin/hierarchy/authors`
- `PATCH /api/v1/admin/hierarchy/authors/{author_id}`
- `POST /api/v1/admin/hierarchy/authors/{author_id}/works`
- `PATCH /api/v1/admin/hierarchy/works/{work_id}`
- `POST /api/v1/admin/hierarchy/works/{work_id}/chapters`
- `PATCH /api/v1/admin/hierarchy/chapters/{chapter_id}`

Admin analytics:
- `GET /api/v1/admin/analytics/summary`
- `GET /api/v1/admin/analytics/v2/summary`
- `GET /api/v1/admin/analytics/v2/top`
- `GET /api/v1/admin/analytics/v2/growth`
- `GET /api/v1/admin/analytics/v2/demand`
- `GET /api/v1/admin/analytics/v2/action-throughput`
- `GET /api/v1/admin/analytics/v2/moderation-cycle-time`
- `GET /api/v1/admin/analytics/v2/rbac-denials`
- `GET /api/v1/admin/analytics/v2/moderation-kpi`
- `GET /api/v1/admin/analytics/v2/events`
- `GET /api/v1/admin/analytics/v2/3d/actor-resource-graph`
- `GET /api/v1/admin/analytics/v2/3d/latency-error-surface`

Admin telemetry / governance controls:
- `POST /api/v1/telemetry/admin-events`
- `GET /api/v1/telemetry/admin-observability/slo`
- `GET /api/v1/telemetry/admin-observability/completeness`
- `POST /api/v1/ai/settings-risk-score`
- `POST /api/v1/governance/retention/run`
- `GET /api/v1/governance/checklist`

---

## 4) Minimal Flutter App Architecture

Use one app, role-gated modules.

## 4.1 Tech Choices (Small + Functional)

Dependencies:
- `flutter_riverpod`: predictable state, low boilerplate.
- `dio`: robust HTTP, interceptors, retry hooks.
- `go_router`: simple role-based route guards.
- `shared_preferences` (or `flutter_secure_storage` for stricter security): token persistence.

Avoid in v1:
- Heavy clean-architecture layering with excessive abstractions.
- Multiple state managers.
- Code generation unless team already uses it.

## 4.2 Folder Layout

```text
lib/
  main.dart
  app.dart
  core/
    api/
      api_client.dart
      endpoint_resolver.dart
      api_error.dart
    auth/
      token_store.dart
      auth_controller.dart
      role_guard.dart
    routing/
      app_router.dart
    ui/
      app_scaffold.dart
  features/
    auth/
      login_page.dart
      auth_repository.dart
    moderator/
      queue_page.dart
      submission_detail_page.dart
      moderation_repository.dart
      moderation_models.dart
      triage_page.dart
    admin_users/
      users_page.dart
      user_edit_page.dart
      users_repository.dart
    admin_settings/
      settings_page.dart
      setting_edit_page.dart
      settings_import_page.dart
      settings_repository.dart
    admin_hierarchy/
      authors_page.dart
      works_page.dart
      chapters_page.dart
      hierarchy_repository.dart
    admin_audit/
      audit_list_page.dart
      audit_detail_page.dart
      audit_repository.dart
    admin_analytics/
      analytics_dashboard_page.dart
      analytics_repository.dart
    governance/
      governance_page.dart
      governance_repository.dart
```

## 4.3 State Model

Keep it simple:
- One repository per feature group.
- One page-level `StateNotifier`/`AsyncNotifier` per screen.
- No cross-feature event bus.

Shared providers:
- `authProvider`: current user + role.
- `apiClientProvider`: configured Dio with auth interceptor.
- `endpointResolverProvider`: resolves AI/governance/telemetry path fallback.

## 4.4 Routing and Access Control

Rules:
- Unauthenticated -> only login route.
- Role `moderator` and above -> moderation routes.
- Role `admin` -> admin routes in addition to moderator routes.

Route groups:
- `/login`
- `/moderator/queue`
- `/moderator/submission/:id`
- `/moderator/triage`
- `/admin/users`
- `/admin/settings`
- `/admin/hierarchy`
- `/admin/audit`
- `/admin/analytics`
- `/admin/governance`

## 4.5 API Layer Contract

`ApiClient` responsibilities:
- Inject bearer token.
- 401 handling: attempt refresh once, then logout.
- Parse server errors consistently.
- Include `X-Request-ID` for traceability.

`EndpointResolver` responsibilities:
- For normal groups, return fixed `/api/v1/*` path.
- For AI/governance/telemetry groups, allow fallback sequence:
  1. `/api/v1/...`
  2. `/api/v1/api/v1/...`

Cache successful resolved prefix per group to avoid repeated retries.

---

## 5) Screen Blueprint (Role-Capability Complete)

## 5.1 Moderator Screens

1. Queue Screen
- Lists pending submissions.
- Filters: assigned to me, unassigned only.
- Bulk selection for batch approve/reject.

2. Submission Review Screen
- Shows full submission details.
- Actions: approve, reject.
- Required fields: note, guideline version, approved_by_human.

3. AI Triage Screen
- Pull triage recommendations.
- Allow moderator to log model decision.

4. Moderator Snapshot
- Summary counters (`analytics/summary`).

## 5.2 Admin Screens

1. Users Management
- Search/list users.
- Create user.
- Update role, active/banned, permission fields.

2. System Settings
- List/edit single setting.
- Delete setting.
- Bulk import settings with dry-run + confirmation workflow.

3. Hierarchy Management
- Create/update authors.
- Create/update works.
- Create/update chapters.

4. Audit Logs
- List with filters.
- Drill into row details.
- Respect masked fields for non-admin role behavior if reused by moderator view.

5. Analytics Dashboard
- KPI summary + v2 charts/lists:
  - top, growth, demand
  - throughput, moderation cycle time
  - RBAC denials, events

6. Governance + Observability
- Checklist view.
- Retention run trigger.
- SLO and completeness stats.
- Optional event ingestion utility for admin events.

---

## 6) Data Contracts (Minimal Domain Models)

Define only models required by UI now:
- `CurrentUser`: id, email, username, role, permissions, permission_scopes.
- `AdminUser`: id, email, username, role, is_active, is_banned, created_at, permissions, permission_scopes.
- `ModerationSubmission`: fields from moderation list/detail response.
- `AuditLog`: id, action, resource_type, resource_id, before, after, metadata, created_at.
- `SettingItem`: key, value.
- `AnalyticsSummary`: today_approved, pending_review, total_approved.

Keep unknown payload fields in `Map<String, dynamic>` for advanced analytics/governance endpoints to avoid model bloat.

---

## 7) API Mapping by Feature (Implementation Checklist)

Authentication:
- login -> `POST /auth/login`
- refresh -> `POST /auth/refresh`
- me -> `GET /auth/me`
- logout -> `POST /auth/logout`

Moderator:
- queue list/detail -> `/moderation/submissions*`
- approve/reject -> `/moderation/submissions/{id}/approve|reject`
- batch -> `/moderation/batch`, `/moderation/batch_approve`
- summary -> `/analytics/summary`
- triage + decision -> `/ai/moderation-triage`, `/ai/model-decision`

Admin:
- users -> `/admin/users*`
- settings -> `/admin/system_settings*`
- hierarchy -> `/admin/hierarchy*`
- audit -> `/admin/audit_logs*`
- analytics -> `/admin/analytics/*`
- governance -> `/governance/checklist`, `/governance/retention/run`
- observability -> `/telemetry/admin-observability/*`, `/telemetry/admin-events`

All relative paths above assume base `/api/v1` (with resolver fallback for AI/governance/telemetry).

---

## 8) Contract Risks to Handle in Flutter

Known drift signals:
- Use `PATCH /admin/users/{id}` as canonical update route (not legacy split role/deactivate endpoints).
- Audit log payload shape may not match older frontend assumptions (prefer backend shape directly).
- Chapter field is `number` (not `order_num`).

Client safeguards:
- Parse unknown fields defensively.
- Feature-level integration tests against live OpenAPI contract.
- Keep endpoint paths centralized (single source in `endpoint_resolver.dart`).

---

## 9) Minimal Delivery Plan

Phase 1 (Foundation, 2-3 days):
- Auth, token refresh, role guard, shell navigation.

Phase 2 (Moderator core, 3-4 days):
- Queue list/detail, approve/reject, batch actions, summary.

Phase 3 (Admin core, 4-6 days):
- Users, settings (including import), hierarchy CRUD, audit list/detail.

Phase 4 (Observability + Governance, 2-3 days):
- Admin analytics v2, SLO/completeness, governance checklist/retention.

Done criteria:
- Every endpoint group in sections 3.2 and 3.3 reachable from role-appropriate UI.
- 401 refresh flow works globally.
- No duplicated architecture layers.
