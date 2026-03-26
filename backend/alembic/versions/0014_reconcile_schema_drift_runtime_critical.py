"""reconcile runtime-critical schema drift and optional book fulltext

Revision ID: 0014_reconcile_schema_drift_runtime_critical
Revises: 0013_add_interactions_reports_bookmarks
Create Date: 2026-03-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "0014_reconcile_schema_drift_runtime_critical"
down_revision = "0013_add_interactions_reports_bookmarks"
branch_labels = None
depends_on = None


def _table_columns(bind, table_name: str) -> set[str]:
    insp = inspect(bind)
    if table_name not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(table_name)}


def _has_fulltext_index(bind, table_name: str) -> bool:
    if bind.dialect.name != "mysql":
        return False

    count = bind.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND index_type = 'FULLTEXT'
            """
        ),
        {"table_name": table_name},
    ).scalar()
    return bool(count)


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # 1) submissions.references -> submissions.external_references
    sub_cols = _table_columns(bind, "submissions")
    if "references" in sub_cols and "external_references" not in sub_cols:
        if dialect == "sqlite":
            with op.batch_alter_table("submissions") as batch_op:
                batch_op.alter_column(
                    "references",
                    new_column_name="external_references",
                    existing_type=sa.JSON(),
                    nullable=True,
                )
        else:
            op.execute("ALTER TABLE submissions CHANGE COLUMN `references` external_references JSON NULL")
    elif "references" in sub_cols and "external_references" in sub_cols:
        op.execute(
            """
            UPDATE submissions
            SET external_references = `references`
            WHERE external_references IS NULL
            """
        )
        if dialect == "sqlite":
            with op.batch_alter_table("submissions") as batch_op:
                batch_op.drop_column("references")
        else:
            op.execute("ALTER TABLE submissions DROP COLUMN `references`")

    # 2) system_settings.key -> system_settings.setting_key
    ss_cols = _table_columns(bind, "system_settings")
    if "key" in ss_cols and "setting_key" not in ss_cols:
        if dialect == "sqlite":
            with op.batch_alter_table("system_settings") as batch_op:
                batch_op.alter_column(
                    "key",
                    new_column_name="setting_key",
                    existing_type=sa.String(length=255),
                    nullable=False,
                )
        else:
            op.execute(
                "ALTER TABLE system_settings CHANGE COLUMN `key` setting_key VARCHAR(255) NOT NULL"
            )

    # 3) widen alembic_version.version_num to prevent revision ID overflow
    av_cols = _table_columns(bind, "alembic_version")
    if "version_num" in av_cols and dialect == "mysql":
        op.execute("ALTER TABLE alembic_version MODIFY COLUMN version_num VARCHAR(255) NOT NULL")

    # 4) ensure book_entries has a FULLTEXT index when table exists.
    # Prefer (title, text), fall back to single-column text if needed.
    book_cols = _table_columns(bind, "book_entries")
    if dialect == "mysql" and book_cols and not _has_fulltext_index(bind, "book_entries"):
        if {"title", "text"}.issubset(book_cols):
            op.execute("CREATE FULLTEXT INDEX ft_book_entries_title_text ON book_entries (`title`, `text`)")
        elif "text" in book_cols:
            op.execute("CREATE FULLTEXT INDEX ft_book_entries_text ON book_entries (`text`)")


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != "mysql":
        return

    book_cols = _table_columns(bind, "book_entries")
    if book_cols and _has_fulltext_index(bind, "book_entries"):
        # Drop only indexes created by this migration if they exist.
        existing = {idx["name"] for idx in inspect(bind).get_indexes("book_entries")}
        if "ft_book_entries_title_text" in existing:
            op.execute("DROP INDEX ft_book_entries_title_text ON book_entries")
        if "ft_book_entries_text" in existing:
            op.execute("DROP INDEX ft_book_entries_text ON book_entries")
