#!/usr/bin/env python3
"""Validate ORM metadata against a migration-built database schema."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import current_timestamp

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.models import Base


def build_alembic_config(sqlalchemy_url: str) -> Config:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", sqlalchemy_url)
    return cfg


def enable_sqlite_migration_compat() -> None:
    # Some legacy migrations emit CURRENT_TIMESTAMP() which SQLite rejects.
    @compiles(current_timestamp, "sqlite")
    def _compile_current_timestamp_sqlite(element, compiler, **kw):
        return "CURRENT_TIMESTAMP"


def affinity(type_name: str) -> str:
    t = type_name.upper()
    if "INT" in t:
        return "INTEGER"
    if any(token in t for token in ("CHAR", "CLOB", "TEXT", "JSON")):
        return "TEXT"
    if "BLOB" in t:
        return "BLOB"
    if any(token in t for token in ("REAL", "FLOA", "DOUB")):
        return "REAL"
    if any(token in t for token in ("DATE", "TIME")):
        return "TEXT"
    if any(token in t for token in ("DEC", "NUM")):
        return "NUMERIC"
    if "BOOL" in t:
        return "INTEGER"
    return "NUMERIC"


def orm_schema() -> Dict[str, Dict[str, Dict[str, Any]]]:
    schema: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for table_name, table in Base.metadata.tables.items():
        schema[table_name] = {}
        for col in table.columns:
            schema[table_name][col.name] = {
                "type": str(col.type),
                "affinity": affinity(str(col.type)),
                "nullable": bool(col.nullable),
            }
    return schema


def db_schema(sqlalchemy_url: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    schema: Dict[str, Dict[str, Dict[str, Any]]] = {}
    engine = create_engine(sqlalchemy_url)
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        if table_name == "alembic_version":
            continue
        schema[table_name] = {}
        for col in inspector.get_columns(table_name):
            col_type = str(col.get("type"))
            schema[table_name][col["name"]] = {
                "type": col_type,
                "affinity": affinity(col_type),
                "nullable": bool(col.get("nullable", True)),
            }
    engine.dispose()
    return schema


def inject_simulated_drift() -> None:
    submissions = Base.metadata.tables.get("submissions")
    if submissions is None:
        raise RuntimeError("Table 'submissions' not found in Base.metadata")
    if "ci_drift_probe" not in submissions.c:
        submissions.append_column(sa.Column("ci_drift_probe", sa.Integer(), nullable=True))


def compare_schemas(
    expected: Dict[str, Any],
    actual: Dict[str, Any],
    *,
    check_nullability: bool,
) -> list[str]:
    diffs: list[str] = []

    expected_tables = set(expected)
    actual_tables = set(actual)

    for table in sorted(expected_tables - actual_tables):
        diffs.append(f"Missing table in migrated DB: {table}")
    for table in sorted(actual_tables - expected_tables):
        diffs.append(f"Unexpected table in migrated DB: {table}")

    for table in sorted(expected_tables & actual_tables):
        exp_cols = expected[table]
        act_cols = actual[table]
        exp_col_names = set(exp_cols)
        act_col_names = set(act_cols)

        for col in sorted(exp_col_names - act_col_names):
            diffs.append(f"{table}.{col}: missing in migrated DB")
        for col in sorted(act_col_names - exp_col_names):
            diffs.append(f"{table}.{col}: unexpected in migrated DB")

        for col in sorted(exp_col_names & act_col_names):
            exp = exp_cols[col]
            act = act_cols[col]

            if exp["affinity"] != act["affinity"]:
                diffs.append(
                    f"{table}.{col}: type mismatch ORM={exp['type']} ({exp['affinity']}) "
                    f"DB={act['type']} ({act['affinity']})"
                )
            if check_nullability and exp["nullable"] != act["nullable"]:
                diffs.append(
                    f"{table}.{col}: nullability mismatch ORM={exp['nullable']} DB={act['nullable']}"
                )

    return diffs


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate schema contract between ORM models and Alembic migrations")
    parser.add_argument(
        "--simulate-drift",
        action="store_true",
        help="Inject metadata-only drift to verify this check fails",
    )
    parser.add_argument(
        "--check-nullability",
        action="store_true",
        help="Also fail on ORM-vs-migration nullability differences",
    )
    args = parser.parse_args()

    sqlite_url = "sqlite:///file:schema_contract_guard?mode=memory&cache=shared&uri=true"
    keepalive_engine = create_engine(sqlite_url)
    keepalive_conn = keepalive_engine.connect()

    prev_override = os.environ.get("ALEMBIC_DATABASE_URL")
    os.environ["ALEMBIC_DATABASE_URL"] = sqlite_url

    try:
        enable_sqlite_migration_compat()
        command.upgrade(build_alembic_config(sqlite_url), "head")

        if args.simulate_drift:
            inject_simulated_drift()

        expected = orm_schema()
        actual = db_schema(sqlite_url)
        diffs = compare_schemas(expected, actual, check_nullability=args.check_nullability)

        if diffs:
            print("Schema contract check failed. Drift detected:")
            for idx, diff in enumerate(diffs, start=1):
                print(f"  {idx}. {diff}")
            return 1

        print("Schema contract check passed: migrated DB schema matches ORM metadata")
        return 0
    finally:
        if prev_override is None:
            os.environ.pop("ALEMBIC_DATABASE_URL", None)
        else:
            os.environ["ALEMBIC_DATABASE_URL"] = prev_override
        keepalive_conn.close()
        keepalive_engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
