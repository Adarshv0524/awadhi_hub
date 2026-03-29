# Awadhi Corpus Backend API Reference (OpenAPI Generated)

This document is auto-generated from backend OpenAPI (`app.openapi()`).
Do not hand-edit this file. Run `python backend/scripts/generate_api_reference.py`.

- OpenAPI version: `3.1.0`
- App version: `0.1.0`
- Total paths: `157`

- Total operations: `169`
- Deprecated operations: `6`
## `/admin/analytics/summary`

### `GET /admin/analytics/summary`

- Summary: Admin Analytics Summary
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/lib/analytics.ts`, `frontend/src/pages/admin/analytics.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/analytics.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_analytics_endpoints.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


## `/admin/analytics/v2/demand`

### `GET /admin/analytics/v2/demand`

- Summary: Admin Demand Distribution V2
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/lib/analytics.ts`, `frontend/src/pages/admin/analytics.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/analytics.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_analytics_endpoints.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | object |


## `/admin/analytics/v2/growth`

### `GET /admin/analytics/v2/growth`

- Summary: Admin Growth Trends V2
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/lib/analytics.ts`, `frontend/src/pages/admin/analytics.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/analytics.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_analytics_endpoints.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| start_date | query | no | anyOf |  |
| end_date | query | no | anyOf |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | GrowthSeries |
| 422 | Validation Error | HTTPValidationError |


## `/admin/analytics/v2/summary`

### `GET /admin/analytics/v2/summary`

- Summary: Admin Analytics Summary V2
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/lib/analytics.ts`, `frontend/src/pages/admin/analytics.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/analytics.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_analytics_endpoints.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


## `/admin/analytics/v2/top`

### `GET /admin/analytics/v2/top`

- Summary: Admin Top Content V2
- Deprecation Status: Active
- Migration Targets: -
- Tags: `analytics`

**System Context**
Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.

**Semantic Description**
No explicit description in OpenAPI.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations. Requires admin-level authorization in normal operation.

**Used In System**
- Frontend references: `frontend/src/lib/analytics.ts`, `frontend/src/pages/admin/analytics.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/analytics.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_analytics_endpoints.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| content_type | query | no | anyOf |  |
| limit | query | no | integer |  |
| start_date | query | no | anyOf |  |
| end_date | query | no | anyOf |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/admin/audit_logs`

### `GET /admin/audit_logs`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_audit.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_audit_logs.py`

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


## `/admin/audit_logs/{id}`

### `GET /admin/audit_logs/{id}`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_audit.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_audit_logs.py`

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


## `/admin/hierarchy/authors`

### `POST /admin/hierarchy/authors`

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
- Frontend references: `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/hierarchy.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_hierarchy.py`

**Parameters**
- None

**Request Body**
- `application/json`: `AuthorCreateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/admin/hierarchy/authors/{author_id}`

### `PATCH /admin/hierarchy/authors/{author_id}`

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
- Frontend references: `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/hierarchy.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_hierarchy.py`

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


## `/admin/hierarchy/authors/{author_id}/works`

### `POST /admin/hierarchy/authors/{author_id}/works`

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
- Frontend references: `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/hierarchy.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_hierarchy.py`

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


## `/admin/hierarchy/chapters/{chapter_id}`

### `PATCH /admin/hierarchy/chapters/{chapter_id}`

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
- Frontend references: `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/hierarchy.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_hierarchy.py`

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


## `/admin/hierarchy/works/{work_id}`

### `PATCH /admin/hierarchy/works/{work_id}`

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
- Frontend references: `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/hierarchy.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_hierarchy.py`

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


## `/admin/hierarchy/works/{work_id}/chapters`

### `POST /admin/hierarchy/works/{work_id}/chapters`

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
- Frontend references: `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/hierarchy.astro`, `frontend/src/pages/admin/index.astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_hierarchy.py`

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


## `/admin/system_settings`

### `GET /admin/system_settings`

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
- Frontend references: `frontend/src/components/admin/SettingsTable.svelte`, `frontend/src/components/admin/SystemInfo.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_settings.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_system_settings.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |


## `/admin/system_settings/import`

### `POST /admin/system_settings/import`

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
- Frontend references: `frontend/src/components/admin/SettingsTable.svelte`, `frontend/src/components/admin/SystemInfo.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_settings.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_system_settings.py`

**Parameters**
- None

**Request Body**
- `application/json`: `BulkImportIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/admin/system_settings/{key}`

### `GET /admin/system_settings/{key}`

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
- Frontend references: `frontend/src/components/admin/SettingsTable.svelte`, `frontend/src/components/admin/SystemInfo.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_settings.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_system_settings.py`

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

### `PUT /admin/system_settings/{key}`

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
- Frontend references: `frontend/src/components/admin/SettingsTable.svelte`, `frontend/src/components/admin/SystemInfo.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_settings.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_system_settings.py`

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

### `DELETE /admin/system_settings/{key}`

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
- Frontend references: `frontend/src/components/admin/SettingsTable.svelte`, `frontend/src/components/admin/SystemInfo.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_settings.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_system_settings.py`

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


## `/admin/users`

### `GET /admin/users`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/user/ProfileEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/index.astro`, `frontend/src/pages/admin/users.astro`
- Backend references: `backend/app/api/v1/admin_users.py`, `backend/app/core/security.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_auth_endpoints.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| offset | query | no | integer |  |
| limit | query | no | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |

### `POST /admin/users`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/user/ProfileEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/index.astro`, `frontend/src/pages/admin/users.astro`
- Backend references: `backend/app/api/v1/admin_users.py`, `backend/app/core/security.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- `application/json`: `UserCreateAdminIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | UserOut |
| 422 | Validation Error | HTTPValidationError |


## `/admin/users/{user_id}`

### `GET /admin/users/{user_id}`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/user/ProfileEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/index.astro`, `frontend/src/pages/admin/users.astro`
- Backend references: `backend/app/api/v1/admin_users.py`, `backend/app/core/security.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_auth_endpoints.py`

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

### `PATCH /admin/users/{user_id}`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/user/ProfileEditor.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`, `frontend/src/pages/admin/index.astro`, `frontend/src/pages/admin/users.astro`
- Backend references: `backend/app/api/v1/admin_users.py`, `backend/app/core/security.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_auth_endpoints.py`

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


## `/analytics/leaderboard`

### `GET /analytics/leaderboard`

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
- Frontend references: `frontend/src/components/leaderboard/LiveLeaderboard.svelte`
- Backend references: None found
- Test coverage refs: None found

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


## `/analytics/summary`

### `GET /analytics/summary`

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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: `backend/tests/test_analytics_endpoints.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


## `/api/v1/admin/analytics/v2/demand`

### `GET /api/v1/admin/analytics/v2/demand`

- Summary: Admin Demand Distribution V2
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | object |


## `/api/v1/admin/analytics/v2/growth`

### `GET /api/v1/admin/analytics/v2/growth`

- Summary: Admin Growth Trends V2
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| start_date | query | no | anyOf |  |
| end_date | query | no | anyOf |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | GrowthSeries |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/admin/analytics/v2/summary`

### `GET /api/v1/admin/analytics/v2/summary`

- Summary: Admin Analytics Summary V2
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | AnalyticsSummaryOut |


## `/api/v1/admin/analytics/v2/top`

### `GET /api/v1/admin/analytics/v2/top`

- Summary: Admin Top Content V2
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| content_type | query | no | anyOf |  |
| limit | query | no | integer |  |
| start_date | query | no | anyOf |  |
| end_date | query | no | anyOf |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| offset | query | no | integer |  |
| limit | query | no | integer |  |

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RegisterIn`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ResetPasswordIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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


## `/api/v1/content/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas`

### `GET /api/v1/content/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas`

- Summary: List Chapter Dohas By Path
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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


## `/api/v1/content/by-path/{hierarchy_path}`

### `GET /api/v1/content/by-path/{hierarchy_path}`

- Summary: Get Doha By Path
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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


## `/api/v1/content/chapters/{chapter_id}/dohas`

### `GET /api/v1/content/chapters/{chapter_id}/dohas`

- Summary: List Chapter Dohas
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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


## `/api/v1/content/doha`

### `GET /api/v1/content/doha`

- Summary: List Dohas
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
List canonical doha entries (for now mostly for debugging / browsing).

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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


## `/api/v1/content/doha/{doha_id}`

### `GET /api/v1/content/doha/{doha_id}`

- Summary: Get Doha
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| doha_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | DohaOut |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/doha/{doha_id}/history`

### `GET /api/v1/content/doha/{doha_id}/history`

- Summary: Get Doha History
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| doha_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/api/v1/content/doha/{doha_id}/navigation`

### `GET /api/v1/content/doha/{doha_id}/navigation`

- Summary: Get Doha Navigation Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
Return previous/current/next doha cards based on chapter sequence.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| doha_id | path | yes | integer |  |

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
Search canonical doha content.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf | Search query |
| author | query | no | anyOf | Author slug |
| work | query | no | anyOf | Work slug |
| chapter | query | no | anyOf | Chapter slug |
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `AdminTelemetryEventIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 202 | Successful Response | - |
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RendererFallbackEventIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 202 | Successful Response | - |
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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/content/poetry/PoetryChapterReader.svelte`, `frontend/src/components/content/poetry/PoetryDispatcher.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/observability.ts`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/[author]/[work]/[chapter].astro`
- Backend references: `backend/app/api/v1/__init__.py`, `backend/app/api/v1/admin_audit.py`, `backend/app/api/v1/admin_settings.py`, `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/article.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/content.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_api_v1_aliases.py`

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


## `/articles`

### `GET /articles`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/articles/ArticleDiscoverySidebar.svelte`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/navigation/NavigationControls.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/articles.astro`, `frontend/src/pages/articles/[id].astro`, `frontend/src/pages/articles/tag/[tag].astro`
- Backend references: `backend/app/api/v1/article.py`
- Test coverage refs: `backend/tests/test_dictionary_idiom_article.py`

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


## `/articles/by-tag/{tag}`

### `GET /articles/by-tag/{tag}`

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
- Frontend references: `frontend/src/pages/articles/tag/[tag].astro`
- Backend references: None found
- Test coverage refs: None found

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


## `/articles/recent/list`

### `GET /articles/recent/list`

- Summary: Get Recent Articles
- Deprecation Status: Deprecated
- Migration Targets: `GET /articles?sort=recent`
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get recently published articles.

**Pragmatic Integration Notes**
Deprecated: migrate clients to `GET /articles?sort=recent`.

**Used In System**
- Frontend references: `frontend/src/components/articles/ArticleDiscoverySidebar.svelte`
- Backend references: `backend/app/api/v1/article.py`
- Test coverage refs: None found

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


## `/articles/search/advanced`

### `GET /articles/search/advanced`

- Summary: Advanced Search Articles
- Deprecation Status: Deprecated
- Migration Targets: `GET /search`, `GET /articles`
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Advanced search with multiple filters.

**Pragmatic Integration Notes**
Deprecated: migrate clients to `GET /search`, `GET /articles`.

**Used In System**
- Frontend references: None found
- Backend references: `backend/app/api/v1/article.py`
- Test coverage refs: None found

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


## `/articles/stats`

### `GET /articles/stats`

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
- Frontend references: `frontend/src/components/articles/ArticleDiscoverySidebar.svelte`
- Backend references: None found
- Test coverage refs: None found

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ArticleStatsOut |


## `/articles/tags/list`

### `GET /articles/tags/list`

- Summary: List All Tags
- Deprecation Status: Deprecated
- Migration Targets: `GET /articles`
- Tags: `articles`

**System Context**
Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests.

**Semantic Description**
Get a list of all unique tags used in articles.

**Pragmatic Integration Notes**
Deprecated: migrate clients to `GET /articles`.

**Used In System**
- Frontend references: `frontend/src/components/articles/ArticleDiscoverySidebar.svelte`
- Backend references: `backend/app/api/v1/article.py`
- Test coverage refs: None found

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |


## `/articles/{article_id}`

### `GET /articles/{article_id}`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/articles/ArticleDiscoverySidebar.svelte`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/navigation/NavigationControls.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/articles.astro`, `frontend/src/pages/articles/[id].astro`, `frontend/src/pages/articles/tag/[tag].astro`
- Backend references: `backend/app/api/v1/article.py`
- Test coverage refs: `backend/tests/test_dictionary_idiom_article.py`

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


## `/auth/forgot-password`

### `POST /auth/forgot-password`

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
- Frontend references: `frontend/src/pages/forgot-password.astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ForgotPasswordIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/auth/login`

### `POST /auth/login`

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
- Frontend references: `frontend/src/lib/auth.ts`, `frontend/src/pages/login.astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_auth_endpoints.py`, `backend/tests/test_rate_limiter.py`

**Parameters**
- None

**Request Body**
- `application/json`: `LoginIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/auth/logout`

### `POST /auth/logout`

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
- Frontend references: `frontend/src/components/auth/AuthStatus.svelte`, `frontend/src/lib/auth.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- `application/json`: `LogoutIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/auth/me`

### `GET /auth/me`

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
- Frontend references: `frontend/src/components/auth/AuthGuard.astro`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/user/Dashboard.svelte`, `frontend/src/components/user/MySubmissions.svelte`, `frontend/src/components/user/ProfileEditor.svelte`, `frontend/src/lib/admin.ts`, `frontend/src/lib/auth.ts`, `frontend/src/pages/login.astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |


## `/auth/oauth/google/callback`

### `GET /auth/oauth/google/callback`

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
- Frontend references: `frontend/src/lib/googleAuth.ts`
- Backend references: `backend/app/core/settings.py`
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

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


## `/auth/oauth/google/login`

### `GET /auth/oauth/google/login`

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
- Frontend references: `frontend/src/lib/googleAuth.ts`
- Backend references: `backend/app/core/settings.py`
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

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


## `/auth/refresh`

### `POST /auth/refresh`

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
- Frontend references: `frontend/src/lib/api.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RefreshIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/auth/register`

### `POST /auth/register`

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
- Frontend references: `frontend/src/pages/register.astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- `application/json`: `RegisterIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/auth/reset-password`

### `POST /auth/reset-password`

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
- Frontend references: `frontend/src/pages/reset-password.astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_auth_endpoints.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ResetPasswordIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/authors`

### `GET /authors`

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
- Frontend references: `frontend/src/components/Header.astro`, `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/submission/SubmissionEditForm.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/admin.ts`, `frontend/src/lib/submissions.ts`, `frontend/src/pages/[...slug].astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`, `backend/app/api/v1/hierarchy_public.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_hierarchy.py`

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


## `/authors/{author_slug}`

### `GET /authors/{author_slug}`

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
- Frontend references: `frontend/src/components/Header.astro`, `frontend/src/components/admin/HierarchyEditor.svelte`, `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/submission/SubmissionEditForm.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/lib/admin.ts`, `frontend/src/lib/submissions.ts`, `frontend/src/pages/[...slug].astro`
- Backend references: `backend/app/api/v1/hierarchy_admin.py`, `backend/app/api/v1/hierarchy_public.py`
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_hierarchy.py`

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


## `/authors/{author_slug}/works`

### `GET /authors/{author_slug}/works`

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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`

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


## `/authors/{author_slug}/works/{work_slug}`

### `GET /authors/{author_slug}/works/{work_slug}`

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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`

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


## `/authors/{author_slug}/works/{work_slug}/chapters`

### `GET /authors/{author_slug}/works/{work_slug}/chapters`

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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_admin_payload_contract.py`

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


## `/content/article/{entry_id}/navigation`

### `GET /content/article/{entry_id}/navigation`

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
- Frontend references: `frontend/src/pages/articles/[id].astro`
- Backend references: None found
- Test coverage refs: None found

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


## `/content/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas`

### `GET /content/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas`

- Summary: List Chapter Dohas By Path
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
- Frontend references: `frontend/src/pages/[...slug].astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_canonical_doha.py`

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


## `/content/by-path/{hierarchy_path}`

### `GET /content/by-path/{hierarchy_path}`

- Summary: Get Doha By Path
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
- Frontend references: `frontend/src/pages/[...slug].astro`
- Backend references: None found
- Test coverage refs: `backend/tests/test_canonical_doha.py`

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


## `/content/chapters/{chapter_id}/dohas`

### `GET /content/chapters/{chapter_id}/dohas`

- Summary: List Chapter Dohas
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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: `backend/tests/e2e/test_user_journey.py`, `backend/tests/test_canonical_doha.py`

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


## `/content/dictionary/{entry_id}/navigation`

### `GET /content/dictionary/{entry_id}/navigation`

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
- Frontend references: `frontend/src/pages/dictionary/[id].astro`
- Backend references: None found
- Test coverage refs: None found

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


## `/content/doha`

### `GET /content/doha`

- Summary: List Dohas
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
List canonical doha entries (for now mostly for debugging / browsing).

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/content/ContentHistory.svelte`, `frontend/src/pages/doha.astro`, `frontend/src/pages/doha/[id].astro`, `frontend/src/pages/sitemap.xml.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/api/v1/test_content_navigation.py`, `backend/tests/e2e/test_user_journey.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`

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


## `/content/doha/{doha_id}`

### `GET /content/doha/{doha_id}`

- Summary: Get Doha
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
- Frontend references: `frontend/src/components/content/ContentHistory.svelte`, `frontend/src/pages/doha.astro`, `frontend/src/pages/doha/[id].astro`, `frontend/src/pages/sitemap.xml.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/api/v1/test_content_navigation.py`, `backend/tests/e2e/test_user_journey.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| doha_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | DohaOut |
| 422 | Validation Error | HTTPValidationError |


## `/content/doha/{doha_id}/history`

### `GET /content/doha/{doha_id}/history`

- Summary: Get Doha History
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
- Frontend references: `frontend/src/components/content/ContentHistory.svelte`, `frontend/src/pages/doha.astro`, `frontend/src/pages/doha/[id].astro`, `frontend/src/pages/sitemap.xml.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/api/v1/test_content_navigation.py`, `backend/tests/e2e/test_user_journey.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| doha_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | array |
| 422 | Validation Error | HTTPValidationError |


## `/content/doha/{doha_id}/navigation`

### `GET /content/doha/{doha_id}/navigation`

- Summary: Get Doha Navigation Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `content`

**System Context**
Canonical content retrieval APIs used by public pages and navigation workflows.

**Semantic Description**
Return previous/current/next doha cards based on chapter sequence.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/content/ContentHistory.svelte`, `frontend/src/pages/doha.astro`, `frontend/src/pages/doha/[id].astro`, `frontend/src/pages/sitemap.xml.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/api/v1/test_content_navigation.py`, `backend/tests/e2e/test_user_journey.py`, `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| doha_id | path | yes | integer |  |

**Request Body**
- None

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | ContentNavigationOut |
| 422 | Validation Error | HTTPValidationError |


## `/content/idiom/{entry_id}/navigation`

### `GET /content/idiom/{entry_id}/navigation`

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
- Frontend references: `frontend/src/pages/idioms/[id].astro`
- Backend references: None found
- Test coverage refs: None found

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


## `/dictionary`

### `GET /dictionary`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/navigation/NavigationControls.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/404.astro`, `frontend/src/pages/dictionary.astro`, `frontend/src/pages/dictionary/[id].astro`, `frontend/src/pages/index.astro`
- Backend references: `backend/app/api/v1/content.py`, `backend/app/api/v1/dictionary.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_dictionary_idiom_article.py`

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


## `/dictionary/{entry_id}`

### `GET /dictionary/{entry_id}`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/navigation/NavigationControls.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/404.astro`, `frontend/src/pages/dictionary.astro`, `frontend/src/pages/dictionary/[id].astro`, `frontend/src/pages/index.astro`
- Backend references: `backend/app/api/v1/content.py`, `backend/app/api/v1/dictionary.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_dictionary_idiom_article.py`

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


## `/idioms`

### `GET /idioms`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/navigation/NavigationControls.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/idioms.astro`, `frontend/src/pages/idioms/[id].astro`, `frontend/src/pages/index.astro`, `frontend/src/pages/robots.txt.ts`
- Backend references: `backend/app/api/v1/idiom.py`
- Test coverage refs: `backend/tests/test_dictionary_idiom_article.py`

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


## `/idioms/{idiom_id}`

### `GET /idioms/{idiom_id}`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/navigation/NavigationControls.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/idioms.astro`, `frontend/src/pages/idioms/[id].astro`, `frontend/src/pages/index.astro`, `frontend/src/pages/robots.txt.ts`
- Backend references: `backend/app/api/v1/idiom.py`
- Test coverage refs: `backend/tests/test_dictionary_idiom_article.py`

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


## `/interactions/report`

### `POST /interactions/report`

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
- Frontend references: `frontend/src/components/interaction/InteractionButtons.svelte`, `frontend/src/lib/interactions.ts`
- Backend references: None found
- Test coverage refs: None found

**Parameters**
- None

**Request Body**
- `application/json`: `ReportIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/interactions/share`

### `POST /interactions/share`

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
- Frontend references: `frontend/src/components/interaction/InteractionButtons.svelte`, `frontend/src/lib/interactions.ts`
- Backend references: None found
- Test coverage refs: None found

**Parameters**
- None

**Request Body**
- `application/json`: `ShareIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/interactions/toggle`

### `POST /interactions/toggle`

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
- Frontend references: `frontend/src/components/interaction/InteractionButtons.svelte`, `frontend/src/lib/interactions.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_interactions.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ToggleIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/interactions/users/{user_id}/bookmarks`

### `GET /interactions/users/{user_id}/bookmarks`

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
- Frontend references: `frontend/src/components/user/Dashboard.svelte`, `frontend/src/components/user/UserBookmarks.svelte`, `frontend/src/lib/interactions.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_interactions.py`

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


## `/interactions/users/{user_id}/likes`

### `GET /interactions/users/{user_id}/likes`

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
- Frontend references: `frontend/src/components/user/Dashboard.svelte`, `frontend/src/components/user/UserBookmarks.svelte`, `frontend/src/lib/interactions.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_interactions.py`

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


## `/moderation/batch`

### `POST /moderation/batch`

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
- Frontend references: `frontend/src/components/moderation/ModerationQueue.svelte`
- Backend references: None found
- Test coverage refs: `backend/tests/test_batch_moderation_atomic.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`

**Parameters**
- None

**Request Body**
- `application/json`: `ModerationBatchIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | - |
| 422 | Validation Error | HTTPValidationError |


## `/moderation/batch_approve`

### `POST /moderation/batch_approve`

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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: `backend/tests/test_batch_moderation_atomic.py`, `backend/tests/test_dictionary_idiom_article.py`

**Parameters**
- None

**Request Body**
- `application/json`: `BatchApproveIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | BatchApproveOut |
| 422 | Validation Error | HTTPValidationError |


## `/moderation/submissions`

### `GET /moderation/submissions`

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
- Frontend references: `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/lib/admin.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`

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


## `/moderation/submissions/{submission_id}`

### `GET /moderation/submissions/{submission_id}`

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
- Frontend references: `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/lib/admin.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`

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


## `/moderation/submissions/{submission_id}/approve`

### `POST /moderation/submissions/{submission_id}/approve`

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
- Frontend references: `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/lib/admin.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`

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


## `/moderation/submissions/{submission_id}/reject`

### `POST /moderation/submissions/{submission_id}/reject`

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
- Frontend references: `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/lib/admin.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`

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


## `/recommendations/{content_type}/{content_id}`

### `GET /recommendations/{content_type}/{content_id}`

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
- Frontend references: `frontend/src/components/Recommendations.astro`, `frontend/src/components/recommendations/Recommendations.svelte`, `frontend/src/pages/articles/[id].astro`, `frontend/src/pages/dictionary/[id].astro`, `frontend/src/pages/doha/[id].astro`, `frontend/src/pages/idioms/[id].astro`
- Backend references: `backend/app/api/v1/recommendations.py`
- Test coverage refs: None found

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


## `/search`

### `GET /search`

- Summary: Search Endpoint
- Deprecation Status: Active
- Migration Targets: -
- Tags: `search`

**System Context**
Search APIs used by global search interfaces and discovery pages.

**Semantic Description**
Search canonical doha content.

**Pragmatic Integration Notes**
Preferred endpoint for new integrations.

**Used In System**
- Frontend references: `frontend/src/components/Header.astro`, `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/search/SearchExperience.svelte`, `frontend/src/pages/404.astro`, `frontend/src/pages/[...slug].astro`, `frontend/src/pages/dictionary.astro`, `frontend/src/pages/idioms.astro`, `frontend/src/pages/index.astro`
- Backend references: `backend/app/api/v1/article.py`, `backend/app/api/v1/poetry.py`, `backend/app/api/v1/search.py`, `backend/app/management/generate_pydantic_db_mapping.py`, `backend/app/services/search_service.py`
- Test coverage refs: `backend/tests/test_api_v1_aliases.py`, `backend/tests/test_rate_limiter.py`, `backend/tests/test_search.py`

**Parameters**
| Name | In | Required | Type | Description |
|---|---|---|---|---|
| q | query | no | anyOf | Search query |
| author | query | no | anyOf | Author slug |
| work | query | no | anyOf | Work slug |
| chapter | query | no | anyOf | Chapter slug |
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


## `/submissions`

### `POST /submissions`

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
- Frontend references: `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/dashboard/SubmissionsClient.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/submission/SubmissionDetail.svelte`, `frontend/src/components/submission/SubmissionEditForm.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionsClient.svelte`
- Backend references: `backend/app/api/v1/moderation.py`, `backend/app/api/v1/submissions.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`, `backend/tests/test_rate_limiter.py`, `backend/tests/test_submissions.py`

**Parameters**
- None

**Request Body**
- `application/json`: `SubmissionCreateIn`

**Responses**
| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | SubmissionOut |
| 422 | Validation Error | HTTPValidationError |


## `/submissions/me`

### `GET /submissions/me`

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
- Frontend references: `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/user/Dashboard.svelte`, `frontend/src/components/user/MySubmissions.svelte`, `frontend/src/lib/submissions.ts`
- Backend references: None found
- Test coverage refs: `backend/tests/test_submissions.py`

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


## `/submissions/{submission_id}`

### `GET /submissions/{submission_id}`

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
- Frontend references: `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/dashboard/SubmissionsClient.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/submission/SubmissionDetail.svelte`, `frontend/src/components/submission/SubmissionEditForm.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionsClient.svelte`
- Backend references: `backend/app/api/v1/moderation.py`, `backend/app/api/v1/submissions.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`, `backend/tests/test_rate_limiter.py`, `backend/tests/test_submissions.py`

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

### `PUT /submissions/{submission_id}`

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
- Frontend references: `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/dashboard/SubmissionsClient.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/submission/SubmissionDetail.svelte`, `frontend/src/components/submission/SubmissionEditForm.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionsClient.svelte`
- Backend references: `backend/app/api/v1/moderation.py`, `backend/app/api/v1/submissions.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`, `backend/tests/test_rate_limiter.py`, `backend/tests/test_submissions.py`

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

### `DELETE /submissions/{submission_id}`

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
- Frontend references: `frontend/src/components/dashboard/DashboardClient.svelte`, `frontend/src/components/dashboard/SubmissionsClient.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/submission/SubmissionDetail.svelte`, `frontend/src/components/submission/SubmissionEditForm.svelte`, `frontend/src/components/submission/SubmissionForm.svelte`, `frontend/src/components/submission/SubmissionsClient.svelte`
- Backend references: `backend/app/api/v1/moderation.py`, `backend/app/api/v1/submissions.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_canonical_doha.py`, `backend/tests/test_dictionary_idiom_article.py`, `backend/tests/test_moderation.py`, `backend/tests/test_rate_limiter.py`, `backend/tests/test_submissions.py`

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


## `/users/{username}`

### `GET /users/{username}`

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
- Frontend references: `frontend/src/components/admin/SystemStatus.svelte`, `frontend/src/components/moderation/ModerationDetail.svelte`, `frontend/src/components/moderation/ModerationQueue.svelte`, `frontend/src/components/user/Dashboard.svelte`, `frontend/src/components/user/ProfileEditor.svelte`, `frontend/src/components/user/UserBookmarks.svelte`, `frontend/src/layouts/AdminLayout.astro`, `frontend/src/lib/admin.ts`
- Backend references: `backend/app/api/v1/admin_users.py`, `backend/app/api/v1/interactions.py`, `backend/app/api/v1/users.py`, `backend/app/core/security.py`, `backend/app/management/generate_pydantic_db_mapping.py`
- Test coverage refs: `backend/tests/test_admin_observability.py`, `backend/tests/test_admin_openapi_contract.py`, `backend/tests/test_auth_endpoints.py`, `backend/tests/test_interactions.py`, `backend/tests/test_user_stats.py`

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


## `/users/{username}/stats`

### `GET /users/{username}/stats`

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
- Frontend references: None found
- Backend references: None found
- Test coverage refs: None found

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
