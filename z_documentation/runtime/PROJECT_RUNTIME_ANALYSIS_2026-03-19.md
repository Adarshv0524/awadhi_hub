# Project Runtime Analysis (2026-03-19)

## Scope Completed
- Backend started and reachable on port 8000.
- Frontend started and reachable on port 4321.
- OpenAPI contract fetched and all discovered backend operations exercised via curl.
- Additional authenticated curl checks executed with a newly created user account.

## Runtime Verification
- Backend health endpoint returned 200.
- Frontend root endpoint returned 200.
- Active listeners confirmed:
  - uvicorn on 0.0.0.0:8000
  - node (Astro dev) on 0.0.0.0:4321

## API Sweep Result Summary
- Total operations called: 67
- Status distribution after migration recovery:
  - 200: 15
  - 400: 2
  - 401: 37
  - 404: 11
  - 500: 2

## Authenticated API Check Summary
- Register: 200
- Login: 200
- Auth me: 200
- Refresh: 200
- Logout: 200
- Protected RBAC endpoints for admin/moderator returned 403 for registered user (expected).

## Critical Findings

### 1) ORM vs Migration Drift in submissions schema
- Runtime failure: Unknown column submissions.external_references.
- ORM expects external_references in submissions model.
- Migration created references instead.
- Evidence:
  - Model column: backend/app/db/models.py line with external_references.
  - Migration column: backend/alembic/versions/0004_create_submissions_table.py line with references.

### 2) ORM vs Migration Drift in system_settings schema
- Runtime failure: Unknown column system_settings.setting_key.
- ORM expects setting_key.
- Migration created key.
- Evidence:
  - Model column: backend/app/db/models.py line with setting_key.
  - Migration column: backend/alembic/versions/0010_system_settings.py line with key.

### 3) Migration chain fragility with long Alembic revision IDs
- Alembic upgrade failed because alembic_version.version_num was VARCHAR(32), too short for newer revision ID names.
- Manual DB fix applied during this run: widened to VARCHAR(255).

## Expected vs Unexpected API Responses
- Expected in this test setup:
  - 401 for endpoints requiring credentials when called anonymously.
  - 403 for admin/moderator endpoints when using registered-user token.
  - 404 for lookups by sample IDs/slugs with empty content tables.
  - 400 for OAuth callback without code parameter.
- Unexpected:
  - 500 on submissions and recommendations endpoints caused by schema drift above.

## Artifacts
- Full sweep report (TSV): z_documentation/runtime/api_sweep_after_migrate_report.tsv
- Full sweep report (JSON): z_documentation/runtime/api_sweep_after_migrate_report.json
- Authenticated checks: z_documentation/runtime/authenticated_api_checks.txt

## Notes About Line-by-Line Analysis Request
- The codebase surface analyzed includes 20,681 lines across backend app code, backend tests, and frontend source files.
- The highest-complexity files were identified and prioritized for inspection, including:
  - frontend/src/components/submission/SubmissionForm.svelte
  - backend/app/services/content_service.py
  - backend/app/db/models.py
  - backend/app/api/v1/article.py
  - backend/app/api/v1/submissions.py

## Recommended Fix Order
1. Resolve submissions schema drift (external_references vs references) with a forward migration or model alignment.
2. Resolve system_settings schema drift (setting_key vs key) with a forward migration or model alignment.
3. Add migration/test guardrails so ORM and Alembic schema stay synchronized.
4. Re-run full curl sweep and target zero 500 responses.
