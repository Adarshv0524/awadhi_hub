# Awadhi Corpus Backend API Reference (OpenAPI Generated)

Audit note (March 31, 2026): this file is generated from OpenAPI and includes broad static usage references. For content delivery architecture work, use the curated contract section below as the source of truth.

This document is auto-generated from backend OpenAPI (`app.openapi()`).
Do not hand-edit this file. Run `python backend/scripts/generate_api_reference.py`.

- OpenAPI version: `3.1.0`
- App version: `0.1.0`
- Total paths: `95`

- Total operations: `101`
- Deprecated operations: `3`

## Curated Content Delivery Contracts

This section is hand-maintained for the hierarchical text-delivery architecture and takes precedence for implementation decisions in this project.

### Hierarchy Browse

1. GET /authors
2. GET /authors/{author_slug}
3. GET /authors/{author_slug}/works
4. GET /authors/{author_slug}/works/{work_slug}/chapters

Minimum chapter payload contract:

1. id
2. slug
3. title
4. number
5. poetry_nodes_count

### Polymorphic Poetry Delivery

1. GET /api/v1/poetry/chapters/{chapter_id}/stream
Returns: hierarchy, total, offset, limit, items[]

2. GET /api/v1/poetry/chapters/{chapter_id}/nav?sequence_no={n}
Returns: hierarchy, current, previous, next

3. GET /api/v1/poetry/{poetry_node_id}
Returns: hierarchy, current, previous, next for detail page

4. GET /api/v1/poetry/search
Returns: chapter_path and hierarchy_path for deep links

### Legacy Doha Compatibility

1. GET /content/chapters/{chapter_id}/dohas
2. GET /content/doha/{id}/navigation

These remain active compatibility endpoints and should be treated as legacy layer contracts until canonical consolidation is completed.

## `/api/v1/admin/analytics/insights`

### `GET /api/v1/admin/analytics/insights`

- Summary: Admin Analytics Insights
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| view | query | yes | string | One of: summary, top, growth, demand, engagement-summary, action-throughput, moderation-cycle-time, rbac-denials, moderation-kpi, events, actor-resource-graph, latency-error-surface |
| content_type | query | no | anyOf |  |
| limit | query | no | integer |  |
| start_date | query | no | anyOf |  |
| end_date | query | no | anyOf |  |
| module | query | no | anyOf |  |
| action | query | no | anyOf |  |
| result | query | no | anyOf |  |
| bucket_minutes | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsInsightsOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/analytics/summary`

### `GET /api/v1/admin/analytics/summary`

- Summary: Admin Analytics Summary
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


## `/api/v1/admin/audit_logs`

### `GET /api/v1/admin/audit_logs`

- Summary: List Audit Logs
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-audit`

**System Context**
Administrative audit trail retrieval APIs. Used by frontend admin audit page and incident analysis workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| action | query | no | anyOf |  |
| resource_type | query | no | anyOf |  |
| actor_user_id | query | no | anyOf |  |
| start | query | no | anyOf |  |
| end | query | no | anyOf |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AuditLogListOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/audit_logs/{id}`

### `GET /api/v1/admin/audit_logs/{id}`

- Summary: Get Audit Log
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-audit`

**System Context**
Administrative audit trail retrieval APIs. Used by frontend admin audit page and incident analysis workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AuditLogOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/hierarchy/authors`

### `POST /api/v1/admin/hierarchy/authors`

- Summary: Create Author
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-hierarchy`

**System Context**
Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `AuthorCreateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/hierarchy/authors/{author_id}`

### `PATCH /api/v1/admin/hierarchy/authors/{author_id}`

- Summary: Update Author
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-hierarchy`

**System Context**
Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_id | path | yes | integer |  |

**Request Body**
- `application/json`: `AuthorUpdateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/hierarchy/authors/{author_id}/works`

### `POST /api/v1/admin/hierarchy/authors/{author_id}/works`

- Summary: Create Work
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-hierarchy`

**System Context**
Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_id | path | yes | integer |  |

**Request Body**
- `application/json`: `WorkCreateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/hierarchy/chapters/{chapter_id}`

### `PATCH /api/v1/admin/hierarchy/chapters/{chapter_id}`

- Summary: Update Chapter
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-hierarchy`

**System Context**
Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| chapter_id | path | yes | integer |  |

**Request Body**
- `application/json`: `ChapterUpdateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/hierarchy/works/{work_id}`

### `PATCH /api/v1/admin/hierarchy/works/{work_id}`

- Summary: Update Work
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-hierarchy`

**System Context**
Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| work_id | path | yes | integer |  |

**Request Body**
- `application/json`: `WorkUpdateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/hierarchy/works/{work_id}/chapters`

### `POST /api/v1/admin/hierarchy/works/{work_id}/chapters`

- Summary: Create Chapter
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-hierarchy`

**System Context**
Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| work_id | path | yes | integer |  |

**Request Body**
- `application/json`: `ChapterCreateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/system_settings`

### `GET /api/v1/admin/system_settings`

- Summary: List Settings
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-system-settings`

**System Context**
System configuration APIs for runtime settings, feature flags, and rate-limit controls. Used by frontend admin settings page.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |


## `/api/v1/admin/system_settings/import`

### `POST /api/v1/admin/system_settings/import`

- Summary: Import Settings
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-system-settings`

**System Context**
System configuration APIs for runtime settings, feature flags, and rate-limit controls. Used by frontend admin settings page.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `BulkImportIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/system_settings/{key}`

### `GET /api/v1/admin/system_settings/{key}`

- Summary: Get Setting Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-system-settings`

**System Context**
System configuration APIs for runtime settings, feature flags, and rate-limit controls. Used by frontend admin settings page.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| key | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | SettingOut |
| 422 | Validation Error | HTTPValidationError |

### `PUT /api/v1/admin/system_settings/{key}`

- Summary: Upsert Setting
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-system-settings`

**System Context**
System configuration APIs for runtime settings, feature flags, and rate-limit controls. Used by frontend admin settings page.

**Semantic Description**
Accept JSON body with format: {"value": <actual_value>}
Extracts the "value" field and stores it as the setting value.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| key | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | SettingOut |
| 422 | Validation Error | HTTPValidationError |

### `DELETE /api/v1/admin/system_settings/{key}`

- Summary: Delete Setting Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-system-settings`

**System Context**
System configuration APIs for runtime settings, feature flags, and rate-limit controls. Used by frontend admin settings page.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| key | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 204 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/users`

### `GET /api/v1/admin/users`

- Summary: List Users
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-users`

**System Context**
Admin user management for listing users and updating roles/permissions/account state. Used by frontend admin users dashboard.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| offset | query | no | integer |  |
| limit | query | no | integer |  |
| q | query | no | string | Search by user id, username, or email |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |

### `POST /api/v1/admin/users`

- Summary: Create User Admin
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-users`

**System Context**
Admin user management for listing users and updating roles/permissions/account state. Used by frontend admin users dashboard.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `UserCreateAdminIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/users/{user_id}`

### `GET /api/v1/admin/users/{user_id}`

- Summary: Get User Admin
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-users`

**System Context**
Admin user management for listing users and updating roles/permissions/account state. Used by frontend admin users dashboard.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| user_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserOut |
| 422 | Validation Error | HTTPValidationError |

### `PATCH /api/v1/admin/users/{user_id}`

- Summary: Update User Admin
- Deprecation Status: Active
- Migration Targets: -
- Tags: `admin-users`

**System Context**
Admin user management for listing users and updating roles/permissions/account state. Used by frontend admin users dashboard.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| user_id | path | yes | integer |  |

**Request Body**
- `application/json`: `UserUpdateAdminIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/ai/model-decision`

### `POST /api/v1/ai/model-decision`

- Summary: Model Decision
- Deprecation Status: Active
- Migration Targets: -
- Tags: `ai-ops`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ModelDecisionIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/ai/moderation-triage`

### `GET /api/v1/ai/moderation-triage`

- Summary: Moderation Triage
- Deprecation Status: Active
- Migration Targets: -
- Tags: `ai-ops`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/ai/settings-risk-score`

### `POST /api/v1/ai/settings-risk-score`

- Summary: Settings Risk Score
- Deprecation Status: Active
- Migration Targets: -
- Tags: `ai-ops`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `SettingsRiskIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/analytics/leaderboard`

### `GET /api/v1/analytics/leaderboard`

- Summary: Get Public Leaderboard
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics-live`

**System Context**
Public real-time leaderboard and analytics streaming APIs for live ranking views.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | LeaderboardOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/analytics/summary`

### `GET /api/v1/analytics/summary`

- Summary: Analytics Summary
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


## `/api/v1/articles`

### `GET /api/v1/articles`

- Summary: List Articles
- Deprecation Status: Active
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
List articles with optional search and filtering.
- Public visibility only
- Ordered by configured sort/order (default newest first)
- Tracks search hits in engagement KPIs when q is provided

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf | Search query for title or body |
| tag | query | no | anyOf | Filter by tag |
| sort | query | no | string |  |
| order | query | no | string |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/articles/by-tag/{tag}`

### `GET /api/v1/articles/by-tag/{tag}`

- Summary: Get Articles By Tag
- Deprecation Status: Active
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get all articles with a specific tag.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| tag | path | yes | string |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/articles/recent/list`

### `GET /api/v1/articles/recent/list`

- Summary: Get Recent Articles
- Deprecation Status: Deprecated
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get recently published articles.

**Pragmatic Integration Notes**
Deprecated: migration target not explicitly mapped; verify with owning module before integrating.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| days | query | no | integer | Number of days to look back |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/articles/search/advanced`

### `GET /api/v1/articles/search/advanced`

- Summary: Advanced Search Articles
- Deprecation Status: Deprecated
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Advanced search with multiple filters.

**Pragmatic Integration Notes**
Deprecated: migration target not explicitly mapped; verify with owning module before integrating.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| title | query | no | anyOf |  |
| body | query | no | anyOf |  |
| tag | query | no | anyOf |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/articles/stats`

### `GET /api/v1/articles/stats`

- Summary: Get Article Stats
- Deprecation Status: Active
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get statistics about articles.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ArticleStatsOut |


## `/api/v1/articles/tags/list`

### `GET /api/v1/articles/tags/list`

- Summary: List All Tags
- Deprecation Status: Deprecated
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get a list of all unique tags used in articles.

**Pragmatic Integration Notes**
Deprecated: migration target not explicitly mapped; verify with owning module before integrating.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |


## `/api/v1/articles/{article_id}`

### `GET /api/v1/articles/{article_id}`

- Summary: Get Article
- Deprecation Status: Active
- Migration Targets: -
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get detailed information about a specific article.
Increments view count in engagement KPIs.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| article_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/forgot-password`

### `POST /api/v1/auth/forgot-password`

- Summary: Forgot Password
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ForgotPasswordIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/login`

### `POST /api/v1/auth/login`

- Summary: Login
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `LoginIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/logout`

### `POST /api/v1/auth/logout`

- Summary: Logout
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `LogoutIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/me`

### `GET /api/v1/auth/me`

- Summary: Me
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |


## `/api/v1/auth/oauth/google/callback`

### `GET /api/v1/auth/oauth/google/callback`

- Summary: Google Callback
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| code | query | no | anyOf |  |
| state | query | no | anyOf |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/oauth/google/login`

### `GET /api/v1/auth/oauth/google/login`

- Summary: Google Login
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| next | query | no | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/refresh`

### `POST /api/v1/auth/refresh`

- Summary: Refresh Token
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RefreshIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/register`

### `POST /api/v1/auth/register`

- Summary: Register
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RegisterIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/resend-email-otp`

### `POST /api/v1/auth/resend-email-otp`

- Summary: Resend Email Otp
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ResendEmailOtpIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/reset-password`

### `POST /api/v1/auth/reset-password`

- Summary: Reset Password
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ResetPasswordIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/auth/verify-email`

### `POST /api/v1/auth/verify-email`

- Summary: Verify Email
- Deprecation Status: Active
- Migration Targets: -
- Tags: `auth`

**System Context**
Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Used in login/session lifecycle; failures directly impact route guards.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `VerifyEmailOtpIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | VerifyEmailOtpOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/authors`

### `GET /api/v1/authors`

- Summary: List Authors
- Deprecation Status: Active
- Migration Targets: -
- Tags: `authors`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Public: list authors, with optional search and language filter.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf | Search in author name |
| language | query | no | anyOf |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/authors/works/search`

### `GET /api/v1/authors/works/search`

- Summary: Search Works
- Deprecation Status: Active
- Migration Targets: -
- Tags: `authors`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Public: search works globally by work title and optionally author name.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf | Search in work title or author name |
| work_type | query | no | anyOf |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/authors/{author_slug}`

### `GET /api/v1/authors/{author_slug}`

- Summary: Get Author
- Deprecation Status: Active
- Migration Targets: -
- Tags: `authors`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Public: details of a single author by slug.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_slug | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AuthorDetailOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/authors/{author_slug}/works`

### `GET /api/v1/authors/{author_slug}/works`

- Summary: List Works For Author
- Deprecation Status: Active
- Migration Targets: -
- Tags: `authors`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Public: list works for an author.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_slug | path | yes | string |  |
| work_type | query | no | anyOf |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/authors/{author_slug}/works/{work_slug}`

### `GET /api/v1/authors/{author_slug}/works/{work_slug}`

- Summary: Get Work
- Deprecation Status: Active
- Migration Targets: -
- Tags: `authors`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Public: details of a single work under an author.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_slug | path | yes | string |  |
| work_slug | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | WorkDetailOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/authors/{author_slug}/works/{work_slug}/chapters`

### `GET /api/v1/authors/{author_slug}/works/{work_slug}/chapters`

- Summary: List Chapters
- Deprecation Status: Active
- Migration Targets: -
- Tags: `authors`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Public: list chapters for a given work.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_slug | path | yes | string |  |
| work_slug | path | yes | string |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/article/{entry_id}/navigation`

### `GET /api/v1/content/article/{entry_id}/navigation`

- Summary: Get Article Navigation Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| entry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ContentNavigationOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/by-path/{author_slug}/{work_slug}/{chapter_slug}/poetry`

### `GET /api/v1/content/by-path/{author_slug}/{work_slug}/{chapter_slug}/poetry`

- Summary: List Chapter Poetry By Path
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| author_slug | path | yes | string |  |
| work_slug | path | yes | string |  |
| chapter_slug | path | yes | string |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ChapterDohasOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/chapters/{chapter_id}/poetry`

### `GET /api/v1/content/chapters/{chapter_id}/poetry`

- Summary: List Chapter Poetry
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| chapter_id | path | yes | integer |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ChapterDohasOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/dictionary/{entry_id}/navigation`

### `GET /api/v1/content/dictionary/{entry_id}/navigation`

- Summary: Get Dictionary Navigation Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| entry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ContentNavigationOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/idiom/{entry_id}/navigation`

### `GET /api/v1/content/idiom/{entry_id}/navigation`

- Summary: Get Idiom Navigation Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| entry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ContentNavigationOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/poetry`

### `GET /api/v1/content/poetry`

- Summary: List Poetry
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
List canonical poetry entries from the legacy canonical table.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| offset | query | no | integer |  |
| limit | query | no | integer |  |
| visibility | query | no | anyOf |  |
| sort | query | no | string |  |
| order | query | no | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/poetry/by-path/{hierarchy_path}`

### `GET /api/v1/content/poetry/by-path/{hierarchy_path}`

- Summary: Get Poetry By Path
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| hierarchy_path | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | DohaOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/poetry/{poetry_id}`

### `GET /api/v1/content/poetry/{poetry_id}`

- Summary: Get Poetry
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| poetry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | DohaOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/poetry/{poetry_id}/history`

### `GET /api/v1/content/poetry/{poetry_id}/history`

- Summary: Get Poetry History
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| poetry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/poetry/{poetry_id}/navigation`

### `GET /api/v1/content/poetry/{poetry_id}/navigation`

- Summary: Get Poetry Navigation Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
Return previous/current/next poetry cards based on chapter sequence.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| poetry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ContentNavigationOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/dictionary`

### `GET /api/v1/dictionary`

- Summary: Search Dictionary
- Deprecation Status: Active
- Migration Targets: -
- Tags: `dictionary`

**System Context**
Dictionary canonical content APIs used by dictionary listing/detail and contributor workflows.

**Semantic Description**
Search or list dictionary entries.
- If q is provided: search by lemma (devanagari or roman)
- If q is None: list all public entries (paginated)

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf |  |
| sort | query | no | string |  |
| order | query | no | string |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/dictionary/{entry_id}`

### `GET /api/v1/dictionary/{entry_id}`

- Summary: Get Dictionary Entry
- Deprecation Status: Active
- Migration Targets: -
- Tags: `dictionary`

**System Context**
Dictionary canonical content APIs used by dictionary listing/detail and contributor workflows.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| entry_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | DictionaryDetailOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/governance/checklist`

### `GET /api/v1/governance/checklist`

- Summary: Governance Checklist
- Deprecation Status: Active
- Migration Targets: -
- Tags: `governance`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |


## `/api/v1/governance/export/audit`

### `GET /api/v1/governance/export/audit`

- Summary: Export Audit Minimized
- Deprecation Status: Active
- Migration Targets: -
- Tags: `governance`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/governance/export/telemetry`

### `GET /api/v1/governance/export/telemetry`

- Summary: Export Telemetry Minimized
- Deprecation Status: Active
- Migration Targets: -
- Tags: `governance`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/governance/retention/run`

### `POST /api/v1/governance/retention/run`

- Summary: Execute Retention
- Deprecation Status: Active
- Migration Targets: -
- Tags: `governance`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |


## `/api/v1/idioms`

### `GET /api/v1/idioms`

- Summary: Search Idioms
- Deprecation Status: Active
- Migration Targets: -
- Tags: `idioms`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Search or list idiom entries.
- If q is provided: search by text (devanagari or roman)
- If q is None: list all public entries (paginated)

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf |  |
| sort | query | no | string |  |
| order | query | no | string |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/idioms/{idiom_id}`

### `GET /api/v1/idioms/{idiom_id}`

- Summary: Get Idiom
- Deprecation Status: Active
- Migration Targets: -
- Tags: `idioms`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| idiom_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | IdiomOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/interactions/master`

### `POST /api/v1/interactions/master`

- Summary: Api Interaction Master
- Deprecation Status: Active
- Migration Targets: -
- Tags: `interactions`

**System Context**
Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `MasterInteractionIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/interactions/report`

### `POST /api/v1/interactions/report`

- Summary: Api Create Report
- Deprecation Status: Active
- Migration Targets: -
- Tags: `interactions`

**System Context**
Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ReportIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/interactions/share`

### `POST /api/v1/interactions/share`

- Summary: Api Record Share
- Deprecation Status: Active
- Migration Targets: -
- Tags: `interactions`

**System Context**
Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ShareIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/interactions/toggle`

### `POST /api/v1/interactions/toggle`

- Summary: Api Toggle Interaction
- Deprecation Status: Active
- Migration Targets: -
- Tags: `interactions`

**System Context**
Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ToggleIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/interactions/users/{user_id}/bookmarks`

### `GET /api/v1/interactions/users/{user_id}/bookmarks`

- Summary: Api List User Bookmarks
- Deprecation Status: Active
- Migration Targets: -
- Tags: `interactions`

**System Context**
Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| user_id | path | yes | integer |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserBookmarksListOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/interactions/users/{user_id}/likes`

### `GET /api/v1/interactions/users/{user_id}/likes`

- Summary: Api List User Likes
- Deprecation Status: Active
- Migration Targets: -
- Tags: `interactions`

**System Context**
Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| user_id | path | yes | integer |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserLikesListOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/moderation/batch`

### `POST /api/v1/moderation/batch`

- Summary: Batch Moderate
- Deprecation Status: Active
- Migration Targets: -
- Tags: `moderation`

**System Context**
Moderation queue and decision APIs for approve/reject workflows and batch moderation.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires moderator or higher role for write actions.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ModerationBatchIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/moderation/batch_approve`

### `POST /api/v1/moderation/batch_approve`

- Summary: Batch Approve
- Deprecation Status: Active
- Migration Targets: -
- Tags: `moderation`

**System Context**
Moderation queue and decision APIs for approve/reject workflows and batch moderation.

**Semantic Description**
Batch approve submissions (Admin only).
Returns batch_id, created canonical content, skipped submissions, and any errors.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires moderator or higher role for write actions.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `BatchApproveIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | BatchApproveOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/moderation/submissions`

### `GET /api/v1/moderation/submissions`

- Summary: List Pending Submissions
- Deprecation Status: Active
- Migration Targets: -
- Tags: `moderation`

**System Context**
Moderation queue and decision APIs for approve/reject workflows and batch moderation.

**Semantic Description**
List moderation queue.
- Only moderators/admins can see this.
- Default: all pending_review submissions (regardless of assignment).
- If `assigned_to_me=true` -> only those assigned to current_user.
- If `unassigned_only=true` -> only those with assigned_moderator_id = NULL.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires moderator or higher role for write actions.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| assigned_to_me | query | no | boolean | If true, only show submissions assigned to me |
| unassigned_only | query | no | boolean | If true, only show unassigned submissions |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/moderation/submissions/{submission_id}`

### `GET /api/v1/moderation/submissions/{submission_id}`

- Summary: Get Submission For Moderation
- Deprecation Status: Active
- Migration Targets: -
- Tags: `moderation`

**System Context**
Moderation queue and decision APIs for approve/reject workflows and batch moderation.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires moderator or higher role for write actions.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| submission_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ModerationSubmissionOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/moderation/submissions/{submission_id}/approve`

### `POST /api/v1/moderation/submissions/{submission_id}/approve`

- Summary: Approve Submission
- Deprecation Status: Active
- Migration Targets: -
- Tags: `moderation`

**System Context**
Moderation queue and decision APIs for approve/reject workflows and batch moderation.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires moderator or higher role for write actions.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| submission_id | path | yes | integer |  |

**Request Body**
- `application/json`: `ModerationActionIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ModerationSubmissionOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/moderation/submissions/{submission_id}/reject`

### `POST /api/v1/moderation/submissions/{submission_id}/reject`

- Summary: Reject Submission
- Deprecation Status: Active
- Migration Targets: -
- Tags: `moderation`

**System Context**
Moderation queue and decision APIs for approve/reject workflows and batch moderation.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires moderator or higher role for write actions.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| submission_id | path | yes | integer |  |

**Request Body**
- `application/json`: `ModerationActionIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ModerationSubmissionOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/poetry/chapters/{chapter_id}/nav`

### `GET /api/v1/poetry/chapters/{chapter_id}/nav`

- Summary: Poetry Nav Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `poetry`

**System Context**
Poetry node and chapter rendering APIs used by poetry readers and hybrid content rendering.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| chapter_id | path | yes | integer |  |
| sequence_no | query | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | PoetryNavContractOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/poetry/chapters/{chapter_id}/stream`

### `GET /api/v1/poetry/chapters/{chapter_id}/stream`

- Summary: Poetry Stream Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `poetry`

**System Context**
Poetry node and chapter rendering APIs used by poetry readers and hybrid content rendering.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| chapter_id | path | yes | integer |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | PoetryStreamOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/poetry/search`

### `GET /api/v1/poetry/search`

- Summary: Poetry Search Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `poetry`

**System Context**
Poetry node and chapter rendering APIs used by poetry readers and hybrid content rendering.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf |  |
| author | query | no | anyOf |  |
| work | query | no | anyOf |  |
| chapter | query | no | anyOf |  |
| poetry_type | query | no | anyOf |  |
| sort | query | no | string |  |
| limit | query | no | integer |  |
| offset | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | PoetrySearchOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/poetry/types`

### `GET /api/v1/poetry/types`

- Summary: Poetry Types Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `poetry`

**System Context**
Poetry node and chapter rendering APIs used by poetry readers and hybrid content rendering.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |


## `/api/v1/poetry/{poetry_node_id}`

### `GET /api/v1/poetry/{poetry_node_id}`

- Summary: Poetry Node Detail Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `poetry`

**System Context**
Poetry node and chapter rendering APIs used by poetry readers and hybrid content rendering.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| poetry_node_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | PoetryNavContractOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/recommendations/{content_type}/{content_id}`

### `GET /api/v1/recommendations/{content_type}/{content_id}`

- Summary: Recommend
- Deprecation Status: Active
- Migration Targets: -
- Tags: `recommendations`

**System Context**
Recommendation APIs used by suggestion panels and personalization experiments.

**Semantic Description**
Get related content recommendations.
- Pure read
- Preview objects
- Empty list if none found

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| content_type | path | yes | string |  |
| content_id | path | yes | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/search`

### `GET /api/v1/search`

- Summary: Search Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `search`

**System Context**
Search APIs used by global search interfaces and discovery pages.

**Semantic Description**
Search poetry content. Doha is treated as a poetry_type.
Falls back to legacy doha search when poetry index has no match.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf | Search query |
| author | query | no | anyOf | Author slug |
| work | query | no | anyOf | Work slug |
| chapter | query | no | anyOf | Chapter slug |
| poetry_type | query | no | anyOf | Poetry form slug, e.g. doha |
| type | query | no | anyOf | Legacy alias for poetry_type |
| sort | query | no | string | Sort by 'relevance' or 'recent' |
| limit | query | no | integer |  |
| offset | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/submissions`

### `POST /api/v1/submissions`

- Summary: Create Submission
- Deprecation Status: Active
- Migration Targets: -
- Tags: `submissions`

**System Context**
Contributor submission lifecycle APIs: create, update, submit for review, and retrieve user submissions.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `SubmissionCreateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | SubmissionOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/submissions/me`

### `GET /api/v1/submissions/me`

- Summary: List My Submissions
- Deprecation Status: Active
- Migration Targets: -
- Tags: `submissions`

**System Context**
Contributor submission lifecycle APIs: create, update, submit for review, and retrieve user submissions.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| status | query | no | anyOf |  |
| content_type | query | no | anyOf |  |
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/submissions/{submission_id}`

### `GET /api/v1/submissions/{submission_id}`

- Summary: Get Submission
- Deprecation Status: Active
- Migration Targets: -
- Tags: `submissions`

**System Context**
Contributor submission lifecycle APIs: create, update, submit for review, and retrieve user submissions.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| submission_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | SubmissionDetailOut |
| 422 | Validation Error | HTTPValidationError |

### `PUT /api/v1/submissions/{submission_id}`

- Summary: Update Submission
- Deprecation Status: Active
- Migration Targets: -
- Tags: `submissions`

**System Context**
Contributor submission lifecycle APIs: create, update, submit for review, and retrieve user submissions.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| submission_id | path | yes | integer |  |

**Request Body**
- `application/json`: `SubmissionUpdateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | SubmissionDetailOut |
| 422 | Validation Error | HTTPValidationError |

### `DELETE /api/v1/submissions/{submission_id}`

- Summary: Delete Submission
- Deprecation Status: Active
- Migration Targets: -
- Tags: `submissions`

**System Context**
Contributor submission lifecycle APIs: create, update, submit for review, and retrieve user submissions.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| submission_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/telemetry/admin-analytics-cutover`

### `POST /api/v1/telemetry/admin-analytics-cutover`

- Summary: Admin Analytics Cutover Event
- Deprecation Status: Active
- Migration Targets: -
- Tags: `telemetry`

**System Context**
Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `AdminAnalyticsCutoverEventIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 202 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/telemetry/admin-events`

### `POST /api/v1/telemetry/admin-events`

- Summary: Ingest Admin Event
- Deprecation Status: Active
- Migration Targets: -
- Tags: `telemetry`

**System Context**
Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `AdminTelemetryEventIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 202 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/telemetry/admin-observability/completeness`

### `GET /api/v1/telemetry/admin-observability/completeness`

- Summary: Admin Observability Completeness
- Deprecation Status: Active
- Migration Targets: -
- Tags: `telemetry`

**System Context**
Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| window_minutes | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/telemetry/admin-observability/slo`

### `GET /api/v1/telemetry/admin-observability/slo`

- Summary: Admin Observability Slo
- Deprecation Status: Active
- Migration Targets: -
- Tags: `telemetry`

**System Context**
Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| window_minutes | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/telemetry/auth-policy`

### `POST /api/v1/telemetry/auth-policy`

- Summary: Auth Policy Event
- Deprecation Status: Active
- Migration Targets: -
- Tags: `telemetry`

**System Context**
Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `AuthPolicyEventIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 202 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/telemetry/renderer-fallback`

### `POST /api/v1/telemetry/renderer-fallback`

- Summary: Renderer Fallback Event
- Deprecation Status: Active
- Migration Targets: -
- Tags: `telemetry`

**System Context**
Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RendererFallbackEventIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 202 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/users/id/{user_id}`

### `GET /api/v1/users/id/{user_id}`

- Summary: Get Public User By Id
- Deprecation Status: Active
- Migration Targets: -
- Tags: `users`

**System Context**
Public/user profile and contributor-focused user data APIs.

**Semantic Description**
Get public user info by numeric ID (for moderation contributor lookup).

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| user_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | PublicUserOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/users/me`

### `PATCH /api/v1/users/me`

- Summary: Update Own Profile
- Deprecation Status: Active
- Migration Targets: -
- Tags: `users`

**System Context**
Public/user profile and contributor-focused user data APIs.

**Semantic Description**
Allow authenticated users to update their own profile (username and email only).

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `UserProfileUpdateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserProfileUpdateOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/users/{username}`

### `GET /api/v1/users/{username}`

- Summary: Get Public User
- Deprecation Status: Active
- Migration Targets: -
- Tags: `users`

**System Context**
Public/user profile and contributor-focused user data APIs.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| username | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | PublicUserOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/users/{username}/stats`

### `GET /api/v1/users/{username}/stats`

- Summary: Get User Stats
- Deprecation Status: Active
- Migration Targets: -
- Tags: `users`

**System Context**
Public/user profile and contributor-focused user data APIs.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/AdminMissionControl.svelte`, `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionFormRedesigned.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_ai_ops_and_governance.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| username | path | yes | string |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserStatsOut |
| 422 | Validation Error | HTTPValidationError |


## `/health`

### `GET /health`

- Summary: Health
- Deprecation Status: Active
- Migration Targets: -
- Tags: -

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`
- Backend references: `backend/app/main.py`
- Test coverage refs: None found

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
