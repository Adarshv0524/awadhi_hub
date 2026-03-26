#!/usr/bin/env python3
"""Run Alembic upgrade on a clean DB and assert runtime-critical schema invariants."""

from __future__ import annotations

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.settings import settings


def build_alembic_config() -> Config:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.mysql_url)
    return cfg


def assert_columns(insp, table_name: str, must_have: set[str], must_not_have: set[str]) -> None:
    actual = {col["name"] for col in insp.get_columns(table_name)}
    missing = must_have - actual
    unexpected = must_not_have & actual
    if missing:
        raise AssertionError(f"{table_name} missing columns: {sorted(missing)}")
    if unexpected:
        raise AssertionError(f"{table_name} has forbidden columns: {sorted(unexpected)}")


def assert_alembic_version_num_widened(engine) -> None:
    with engine.connect() as conn:
        length = conn.execute(
            text(
                """
                SELECT CHARACTER_MAXIMUM_LENGTH
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = 'alembic_version'
                  AND column_name = 'version_num'
                """
            )
        ).scalar()
    if length is None:
        raise AssertionError("alembic_version.version_num metadata unavailable")
    if int(length) < 255:
        raise AssertionError(f"alembic_version.version_num length is {length}, expected >= 255")


def assert_db_at_head(cfg: Config, engine) -> None:
    script = ScriptDirectory.from_config(cfg)
    expected_head = script.get_current_head()
    with engine.connect() as conn:
        current = MigrationContext.configure(conn).get_current_revision()
    if current != expected_head:
        raise AssertionError(f"database revision {current} != expected head {expected_head}")


def main() -> int:
    cfg = build_alembic_config()
    command.upgrade(cfg, "head")

    engine = create_engine(settings.mysql_url)
    inspector = inspect(engine)

    assert_columns(
        inspector,
        "submissions",
        must_have={"external_references"},
        must_not_have={"references"},
    )
    assert_columns(
        inspector,
        "system_settings",
        must_have={"setting_key"},
        must_not_have={"key"},
    )

    assert_alembic_version_num_widened(engine)
    assert_db_at_head(cfg, engine)

    print("Migration smoke test passed: upgrade path and reconciled schema are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
