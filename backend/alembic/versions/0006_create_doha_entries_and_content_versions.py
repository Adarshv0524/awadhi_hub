"""create doha_entries and content_versions

Revision ID: 0006_doha_content
Revises: 0005_create_moderation_tables
Create Date: 2025-12-01 00:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006_doha_content"
down_revision = "0005_create_moderation_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "doha_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("hierarchy_path", sa.String(length=512), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("work_id", sa.Integer(), nullable=True),
        sa.Column("chapter_id", sa.Integer(), nullable=True),
        sa.Column("number_in_chapter", sa.Integer(), nullable=True),
        sa.Column("main_text", sa.Text(), nullable=False),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("text_devanagari", sa.Text(), nullable=True),
        sa.Column("text_romanized", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default="public"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_canonical", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("variant_group_id", sa.Integer(), nullable=True),
        sa.Column("confidence_level", sa.Integer(), nullable=True),
        sa.Column("source_reference", sa.JSON(), nullable=True),
        sa.Column("source_submission_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("verified_by", sa.Integer(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("source_submission_id", name="uq_doha_source_submission"),
    )

    op.create_index("ix_doha_hierarchy_path", "doha_entries", ["hierarchy_path"])
    op.create_index("ix_doha_author_id", "doha_entries", ["author_id"])
    op.create_index("ix_doha_work_id", "doha_entries", ["work_id"])
    op.create_index("ix_doha_chapter_id", "doha_entries", ["chapter_id"])

    op.create_table(
        "content_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("main_text", sa.Text(), nullable=True),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("text_devanagari", sa.Text(), nullable=True),
        sa.Column("text_romanized", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_index(
        "ix_content_versions_type_id",
        "content_versions",
        ["content_type", "content_id"],
    )


def downgrade():
    op.drop_index("ix_content_versions_type_id", table_name="content_versions")
    op.drop_table("content_versions")

    op.drop_index("ix_doha_chapter_id", table_name="doha_entries")
    op.drop_index("ix_doha_work_id", table_name="doha_entries")
    op.drop_index("ix_doha_author_id", table_name="doha_entries")
    op.drop_index("ix_doha_hierarchy_path", table_name="doha_entries")
    op.drop_table("doha_entries")
