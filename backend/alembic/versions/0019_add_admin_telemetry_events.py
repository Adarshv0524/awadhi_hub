"""add admin telemetry events table

Revision ID: 0019_add_admin_telemetry_events
Revises: 0018_add_reputation_levels_badges
Create Date: 2026-03-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0019_add_admin_telemetry_events"
down_revision = "0018_add_reputation_levels_badges"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_telemetry_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_name", sa.String(length=120), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_role", sa.String(length=50), nullable=False, server_default="unknown"),
        sa.Column("route", sa.String(length=255), nullable=True),
        sa.Column("http_method", sa.String(length=16), nullable=True),
        sa.Column("action_context", sa.JSON(), nullable=True),
        sa.Column("result", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("failure_class", sa.String(length=120), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="backend"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_admin_telemetry_events_event_name", "admin_telemetry_events", ["event_name"])
    op.create_index("ix_admin_telemetry_events_request_id", "admin_telemetry_events", ["request_id"])
    op.create_index("ix_admin_telemetry_events_actor_user_id", "admin_telemetry_events", ["actor_user_id"])
    op.create_index("ix_admin_telemetry_events_actor_role", "admin_telemetry_events", ["actor_role"])
    op.create_index("ix_admin_telemetry_events_route", "admin_telemetry_events", ["route"])
    op.create_index("ix_admin_telemetry_events_result", "admin_telemetry_events", ["result"])
    op.create_index("ix_admin_telemetry_events_failure_class", "admin_telemetry_events", ["failure_class"])
    op.create_index("ix_admin_telemetry_events_source", "admin_telemetry_events", ["source"])
    op.create_index("ix_admin_telemetry_events_created_at", "admin_telemetry_events", ["created_at"])
    op.create_index(
        "ix_admin_telemetry_created_result",
        "admin_telemetry_events",
        ["created_at", "result"],
    )
    op.create_index(
        "ix_admin_telemetry_route_created",
        "admin_telemetry_events",
        ["route", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_admin_telemetry_route_created", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_created_result", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_created_at", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_source", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_failure_class", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_result", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_route", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_actor_role", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_actor_user_id", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_request_id", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_event_name", table_name="admin_telemetry_events")
    op.drop_table("admin_telemetry_events")
