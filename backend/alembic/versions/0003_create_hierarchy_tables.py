# alembic/versions/0003_create_hierarchy_tables.py
"""create classical hierarchy tables

Revision ID: 0003_create_hierarchy_tables
Revises: 0002_add_users_role_index
Create Date: 2025-12-01 00:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_create_hierarchy_tables"
down_revision = "0002_add_users_role_index"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "classical_authors",
        # CHANGE 1: BigInteger -> Integer
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("short_bio", sa.Text(), nullable=True),
        sa.Column("long_bio", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.UniqueConstraint("slug", name="uq_authors_slug"),
    )
    op.create_index("ix_authors_slug", "classical_authors", ["slug"])
    op.create_index("ix_authors_language", "classical_authors", ["language"])

    op.create_table(
        "classical_works",
        # CHANGE 2: BigInteger -> Integer
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        # CHANGE 3: BigInteger -> Integer (Foreign Key)
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("work_type", sa.String(length=50), nullable=True),
        sa.Column("original_script", sa.String(length=50), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.ForeignKeyConstraint(["author_id"], ["classical_authors.id"]),
        sa.UniqueConstraint("author_id", "slug", name="uq_works_author_slug"),
    )
    op.create_index("ix_works_author_id", "classical_works", ["author_id"])
    op.create_index("ix_works_slug", "classical_works", ["slug"])
    op.create_index("ix_works_work_type", "classical_works", ["work_type"])

    op.create_table(
        "work_chapters",
        # CHANGE 4: BigInteger -> Integer
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        # CHANGE 5: BigInteger -> Integer (Foreign Key)
        sa.Column("work_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("UTC_TIMESTAMP()")),
        sa.ForeignKeyConstraint(["work_id"], ["classical_works.id"]),
        sa.UniqueConstraint("work_id", "slug", name="uq_chapters_work_slug"),
        sa.UniqueConstraint("work_id", "number", name="uq_chapters_work_number"),
    )
    op.create_index("ix_chapters_work_id", "work_chapters", ["work_id"])
    op.create_index("ix_chapters_slug", "work_chapters", ["slug"])
    op.create_index("ix_chapters_number", "work_chapters", ["number"])


def downgrade():
    op.drop_index("ix_chapters_number", table_name="work_chapters")
    op.drop_index("ix_chapters_slug", table_name="work_chapters")
    op.drop_index("ix_chapters_work_id", table_name="work_chapters")
    op.drop_table("work_chapters")

    op.drop_index("ix_works_work_type", table_name="classical_works")
    op.drop_index("ix_works_slug", table_name="classical_works")
    op.drop_index("ix_works_author_id", table_name="classical_works")
    op.drop_table("classical_works")

    op.drop_index("ix_authors_language", table_name="classical_authors")
    op.drop_index("ix_authors_slug", table_name="classical_authors")
    op.drop_table("classical_authors")