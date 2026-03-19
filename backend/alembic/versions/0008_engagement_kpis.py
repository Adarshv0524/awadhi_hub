"""create engagement_kpis table

Revision ID: 0008_engagement_kpis
Revises: 0007_doha_fulltext_index
Create Date: 2025-12-11 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_engagement_kpis"
down_revision = "0007_doha_fulltext_index"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "engagement_kpis",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),  # CHANGED
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("search_hits_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weight_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("content_type", "content_id", name="uq_engagement_content"),
    )
    op.create_index("ix_engagement_content", "engagement_kpis", ["content_type", "content_id"])


def downgrade():
    op.drop_index("ix_engagement_content", table_name="engagement_kpis")
    op.drop_table("engagement_kpis")
