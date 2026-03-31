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
        ("GET", "/api/v1/admin/users"),
        ("PATCH", "/api/v1/admin/users/{user_id}"),
        ("GET", "/api/v1/admin/audit_logs"),
        ("GET", "/api/v1/admin/audit_logs/{id}"),
        ("GET", "/api/v1/admin/system_settings"),
        ("PUT", "/api/v1/admin/system_settings/{key}"),
        ("DELETE", "/api/v1/admin/system_settings/{key}"),
        ("POST", "/api/v1/admin/system_settings/import"),
        ("POST", "/api/v1/admin/hierarchy/authors"),
        ("PATCH", "/api/v1/admin/hierarchy/authors/{author_id}"),
        ("POST", "/api/v1/admin/hierarchy/authors/{author_id}/works"),
        ("PATCH", "/api/v1/admin/hierarchy/works/{work_id}"),
        ("POST", "/api/v1/admin/hierarchy/works/{work_id}/chapters"),
        ("PATCH", "/api/v1/admin/hierarchy/chapters/{chapter_id}"),
        ("GET", "/api/v1/authors"),
        ("GET", "/api/v1/authors/{author_slug}/works"),
        ("GET", "/api/v1/authors/{author_slug}/works/{work_slug}/chapters"),
        ("GET", "/api/v1/auth/me"),
        ("GET", "/api/v1/admin/analytics/summary"),
        ("GET", "/api/v1/admin/analytics/insights"),
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
        "/api/v1/admin/analytics/summary",
        "/api/v1/admin/analytics/insights",
    }

    for endpoint in analytics_paths:
        assert endpoint in combined, f"Expected frontend to reference endpoint: {endpoint}"
        operation = openapi_paths.get(endpoint, {}).get("get")
        assert operation is not None, f"OpenAPI missing GET operation for {endpoint}"
        assert operation.get("deprecated") is not True, (
            f"Frontend is using deprecated analytics endpoint according to OpenAPI: {endpoint}"
        )

    legacy_v2_paths = [p for p in openapi_paths.keys() if p.startswith("/api/v1/admin/analytics/v2/")]
    assert not legacy_v2_paths, (
        "Legacy analytics v2 endpoints should not be exposed in OpenAPI:\n"
        + "\n".join(sorted(legacy_v2_paths))
    )


def test_openapi_has_no_double_v1_prefix_paths() -> None:
    openapi_paths = _load_openapi_paths()
    bad_paths = [p for p in openapi_paths.keys() if "/api/v1/api/v1/" in p]
    assert not bad_paths, "OpenAPI contains duplicated version prefix paths:\n" + "\n".join(sorted(bad_paths))


def test_openapi_has_no_doha_named_content_paths() -> None:
    openapi_paths = _load_openapi_paths()
    bad_paths = [
        p
        for p in openapi_paths.keys()
        if p.startswith("/api/v1/content/") and ("/doha" in p or "/dohas" in p)
    ]
    assert not bad_paths, (
        "OpenAPI still exposes doha-named canonical content routes:\n" + "\n".join(sorted(bad_paths))
    )
