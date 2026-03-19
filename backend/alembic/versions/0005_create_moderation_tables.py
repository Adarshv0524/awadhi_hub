# alembic/versions/0005_create_moderation_tables.py
"""create moderation tables

Revision ID: 0005_create_moderation_tables
Revises: 0004_create_submissions_table
Create Date: 2025-12-01 00:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_create_moderation_tables"
down_revision = "0004_create_submissions_table"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "moderation_guidelines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.UniqueConstraint("version", name="uq_moderation_guidelines_version"),
    )

    op.create_table(
        "moderation_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("moderator_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=True),
        sa.Column("to_status", sa.String(length=20), nullable=True),
        sa.Column("guideline_version", sa.String(length=50), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
    )

    op.create_index("ix_moderation_logs_submission", "moderation_logs", ["submission_id"])
    op.create_index("ix_moderation_logs_moderator", "moderation_logs", ["moderator_id"])


def downgrade():
    op.drop_index("ix_moderation_logs_moderator", table_name="moderation_logs")
    op.drop_index("ix_moderation_logs_submission", table_name="moderation_logs")
    op.drop_table("moderation_logs")
    op.drop_table("moderation_guidelines")
