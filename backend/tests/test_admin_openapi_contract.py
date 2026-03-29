from __future__ import annotations

from pathlib import Path

from app.main import app


ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ADMIN_WRAPPER = ROOT / "frontend" / "src" / "lib" / "admin.ts"
FRONTEND_ANALYTICS_WRAPPER = ROOT / "frontend" / "src" / "lib" / "analytics.ts"


def _load_openapi_paths() -> dict:
    schema = app.openapi()
    return schema.get("paths", {})


def test_frontend_admin_wrappers_match_openapi_paths_and_methods() -> None:
    openapi_paths = _load_openapi_paths()

    # Contracts consumed by frontend admin wrappers.
    # These are validated against OpenAPI to catch route/method drift.
    frontend_contracts = {
        ("GET", "/admin/users"),
        ("PATCH", "/admin/users/{user_id}"),
        ("GET", "/admin/audit_logs"),
        ("GET", "/admin/audit_logs/{id}"),
        ("GET", "/admin/system_settings"),
        ("PUT", "/admin/system_settings/{key}"),
        ("DELETE", "/admin/system_settings/{key}"),
        ("POST", "/admin/system_settings/import"),
        ("POST", "/admin/hierarchy/authors"),
        ("PATCH", "/admin/hierarchy/authors/{author_id}"),
        ("POST", "/admin/hierarchy/authors/{author_id}/works"),
        ("PATCH", "/admin/hierarchy/works/{work_id}"),
        ("POST", "/admin/hierarchy/works/{work_id}/chapters"),
        ("PATCH", "/admin/hierarchy/chapters/{chapter_id}"),
        ("GET", "/authors"),
        ("GET", "/authors/{author_slug}/works"),
        ("GET", "/authors/{author_slug}/works/{work_slug}/chapters"),
        ("GET", "/auth/me"),
        ("GET", "/admin/analytics/v2/top"),
        ("GET", "/admin/analytics/v2/growth"),
        ("GET", "/admin/analytics/v2/demand"),
        ("GET", "/admin/analytics/v2/summary"),
        ("GET", "/admin/analytics/v2/action-throughput"),
        ("GET", "/admin/analytics/v2/moderation-cycle-time"),
        ("GET", "/admin/analytics/v2/rbac-denials"),
        ("GET", "/admin/analytics/v2/events"),
    }

    missing: list[str] = []
    for method, path in sorted(frontend_contracts):
        operations = openapi_paths.get(path)
        if not operations:
            missing.append(f"{method} {path} (path missing from OpenAPI)")
            continue
        if method.lower() not in operations:
            missing.append(f"{method} {path} (method missing from OpenAPI)")

    assert not missing, "Frontend wrappers drifted from OpenAPI contracts:\n" + "\n".join(missing)


def test_admin_analytics_frontend_uses_non_deprecated_openapi_endpoints() -> None:
    openapi_paths = _load_openapi_paths()

    analytics_source = FRONTEND_ANALYTICS_WRAPPER.read_text(encoding="utf-8")
    admin_source = FRONTEND_ADMIN_WRAPPER.read_text(encoding="utf-8")
    combined = f"{analytics_source}\n{admin_source}"

    # Admin dashboard analytics endpoints that frontend currently targets.
    analytics_paths = {
        "/admin/analytics/v2/top",
        "/admin/analytics/v2/growth",
        "/admin/analytics/v2/demand",
        "/admin/analytics/v2/summary",
        "/admin/analytics/v2/action-throughput",
        "/admin/analytics/v2/moderation-cycle-time",
        "/admin/analytics/v2/rbac-denials",
        "/admin/analytics/v2/events",
    }

    for endpoint in analytics_paths:
        assert endpoint in combined, f"Expected frontend to reference endpoint: {endpoint}"
        operation = openapi_paths.get(endpoint, {}).get("get")
        assert operation is not None, f"OpenAPI missing GET operation for {endpoint}"
        assert operation.get("deprecated") is not True, (
            f"Frontend is using deprecated analytics endpoint according to OpenAPI: {endpoint}"
        )
