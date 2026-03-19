from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sqlalchemy import inspect

from app.db.session import engine


@dataclass
class SchemaClass:
    file: str
    name: str
    fields: list[str]


SCHEMA_FILES = [
    "app/api/v1/auth.py",
    "app/api/v1/admin_users.py",
    "app/api/v1/admin_settings.py",
    "app/api/v1/hierarchy_admin.py",
    "app/api/v1/hierarchy_public.py",
    "app/api/v1/submissions.py",
    "app/api/v1/moderation.py",
    "app/api/v1/content.py",
    "app/api/v1/dictionary.py",
    "app/api/v1/idiom.py",
    "app/api/v1/article.py",
    "app/api/v1/interactions.py",
    "app/api/v1/users.py",
    "app/api/v1/search.py",
    "app/api/v1/analytics.py",
    "app/services/system_settings.py",
]

# Class -> primary DB table(s) used by endpoint/service logic.
SCHEMA_TABLE_MAP = {
    "RegisterIn": ["users"],
    "LoginIn": ["users", "refresh_tokens"],
    "RefreshIn": ["refresh_tokens"],
    "LogoutIn": ["refresh_tokens"],
    "UserCreateAdminIn": ["users"],
    "UserUpdateAdminIn": ["users"],
    "UserOut": ["users"],
    "PublicUserOut": ["users"],
    "SettingIn": ["system_settings"],
    "SettingOut": ["system_settings"],
    "AuthorCreateIn": ["classical_authors"],
    "AuthorUpdateIn": ["classical_authors"],
    "WorkCreateIn": ["classical_works"],
    "WorkUpdateIn": ["classical_works"],
    "ChapterCreateIn": ["work_chapters"],
    "ChapterUpdateIn": ["work_chapters"],
    "AuthorListOut": ["classical_authors"],
    "AuthorDetailOut": ["classical_authors"],
    "WorkOut": ["classical_works"],
    "WorkDetailOut": ["classical_works"],
    "ChapterOut": ["work_chapters"],
    "SubmissionCreateIn": ["submissions"],
    "SubmissionUpdateIn": ["submissions"],
    "SubmissionOut": ["submissions"],
    "ModerationSubmissionOut": ["submissions"],
    "ModerationActionIn": ["moderation_logs"],
    "ModerationBatchIn": ["submissions", "moderation_logs"],
    "BatchApproveIn": ["submissions"],
    "BatchApproveOut": ["submissions", "doha_entries", "dictionary_entries", "idiom_entries", "article_entries"],
    "DohaOut": ["doha_entries"],
    "ContentVersionOut": ["content_versions"],
    "DictionaryOut": ["dictionary_entries"],
    "DictionaryDetailOut": ["dictionary_entries"],
    "IdiomOut": ["idiom_entries"],
    "ArticleListOut": ["article_entries"],
    "ArticleDetailOut": ["article_entries"],
    "ArticleStatsOut": ["article_entries"],
    "ToggleIn": ["user_interactions", "engagement_kpis"],
    "ShareIn": ["share_logs", "engagement_kpis"],
    "ReportIn": ["reports"],
    "SearchItem": ["doha_entries", "engagement_kpis"],
    "SearchOut": ["doha_entries", "engagement_kpis"],
    "TopContentItem": ["engagement_kpis"],
    "GrowthSeries": ["users", "doha_entries", "dictionary_entries", "idiom_entries", "article_entries"],
    "DemandItem": ["engagement_kpis"],
    "RateLimitAction": ["system_settings"],
    "RateLimitsModel": ["system_settings"],
}

SPECIAL_FIELD_MAP = {
    # schema_field -> db_column
    ("SettingOut", "key"): "setting_key",
    ("SettingIn", "value"): "value",
    ("ToggleIn", "interaction"): "interaction_type",
    ("ShareIn", "metadata"): "share_metadata",
    ("ReportIn", "metadata"): "report_metadata",
}


def _is_basemodel_subclass(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "BaseModel":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
            return True
    return False


def parse_schema_classes(py_file: Path) -> list[SchemaClass]:
    mod = ast.parse(py_file.read_text(encoding="utf-8"))
    out: list[SchemaClass] = []
    for node in mod.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not _is_basemodel_subclass(node):
            continue
        fields: list[str] = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields.append(stmt.target.id)
        out.append(SchemaClass(file=str(py_file), name=node.name, fields=fields))
    return out


def collect_schemas(root: Path, files: Iterable[str]) -> list[SchemaClass]:
    schemas: list[SchemaClass] = []
    for rel in files:
        p = root / rel
        if p.exists():
            schemas.extend(parse_schema_classes(p))
    return schemas


def table_columns() -> dict[str, set[str]]:
    insp = inspect(engine)
    res: dict[str, set[str]] = {}
    for t in sorted(insp.get_table_names()):
        res[t] = {c["name"] for c in insp.get_columns(t)}
    return res


def match_fields(schema_name: str, fields: list[str], tables: list[str], cols_by_table: dict[str, set[str]]) -> list[str]:
    lines: list[str] = []
    for field in fields:
        mapped = False
        for table in tables:
            if table not in cols_by_table:
                continue
            target_col = SPECIAL_FIELD_MAP.get((schema_name, field), field)
            if target_col in cols_by_table[table]:
                lines.append(f"- {field} -> {table}.{target_col}")
                mapped = True
                break
        if not mapped:
            lines.append(f"- {field} -> (derived/validated/non-column)")
    return lines


def generate_markdown(root: Path) -> str:
    schemas = collect_schemas(root, SCHEMA_FILES)
    cols_by_table = table_columns()

    lines: list[str] = []
    lines.append("# Pydantic to Database Schema Mapping")
    lines.append("")
    lines.append("Generated from current code and live DB metadata.")
    lines.append("")

    lines.append("## Database Tables")
    lines.append("")
    for table, cols in cols_by_table.items():
        lines.append(f"### {table}")
        lines.append(f"Columns ({len(cols)}): {', '.join(sorted(cols))}")
        lines.append("")

    lines.append("## Pydantic Schemas")
    lines.append("")
    for sc in sorted(schemas, key=lambda s: (s.file, s.name)):
        rel = Path(sc.file)
        rel_disp = rel.as_posix().split("backend/")[-1]
        lines.append(f"### {sc.name}")
        lines.append(f"Source: {rel_disp}")
        lines.append(f"Fields: {', '.join(sc.fields) if sc.fields else '(none)'}")
        tables = SCHEMA_TABLE_MAP.get(sc.name, [])
        if tables:
            lines.append(f"Primary tables: {', '.join(tables)}")
            lines.append("Field mapping:")
            lines.extend(match_fields(sc.name, sc.fields, tables, cols_by_table))
        else:
            lines.append("Primary tables: (not directly persisted / response-only wrapper)")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- Some schemas (analytics/search wrappers) represent computed responses rather than direct table rows.")
    lines.append("- Mapping is based on field names, explicit special cases, and endpoint/service usage patterns.")
    return "\n".join(lines)


def main() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    workspace_root = backend_root.parent
    out_file = workspace_root / "z_documentation" / "runtime" / "PYDANTIC_DB_SCHEMA_MAPPING.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(generate_markdown(backend_root), encoding="utf-8")
    print(f"Wrote mapping file: {out_file}")


if __name__ == "__main__":
    main()
