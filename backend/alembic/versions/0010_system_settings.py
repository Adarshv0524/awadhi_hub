"""create system_settings table

Revision ID: 0010_system_settings
Revises: 0009_rate_limit_counters
Create Date: 2025-12-11 00:00:00.000010
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0010_system_settings"
down_revision = "0009_rate_limit_counters"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(255), primary_key=True, nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_system_settings_key", "system_settings", ["key"])


def downgrade():
    op.drop_index("ix_system_settings_key", table_name="system_settings")
    op.drop_table("system_settings")
