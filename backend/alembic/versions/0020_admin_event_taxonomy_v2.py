"""admin event taxonomy v2

Revision ID: 0020_admin_event_taxonomy_v2
Revises: 0019_add_admin_telemetry_events
Create Date: 2026-03-29 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0020_admin_event_taxonomy_v2"
down_revision = "0019_add_admin_telemetry_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("admin_telemetry_events") as batch:
        batch.add_column(sa.Column("event_id", sa.String(length=36), nullable=True))
        batch.add_column(sa.Column("event_ts_utc", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("session_id", sa.String(length=128), nullable=True))
        batch.add_column(sa.Column("module", sa.String(length=32), nullable=True))
        batch.add_column(sa.Column("action", sa.String(length=32), nullable=True))
        batch.add_column(sa.Column("resource_type", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("resource_id", sa.String(length=128), nullable=True))
        batch.add_column(sa.Column("before_state_hash", sa.String(length=128), nullable=True))
        batch.add_column(sa.Column("after_state_hash", sa.String(length=128), nullable=True))
        batch.add_column(sa.Column("error_code", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("client_meta", sa.JSON(), nullable=True))

    op.execute("UPDATE admin_telemetry_events SET event_id = COALESCE(event_id, lower(hex(randomblob(16))))")
    op.execute("UPDATE admin_telemetry_events SET event_ts_utc = COALESCE(event_ts_utc, created_at)")
    op.execute("UPDATE admin_telemetry_events SET module = COALESCE(module, 'analytics')")
    op.execute("UPDATE admin_telemetry_events SET action = COALESCE(action, 'view')")

    with op.batch_alter_table("admin_telemetry_events") as batch:
        batch.alter_column("event_id", nullable=False)
        batch.alter_column("event_ts_utc", nullable=False)
        batch.alter_column("module", nullable=False, server_default="analytics")
        batch.alter_column("action", nullable=False, server_default="view")
        batch.alter_column("result", nullable=False, server_default="success")

        batch.drop_column("event_name")
        batch.drop_column("route")
        batch.drop_column("http_method")
        batch.drop_column("action_context")
        batch.drop_column("status_code")
        batch.drop_column("failure_class")
        batch.drop_column("source")
        batch.drop_column("metadata")

    op.create_index("ix_admin_telemetry_events_event_id", "admin_telemetry_events", ["event_id"], unique=True)
    op.create_index("ix_admin_telemetry_events_event_ts_utc", "admin_telemetry_events", ["event_ts_utc"], unique=False)
    op.create_index("ix_admin_telemetry_events_session_id", "admin_telemetry_events", ["session_id"], unique=False)
    op.create_index("ix_admin_telemetry_events_module", "admin_telemetry_events", ["module"], unique=False)
    op.create_index("ix_admin_telemetry_events_action", "admin_telemetry_events", ["action"], unique=False)
    op.create_index("ix_admin_telemetry_events_resource_type", "admin_telemetry_events", ["resource_type"], unique=False)
    op.create_index("ix_admin_telemetry_events_resource_id", "admin_telemetry_events", ["resource_id"], unique=False)
    op.create_index("ix_admin_telemetry_events_error_code", "admin_telemetry_events", ["error_code"], unique=False)

    op.create_index("ix_admin_telemetry_ts_result", "admin_telemetry_events", ["event_ts_utc", "result"], unique=False)
    op.create_index("ix_admin_telemetry_module_action", "admin_telemetry_events", ["module", "action"], unique=False)
    op.create_index("ix_admin_telemetry_role_module", "admin_telemetry_events", ["actor_role", "module"], unique=False)

    op.drop_index("ix_admin_telemetry_events_event_name", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_route", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_failure_class", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_source", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_created_result", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_route_created", table_name="admin_telemetry_events")


def downgrade() -> None:
    op.drop_index("ix_admin_telemetry_role_module", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_module_action", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_ts_result", table_name="admin_telemetry_events")

    op.drop_index("ix_admin_telemetry_events_error_code", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_resource_id", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_resource_type", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_action", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_module", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_session_id", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_event_ts_utc", table_name="admin_telemetry_events")
    op.drop_index("ix_admin_telemetry_events_event_id", table_name="admin_telemetry_events")

    with op.batch_alter_table("admin_telemetry_events") as batch:
        batch.add_column(sa.Column("event_name", sa.String(length=120), nullable=True))
        batch.add_column(sa.Column("route", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("http_method", sa.String(length=16), nullable=True))
        batch.add_column(sa.Column("action_context", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("status_code", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("failure_class", sa.String(length=120), nullable=True))
        batch.add_column(sa.Column("source", sa.String(length=50), nullable=True))
        batch.add_column(sa.Column("metadata", sa.JSON(), nullable=True))

        batch.drop_column("client_meta")
        batch.drop_column("error_code")
        batch.drop_column("after_state_hash")
        batch.drop_column("before_state_hash")
        batch.drop_column("resource_id")
        batch.drop_column("resource_type")
        batch.drop_column("action")
        batch.drop_column("module")
        batch.drop_column("session_id")
        batch.drop_column("event_ts_utc")
        batch.drop_column("event_id")

    op.create_index("ix_admin_telemetry_events_event_name", "admin_telemetry_events", ["event_name"], unique=False)
    op.create_index("ix_admin_telemetry_events_route", "admin_telemetry_events", ["route"], unique=False)
    op.create_index("ix_admin_telemetry_events_failure_class", "admin_telemetry_events", ["failure_class"], unique=False)
    op.create_index("ix_admin_telemetry_events_source", "admin_telemetry_events", ["source"], unique=False)
    op.create_index("ix_admin_telemetry_created_result", "admin_telemetry_events", ["created_at", "result"], unique=False)
    op.create_index("ix_admin_telemetry_route_created", "admin_telemetry_events", ["route", "created_at"], unique=False)
