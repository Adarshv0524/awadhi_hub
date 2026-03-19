"""create audit_logs table

Revision ID: 0011_audit_logs
Revises: 0010_system_settings
Create Date: 2025-12-12 00:00:00.000001
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_audit_logs"
down_revision = "0010_system_settings"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.Integer(), nullable=True),  # CHANGED
        sa.Column("before", sa.JSON(), nullable=True),
        sa.Column("after", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_audit_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_resourcetype_id", "audit_logs", ["resource_type", "resource_id"])
    op.create_index("ix_audit_actor", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_action", "audit_logs", ["action"])


def downgrade():
    op.drop_index("ix_audit_action", table_name="audit_logs")
    op.drop_index("ix_audit_actor", table_name="audit_logs")
    op.drop_index("ix_audit_resourcetype_id", table_name="audit_logs")
    op.drop_index("ix_audit_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
