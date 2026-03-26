#!/usr/bin/env python3
"""Fail when SQLAlchemy metadata and Alembic migration state drift apart."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.autogenerate.api import produce_migrations
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations.ops import (
    AddColumnOp,
    AlterColumnOp,
    CreateTableOp,
    DropColumnOp,
    DropTableOp,
    ModifyTableOps,
)
from sqlalchemy import create_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.settings import settings
from app.db.models import Base


def build_alembic_config() -> Config:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.mysql_url)
    return cfg


def inject_simulated_drift() -> None:
    submissions = Base.metadata.tables.get("submissions")
    if submissions is None:
        raise RuntimeError("Table 'submissions' not found in Base.metadata")
    if "ci_drift_probe" not in submissions.c:
        submissions.append_column(sa.Column("ci_drift_probe", sa.Integer(), nullable=True))


def check_pending_autogen_changes() -> list[str]:
    engine = create_engine(settings.mysql_url)
    with engine.connect() as connection:
        migration_context = MigrationContext.configure(
            connection,
            opts={
                "target_metadata": Base.metadata,
                "compare_type": True,
                "compare_server_default": True,
            },
        )
        migration_script = produce_migrations(migration_context, Base.metadata)

    if migration_script.upgrade_ops.is_empty():
        return []

    dangerous_ops: list[str] = []

    def walk(ops: list[object]) -> None:
        for op in ops:
            if isinstance(op, ModifyTableOps):
                walk(op.ops)
                continue

            if isinstance(op, (CreateTableOp, DropTableOp)):
                dangerous_ops.append(str(op))
                continue

            if isinstance(op, (AddColumnOp, DropColumnOp)):
                dangerous_ops.append(str(op))
                continue

            # Column renames are represented as alter operations in some dialects.
            if isinstance(op, AlterColumnOp) and op.modify_name is not None:
                dangerous_ops.append(str(op))

    walk(migration_script.upgrade_ops.ops)
    return dangerous_ops


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Alembic/ORM schema contract")
    parser.add_argument(
        "--upgrade-head",
        action="store_true",
        help="Run 'alembic upgrade head' before checking for pending changes",
    )
    parser.add_argument(
        "--simulate-drift",
        action="store_true",
        help="Inject temporary metadata drift and expect this check to fail",
    )
    args = parser.parse_args()

    alembic_cfg = build_alembic_config()

    if args.upgrade_head:
        command.upgrade(alembic_cfg, "head")

    if args.simulate_drift:
        inject_simulated_drift()

    pending = check_pending_autogen_changes()
    if pending:
        print("Schema drift detected: pending autogenerate operations found")
        for idx, op in enumerate(pending, start=1):
            print(f"  {idx}. {op}")
        return 1

    print("Schema contract check passed: ORM metadata and migration state are in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
