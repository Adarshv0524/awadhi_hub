"""create submissions table

Revision ID: 0004_create_submissions_table
Revises: 0003_create_hierarchy_tables
Create Date: 2025-12-01 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "0004_create_submissions_table"
down_revision = "0003_create_hierarchy_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("main_text", sa.Text(), nullable=False),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("is_classical", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("author_slug", sa.String(length=150), nullable=True),
        sa.Column("work_slug", sa.String(length=150), nullable=True),
        sa.Column("chapter_slug", sa.String(length=150), nullable=True),
        sa.Column("number_in_chapter", sa.Integer(), nullable=True),
        sa.Column("references", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default="private"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("contributor_id", sa.Integer(), nullable=False),  # CHANGED
        sa.Column("assigned_moderator_id", sa.Integer(), nullable=True),  # CHANGED
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
    )

    op.create_index("ix_submissions_contributor", "submissions", ["contributor_id"])
    op.create_index("ix_submissions_status_created", "submissions", ["status", "created_at"])
    op.create_index("ix_submissions_assigned_mod", "submissions", ["assigned_moderator_id"])


def downgrade():
    op.drop_index("ix_submissions_assigned_mod", table_name="submissions")
    op.drop_index("ix_submissions_status_created", table_name="submissions")
    op.drop_index("ix_submissions_contributor", table_name="submissions")
    op.drop_table("submissions")
