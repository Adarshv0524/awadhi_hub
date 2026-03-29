from __future__ import annotations

from app.main import app


def _resolve_ref(schema: dict, ref: str) -> dict:
    node = schema
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def _response_schema(schema: dict, path: str, method: str, status: str = "200") -> dict:
    operation = schema["paths"][path][method]
    payload = operation["responses"][status]["content"]["application/json"]["schema"]
    return _normalize_schema(schema, payload)


def _normalize_schema(schema: dict, payload: dict) -> dict:
    if "$ref" in payload:
        return _normalize_schema(schema, _resolve_ref(schema, payload["$ref"]))
    if "allOf" in payload:
        for item in payload["allOf"]:
            normalized = _normalize_schema(schema, item)
            if normalized.get("type") == "object" or "properties" in normalized:
                return normalized
    return payload


def test_audit_payload_contract_strict_fields() -> None:
    schema = app.openapi()

    list_schema = _response_schema(schema, "/admin/audit_logs", "get")
    assert list_schema["type"] == "object"
    assert "total" in list_schema["properties"]
    assert "results" in list_schema["properties"]

    items = list_schema["properties"]["results"]["items"]
    items = _normalize_schema(schema, items)

    required_fields = {
        "id",
        "actor_user_id",
        "action",
        "resource_type",
        "resource_id",
        "before",
        "after",
        "metadata",
        "created_at",
    }
    assert required_fields.issubset(set(items["properties"].keys()))

    created_at_prop = items["properties"]["created_at"]
    assert created_at_prop.get("type") == "string"


def test_hierarchy_number_field_contract() -> None:
    schema = app.openapi()

    chapters_schema = _response_schema(schema, "/authors/{author_slug}/works/{work_slug}/chapters", "get")
    assert chapters_schema.get("type") == "array"

    chapter_item = chapters_schema["items"]
    chapter_item = _normalize_schema(schema, chapter_item)

    assert "number" in chapter_item["properties"]
    assert chapter_item["properties"]["number"].get("type") == "integer"


def test_no_removed_deprecated_admin_analytics_routes_in_openapi() -> None:
    schema = app.openapi()
    removed = {
        "/analytics/top",
        "/analytics/growth",
        "/analytics/demand",
        "/admin/analytics/contributor-trends",
        "/admin/analytics/content-performance",
        "/admin/audit_logs/export/csv",
    }
    assert removed.isdisjoint(set(schema["paths"].keys()))
