# Admin Telemetry Schema (M2)

This schema powers centralized admin observability and SLO reporting.

## Event Model

Stored table: `admin_telemetry_events`

- `event_name` (string, required)
- `request_id` (string, optional)
- `actor_user_id` (int, optional)
- `actor_role` (string, required)
- `route` (string, optional)
- `http_method` (string, optional)
- `action_context` (object, optional)
- `result` (string, required): `success` | `failure` | `unknown`
- `latency_ms` (float, optional)
- `status_code` (int, optional)
- `failure_class` (string, optional): `auth` | `permission` | `not_found` | `rate_limit` | `client` | `server`
- `source` (string, required): `backend_middleware` | `frontend` | other source tags
- `metadata` (object, optional)
- `created_at` (datetime, generated)

## Ingestion Paths

1. Backend middleware auto-captures admin API calls (`/admin/*` and `/api/v1/admin/*`).
2. Explicit ingestion endpoint for UI/client actions:
   - `POST /api/v1/telemetry/admin-events`

## SLO Endpoint

- `GET /api/v1/telemetry/admin-observability/slo?window_minutes=60`

Response includes:

- `error_rate`
- `latency_ms.p95`
- `action_success_rate`
- failure class breakdown
