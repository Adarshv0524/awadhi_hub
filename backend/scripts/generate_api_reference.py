from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.main import app


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "z_documentation" / "api" / "API_REFERENCE.md"
SCAN_PATHS = [
    ROOT / "frontend" / "src",
    ROOT / "backend" / "tests",
    ROOT / "backend" / "app",
]

TAG_CONTEXT = {
    "auth": "Authentication and session lifecycle. Used by login/logout flows, AuthGuard, and role checks across admin and contributor pages.",
    "admin-users": "Admin user management for listing users and updating roles/permissions/account state. Used by frontend admin users dashboard.",
    "admin-system-settings": "System configuration APIs for runtime settings, feature flags, and rate-limit controls. Used by frontend admin settings page.",
    "admin-audit": "Administrative audit trail retrieval APIs. Used by frontend admin audit page and incident analysis workflows.",
    "admin-hierarchy": "Admin write APIs for author/work/chapter hierarchy management. Used by frontend admin hierarchy editor.",
    "analytics": "Analytics and reporting APIs for admin and moderator dashboards, content performance, and trend monitoring.",
    "analytics-live": "Public real-time leaderboard and analytics streaming APIs for live ranking views.",
    "moderation": "Moderation queue and decision APIs for approve/reject workflows and batch moderation.",
    "submissions": "Contributor submission lifecycle APIs: create, update, submit for review, and retrieve user submissions.",
    "content": "Canonical content retrieval APIs used by public pages and navigation workflows.",
    "search": "Search APIs used by global search interfaces and discovery pages.",
    "users": "Public/user profile and contributor-focused user data APIs.",
    "dictionary": "Dictionary canonical content APIs used by dictionary listing/detail and contributor workflows.",
    "idiom": "Idiom canonical content APIs used by idiom listing/detail and moderation publishing.",
    "article": "Article listing/detail/search APIs used by article pages and recommendation workflows.",
    "poetry": "Poetry node and chapter rendering APIs used by poetry readers and hybrid content rendering.",
    "telemetry": "Operational telemetry ingestion and observability APIs used by auth guard, admin analytics, and SLO dashboards.",
    "interactions": "Likes/bookmarks/shares interaction APIs used by engagement widgets and dashboards.",
    "recommendations": "Recommendation APIs used by suggestion panels and personalization experiments.",
}

MIGRATION_TARGETS: dict[tuple[str, str], list[str]] = {
    ("GET", "/analytics/top"): ["GET /admin/analytics/v2/top"],
    ("GET", "/analytics/growth"): ["GET /admin/analytics/v2/growth"],
    ("GET", "/analytics/demand"): ["GET /admin/analytics/v2/demand"],
    ("GET", "/admin/analytics/contributor-trends"): ["GET /admin/analytics/v2/growth"],
    ("GET", "/admin/analytics/content-performance"): ["GET /admin/analytics/v2/top"],
    ("GET", "/admin/audit_logs/export/csv"): ["GET /admin/audit_logs"],
    ("GET", "/articles/search/advanced"): ["GET /search", "GET /articles"],
    ("GET", "/articles/tags/list"): ["GET /articles"],
    ("GET", "/articles/recent/list"): ["GET /articles?sort=recent"],
}


def _path_tokens(path: str) -> list[str]:
    path = re.sub(r"\{[^}]+\}", "", path)
    return [token for token in path.split("/") if token]


def _usage_query_candidates(path: str) -> list[str]:
    candidates = {path}
    candidates.add(re.sub(r"\{[^}]+\}", "", path).rstrip("/"))
    tokens = _path_tokens(path)
    if tokens:
        candidates.add("/" + "/".join(tokens[:2]))
    return sorted(candidate for candidate in candidates if candidate)


def _collect_usage(path: str) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {"frontend": [], "backend": [], "tests": []}
    candidates = _usage_query_candidates(path)

    for scan_root in SCAN_PATHS:
        if not scan_root.exists():
            continue
        for file_path in scan_root.rglob("*"):
            if file_path.suffix not in {".py", ".ts", ".tsx", ".astro", ".svelte", ".md"}:
                continue
            rel = file_path.relative_to(ROOT).as_posix()
            try:
                source = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            if not any(candidate and candidate in source for candidate in candidates):
                continue

            if rel.startswith("frontend/"):
                refs["frontend"].append(rel)
            elif rel.startswith("backend/tests/"):
                refs["tests"].append(rel)
            else:
                refs["backend"].append(rel)

    for key in refs:
        refs[key] = sorted(set(refs[key]))[:8]
    return refs


def _schema_ref(schema: dict[str, Any] | None) -> str:
    if not schema:
        return "-"
    if "$ref" in schema:
        return str(schema["$ref"]).replace("#/components/schemas/", "")
    if schema.get("type"):
        return str(schema["type"])
    if "anyOf" in schema:
        return "anyOf"
    if "allOf" in schema:
        return "allOf"
    if "oneOf" in schema:
        return "oneOf"
    return "object"


def _render_parameters(parameters: list[dict[str, Any]]) -> list[str]:
    if not parameters:
        return ["- None"]
    lines = ["| Name | In | Required | Type | Description |", "|---|---|---|---|---|"]
    for param in parameters:
        schema = param.get("schema") or {}
        lines.append(
            "| {name} | {in_} | {required} | {ptype} | {desc} |".format(
                name=param.get("name", "-"),
                in_=param.get("in", "-"),
                required="yes" if param.get("required") else "no",
                ptype=_schema_ref(schema),
                desc=(param.get("description") or "").replace("\n", " "),
            )
        )
    return lines


def _render_request_body(operation: dict[str, Any]) -> list[str]:
    body = operation.get("requestBody") or {}
    content = body.get("content") or {}
    if not content:
        return ["- None"]
    lines = []
    for media_type, media_schema in sorted(content.items()):
        schema = media_schema.get("schema") or {}
        lines.append(f"- `{media_type}`: `{_schema_ref(schema)}`")
    return lines


def _render_responses(operation: dict[str, Any]) -> list[str]:
    responses = operation.get("responses") or {}
    if not responses:
        return ["- None"]
    lines = ["| Status | Description | Schema |", "|---|---|---|"]
    for status, payload in sorted(responses.items(), key=lambda item: item[0]):
        content = payload.get("content") or {}
        if content:
            first_media = sorted(content.items(), key=lambda item: item[0])[0][1]
            schema = _schema_ref(first_media.get("schema") or {})
        else:
            schema = "-"
        lines.append(
            "| {status} | {desc} | {schema} |".format(
                status=status,
                desc=(payload.get("description") or "").replace("\n", " "),
                schema=schema,
            )
        )
    return lines


def _context_for_tags(tags: list[str]) -> str:
    contexts = [TAG_CONTEXT[tag] for tag in tags if tag in TAG_CONTEXT]
    if contexts:
        return " ".join(contexts)
    return "Core platform API endpoint. Confirm consumer flows in frontend modules and backend integration tests."


def _pragmatic_notes(method: str, path: str, deprecated: bool, tags: list[str]) -> str:
    notes = []
    if deprecated:
        targets = MIGRATION_TARGETS.get((method, path), [])
        if targets:
            notes.append("Deprecated: migrate clients to " + ", ".join(f"`{t}`" for t in targets) + ".")
        else:
            notes.append("Deprecated: migration target not explicitly mapped; verify with owning module before integrating.")
    else:
        notes.append("Preferred endpoint for new integrations.")

    if any(tag.startswith("admin") for tag in tags) or path.startswith("/admin"):
        notes.append("Requires admin-level authorization in normal operation.")
    elif "moderation" in tags:
        notes.append("Requires moderator or higher role for write actions.")
    elif "auth" in tags:
        notes.append("Used in login/session lifecycle; failures directly impact route guards.")

    return " ".join(notes)


def generate_api_reference() -> str:
    schema = app.openapi()
    paths: dict[str, Any] = schema.get("paths", {})
    title = schema.get("info", {}).get("title", "API")
    version = schema.get("info", {}).get("version", "unknown")

    lines: list[str] = []
    lines.append(f"# {title} API Reference (OpenAPI Generated)")
    lines.append("")
    lines.append("This document is auto-generated from backend OpenAPI (`app.openapi()`).")
    lines.append("Do not hand-edit this file. Run `python backend/scripts/generate_api_reference.py`.")
    lines.append("")
    lines.append(f"- OpenAPI version: `{schema.get('openapi', 'unknown')}`")
    lines.append(f"- App version: `{version}`")
    lines.append(f"- Total paths: `{len(paths)}`")
    lines.append("")

    deprecated_count = 0
    operation_count = 0

    for path in sorted(paths.keys()):
        path_item = paths[path]
        lines.append(f"## `{path}`")
        lines.append("")

        for method in ["get", "post", "put", "patch", "delete", "options", "head"]:
            operation = path_item.get(method)
            if not operation:
                continue
            operation_count += 1

            method_upper = method.upper()
            deprecated = bool(operation.get("deprecated", False))
            if deprecated:
                deprecated_count += 1

            summary = operation.get("summary") or operation.get("operationId") or "No summary"
            description = operation.get("description") or "No explicit description in OpenAPI."
            tags = operation.get("tags") or []
            usage = _collect_usage(path)
            targets = MIGRATION_TARGETS.get((method_upper, path), [])

            lines.append(f"### `{method_upper} {path}`")
            lines.append("")
            lines.append(f"- Summary: {summary}")
            lines.append(f"- Deprecation Status: {'Deprecated' if deprecated else 'Active'}")
            lines.append(f"- Migration Targets: {', '.join(f'`{t}`' for t in targets) if targets else '-'}")
            lines.append(f"- Tags: {', '.join(f'`{tag}`' for tag in tags) if tags else '-'}")
            lines.append("")
            lines.append("**System Context**")
            lines.append(_context_for_tags(tags))
            lines.append("")
            lines.append("**Semantic Description**")
            lines.append(description)
            lines.append("")
            lines.append("**Pragmatic Integration Notes**")
            lines.append(_pragmatic_notes(method_upper, path, deprecated, tags))
            lines.append("")
            lines.append("**Used In System**")
            lines.append("- Frontend references: " + (", ".join(f"`{p}`" for p in usage["frontend"]) if usage["frontend"] else "None found"))
            lines.append("- Backend references: " + (", ".join(f"`{p}`" for p in usage["backend"]) if usage["backend"] else "None found"))
            lines.append("- Test coverage refs: " + (", ".join(f"`{p}`" for p in usage["tests"]) if usage["tests"] else "None found"))
            lines.append("")
            lines.append("**Parameters**")
            lines.extend(_render_parameters(operation.get("parameters") or []))
            lines.append("")
            lines.append("**Request Body**")
            lines.extend(_render_request_body(operation))
            lines.append("")
            lines.append("**Responses**")
            lines.extend(_render_responses(operation))
            lines.append("")

        lines.append("")

    lines.insert(9, f"- Total operations: `{operation_count}`")
    lines.insert(10, f"- Deprecated operations: `{deprecated_count}`")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    doc = generate_api_reference()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(doc, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH.relative_to(ROOT)), "bytes": len(doc.encode("utf-8"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
