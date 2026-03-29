"""ai governance and retention

Revision ID: 0021_ai_governance_and_retention
Revises: 0020_admin_event_taxonomy_v2
Create Date: 2026-03-29 02:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0021_ai_governance_and_retention"
down_revision = "0020_admin_event_taxonomy_v2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_governance_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("recommendation_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("use_case", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_model_governance_events_recommendation_id", "model_governance_events", ["recommendation_id"])
    op.create_index("ix_model_governance_events_event_type", "model_governance_events", ["event_type"])
    op.create_index("ix_model_governance_events_use_case", "model_governance_events", ["use_case"])
    op.create_index("ix_model_governance_events_actor_user_id", "model_governance_events", ["actor_user_id"])
    op.create_index("ix_model_governance_events_created_at", "model_governance_events", ["created_at"])
    op.create_index("ix_model_gov_rec_type", "model_governance_events", ["recommendation_id", "event_type"])
    op.create_index("ix_model_gov_use_case_created", "model_governance_events", ["use_case", "created_at"])

    op.create_table(
        "data_retention_policies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_class", sa.String(length=64), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("delete_mode", sa.String(length=16), nullable=False, server_default="hard"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("event_class", name="uq_data_retention_event_class"),
    )
    op.create_index("ix_data_retention_policies_event_class", "data_retention_policies", ["event_class"])


def downgrade() -> None:
    op.drop_index("ix_data_retention_policies_event_class", table_name="data_retention_policies")
    op.drop_table("data_retention_policies")

    op.drop_index("ix_model_gov_use_case_created", table_name="model_governance_events")
    op.drop_index("ix_model_gov_rec_type", table_name="model_governance_events")
    op.drop_index("ix_model_governance_events_created_at", table_name="model_governance_events")
    op.drop_index("ix_model_governance_events_actor_user_id", table_name="model_governance_events")
    op.drop_index("ix_model_governance_events_use_case", table_name="model_governance_events")
    op.drop_index("ix_model_governance_events_event_type", table_name="model_governance_events")
    op.drop_index("ix_model_governance_events_recommendation_id", table_name="model_governance_events")
    op.drop_table("model_governance_events")
