"""add composite index for chapter doha sequence queries

Revision ID: 0015_add_doha_chapter_sequence_index
Revises: 0014_reconcile_schema_drift_runtime_critical
Create Date: 2026-03-26 00:00:00.000000
"""

from alembic import op
from sqlalchemy import inspect


revision = "0015_add_doha_chapter_sequence_index"
down_revision = "0014_reconcile_schema_drift_runtime_critical"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    idx_names = {idx["name"] for idx in inspect(bind).get_indexes("doha_entries")}
    if "ix_doha_chapter_status_deleted_num" not in idx_names:
        op.create_index(
            "ix_doha_chapter_status_deleted_num",
            "doha_entries",
            ["chapter_id", "status", "is_deleted", "number_in_chapter"],
        )


def downgrade():
    bind = op.get_bind()
    idx_names = {idx["name"] for idx in inspect(bind).get_indexes("doha_entries")}
    if "ix_doha_chapter_status_deleted_num" in idx_names:
        op.drop_index("ix_doha_chapter_status_deleted_num", table_name="doha_entries")
