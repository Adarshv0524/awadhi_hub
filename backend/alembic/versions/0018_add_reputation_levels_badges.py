"""add reputation levels and badges

Revision ID: 0018_add_reputation_levels_badges
Revises: 0017_enforce_work_chapter_sequence_guardrails
Create Date: 2026-03-28 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0018_add_reputation_levels_badges"
down_revision = "0017_enforce_work_chapter_sequence_guardrails"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reputation_levels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("min_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_reputation_levels_slug"),
    )
    op.create_index("ix_reputation_levels_slug", "reputation_levels", ["slug"])

    op.create_table(
        "badge_definitions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=120), nullable=True),
        sa.Column("criteria", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_badge_definitions_slug"),
    )
    op.create_index("ix_badge_definitions_slug", "badge_definitions", ["slug"])

    op.create_table(
        "user_reputation",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_submissions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_level_id", sa.Integer(), sa.ForeignKey("reputation_levels.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_user_reputation_user_id"),
    )
    op.create_index("ix_user_reputation_user_id", "user_reputation", ["user_id"])

    op.create_table(
        "user_badges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("badge_definition_id", sa.Integer(), sa.ForeignKey("badge_definitions.id"), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("badge_metadata", sa.JSON(), nullable=True),
        sa.UniqueConstraint("user_id", "badge_definition_id", name="uq_user_badges_user_badge"),
    )
    op.create_index("ix_user_badges_user_id", "user_badges", ["user_id"])
    op.create_index("ix_user_badges_badge_definition_id", "user_badges", ["badge_definition_id"])

    op.bulk_insert(
        sa.table(
            "reputation_levels",
            sa.column("slug", sa.String),
            sa.column("name", sa.String),
            sa.column("min_points", sa.Integer),
            sa.column("description", sa.String),
        ),
        [
            {"slug": "novice", "name": "Novice", "min_points": 0, "description": "Getting started with contributions"},
            {"slug": "scribe", "name": "Scribe", "min_points": 100, "description": "Consistent contributor"},
            {"slug": "archivist", "name": "Archivist", "min_points": 300, "description": "Reliable and high-quality contributor"},
            {"slug": "ustad", "name": "Ustad", "min_points": 700, "description": "Top-tier community contributor"},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_user_badges_badge_definition_id", table_name="user_badges")
    op.drop_index("ix_user_badges_user_id", table_name="user_badges")
    op.drop_table("user_badges")

    op.drop_index("ix_user_reputation_user_id", table_name="user_reputation")
    op.drop_table("user_reputation")

    op.drop_index("ix_badge_definitions_slug", table_name="badge_definitions")
    op.drop_table("badge_definitions")

    op.drop_index("ix_reputation_levels_slug", table_name="reputation_levels")
    op.drop_table("reputation_levels")
