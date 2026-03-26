"""create rate_limit_counters table

Revision ID: 0009_rate_limit_counters
Revises: 0008_engagement_kpis
Create Date: 2025-12-11 00:00:00.000002
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_rate_limit_counters"
down_revision = "0008_engagement_kpis"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rate_limit_counters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("action_key", sa.String(128), nullable=False),
        sa.Column("time_bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("granularity", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "ip_address", "action_key", "time_bucket_start", name="uq_rate_limit_bucket"),
    )
    op.create_index("ix_rl_action_bucket", "rate_limit_counters", ["action_key", "time_bucket_start"])


def downgrade():
    op.drop_index("ix_rl_action_bucket", table_name="rate_limit_counters")
    op.drop_table("rate_limit_counters")
