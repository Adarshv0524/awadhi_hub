# Flutter Addendum Recheck List (Post-Development)

- [ ] Confirm the Flutter app is built from [flutter.md](flutter.md) scope only (no extra modules, no public-content creep).
- [ ] Confirm all secrets below are migrated to new credentials before staging/production.

- [ ] Recheck backend base URL is set in Flutter env to: http://localhost:8000
- [ ] Recheck localhost fallback URL is supported in client networking: http://127.0.0.1:8000
- [ ] Recheck backend runtime bind is reachable from emulator/device: host 0.0.0.0, port 8000
- [ ] Recheck frontend URL assumptions used by auth redirects: http://localhost:4321

- [ ] Recheck current backend DB credential values (to be replaced later):
- [ ] MYSQL_HOST=127.0.0.1
- [ ] MYSQL_PORT=3306
- [ ] MYSQL_USER=root
- [ ] MYSQL_PASSWORD=<REPLACE_WITH_SECURE_PASSWORD>
- [ ] MYSQL_DATABASE=awadhi_new

- [ ] Recheck current JWT/auth credential values (to be replaced later):
- [ ] JWT_ALGORITHM=HS256
- [ ] JWT_ACCESS_TOKEN_EXPIRES_SECONDS=900
- [ ] JWT_REFRESH_TOKEN_EXPIRES_SECONDS=1209600
- [ ] JWT_SECRET_KEY=<REPLACE_WITH_STRONG_RANDOM_SECRET>

- [ ] Recheck current Google OAuth values (to be replaced later):
- [ ] GOOGLE_CLIENT_ID=<REPLACE_WITH_GOOGLE_CLIENT_ID>
- [ ] GOOGLE_CLIENT_SECRET=<REPLACE_WITH_GOOGLE_CLIENT_SECRET>
- [ ] GOOGLE_REDIRECT_URI=http://localhost:8000/auth/oauth/google/callback

- [ ] Recheck current SMTP values (to be replaced later):
- [ ] SMTP_ENABLED=true
- [ ] SMTP_HOST=smtp.gmail.com
- [ ] SMTP_PORT=587
- [ ] SMTP_USERNAME=<REPLACE_WITH_SMTP_USERNAME>
- [ ] SMTP_PASSWORD=<REPLACE_WITH_SMTP_PASSWORD>
- [ ] SMTP_FROM_EMAIL=<REPLACE_WITH_FROM_EMAIL>
- [ ] SMTP_USE_TLS=true
- [ ] SMTP_USE_SSL=false
- [ ] PASSWORD_RESET_TOKEN_EXPIRES_SECONDS=3600

- [ ] Recheck frontend env values used by current web client (for parity in Flutter):
- [ ] PUBLIC_API_BASE=http://localhost:8000
- [ ] PUBLIC_FRONTEND_BASE_URL=http://localhost:4321

- [ ] Recheck CORS behavior expected for local dev origins:
- [ ] http://localhost:4321
- [ ] http://127.0.0.1:4321
- [ ] http://localhost:4322
- [ ] http://127.0.0.1:4322

- [ ] Recheck auth core routes work end-to-end from Flutter:
- [ ] POST /api/v1/auth/login
- [ ] POST /api/v1/auth/refresh
- [ ] POST /api/v1/auth/logout
- [ ] GET /api/v1/auth/me
- [ ] GET /api/v1/auth/oauth/google/login
- [ ] GET /api/v1/auth/oauth/google/callback

- [ ] Recheck moderator role gates and flows:
- [ ] GET /api/v1/moderation/submissions
- [ ] GET /api/v1/moderation/submissions/{submission_id}
- [ ] POST /api/v1/moderation/submissions/{submission_id}/approve
- [ ] POST /api/v1/moderation/submissions/{submission_id}/reject
- [ ] POST /api/v1/moderation/batch
- [ ] POST /api/v1/moderation/batch_approve
- [ ] GET /api/v1/analytics/summary

- [ ] Recheck admin users module:
- [ ] GET /api/v1/admin/users
- [ ] GET /api/v1/admin/users/{user_id}
- [ ] POST /api/v1/admin/users
- [ ] PATCH /api/v1/admin/users/{user_id}

- [ ] Recheck admin system settings module:
- [ ] GET /api/v1/admin/system_settings
- [ ] GET /api/v1/admin/system_settings/{key}
- [ ] PUT /api/v1/admin/system_settings/{key}
- [ ] DELETE /api/v1/admin/system_settings/{key}
- [ ] POST /api/v1/admin/system_settings/import

- [ ] Recheck admin audit module:
- [ ] GET /api/v1/admin/audit_logs
- [ ] GET /api/v1/admin/audit_logs/{id}

- [ ] Recheck admin hierarchy module:
- [ ] POST /api/v1/admin/hierarchy/authors
- [ ] PATCH /api/v1/admin/hierarchy/authors/{author_id}
- [ ] POST /api/v1/admin/hierarchy/authors/{author_id}/works
- [ ] PATCH /api/v1/admin/hierarchy/works/{work_id}
- [ ] POST /api/v1/admin/hierarchy/works/{work_id}/chapters
- [ ] PATCH /api/v1/admin/hierarchy/chapters/{chapter_id}

- [ ] Recheck admin analytics module:
- [ ] GET /api/v1/admin/analytics/summary
- [ ] GET /api/v1/admin/analytics/v2/summary
- [ ] GET /api/v1/admin/analytics/v2/top
- [ ] GET /api/v1/admin/analytics/v2/growth
- [ ] GET /api/v1/admin/analytics/v2/demand
- [ ] GET /api/v1/admin/analytics/v2/action-throughput
- [ ] GET /api/v1/admin/analytics/v2/moderation-cycle-time
- [ ] GET /api/v1/admin/analytics/v2/rbac-denials
- [ ] GET /api/v1/admin/analytics/v2/moderation-kpi
- [ ] GET /api/v1/admin/analytics/v2/events
- [ ] GET /api/v1/admin/analytics/v2/3d/actor-resource-graph
- [ ] GET /api/v1/admin/analytics/v2/3d/latency-error-surface

- [ ] Recheck AI and governance routes (primary expected paths):
- [ ] GET /api/v1/ai/moderation-triage
- [ ] POST /api/v1/ai/model-decision
- [ ] POST /api/v1/ai/settings-risk-score
- [ ] POST /api/v1/governance/retention/run
- [ ] GET /api/v1/governance/checklist
- [ ] GET /api/v1/governance/export/audit
- [ ] GET /api/v1/governance/export/telemetry

- [ ] Recheck telemetry routes (primary expected paths):
- [ ] POST /api/v1/telemetry/admin-events
- [ ] GET /api/v1/telemetry/admin-observability/slo
- [ ] GET /api/v1/telemetry/admin-observability/completeness
- [ ] POST /api/v1/telemetry/auth-policy

- [ ] Recheck path prefix edge-case handling in Flutter HTTP layer:
- [ ] If /api/v1/ai/* fails in environment, retry /api/v1/api/v1/ai/*
- [ ] If /api/v1/governance/* fails in environment, retry /api/v1/api/v1/governance/*
- [ ] If /api/v1/telemetry/* fails in environment, retry /api/v1/api/v1/telemetry/*

- [ ] Recheck legacy unprefixed route behavior (if backend env enables it):
- [ ] /admin/*, /moderation/*, /auth/* may exist without /api/v1 prefix
- [ ] Ensure Flutter always prefers /api/v1 first

- [ ] Recheck RBAC behavior from Flutter UI guards and backend responses:
- [ ] moderator cannot access admin-only screens/routes
- [ ] admin can access moderator and admin workflows
- [ ] non-auth user is redirected to login and token cleared on 401 refresh failure

- [ ] Recheck payload contract hotspots:
- [ ] Admin user updates only through PATCH /admin/users/{id}
- [ ] Audit response shape uses actor_user_id, before, after, metadata
- [ ] Hierarchy chapter field name is number (not order_num)

- [ ] Recheck Google login actual flow from Flutter web/deeplink:
- [ ] login starts from /api/v1/auth/oauth/google/login
- [ ] callback lands and tokens are persisted
- [ ] /api/v1/auth/me immediately returns correct role

- [ ] Recheck analytics and observability output quality:
- [ ] summary counters match moderation queue
- [ ] v2 analytics endpoints return non-empty data in seeded env
- [ ] admin-observability SLO/completeness return valid numeric payloads

- [ ] Recheck governance exports:
- [ ] moderators get only their own audit/telemetry rows where applicable
- [ ] admins can see full export scope

- [ ] Recheck Flutter build-time environment handoff:
- [ ] dev, staging, prod base URLs are externalized
- [ ] secrets are not hardcoded in source
- [ ] credential rotation checklist executed before release
