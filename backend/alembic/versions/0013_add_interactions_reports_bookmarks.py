"""add interactions, share_logs, reports and bookmarks_count to engagement_kpis
Revision ID: 0013_add_interactions_reports_bookmarks
Revises: 0012_module16_dictionary_idiom_article
Create Date: 2025-12-13 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
revision = "0013_add_interactions_reports_bookmarks"
down_revision = "0012_module16_dictionary_idiom_article"
branch_labels = None
depends_on = None
def upgrade():
    # add bookmarks_count to engagement_kpis
    op.add_column("engagement_kpis", sa.Column("bookmarks_count", sa.Integer(), nullable=False, server_default="0"))
    # create user_interactions
    op.create_table(
        "user_interactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("interaction_type", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("interaction_metadata", sa.JSON(), nullable=True),  # UPDATED: renamed from metadata
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "content_type", "content_id", "interaction_type", name="uq_user_interaction"),
    )
    op.create_index("ix_user_interactions_user_id", "user_interactions", ["user_id"])
    op.create_index("ix_user_interactions_content_type", "user_interactions", ["content_type"])
    op.create_index("ix_user_interactions_content_id", "user_interactions", ["content_id"])
    op.create_index("ix_user_interaction_user_content", "user_interactions", ["user_id", "content_type", "content_id"])
    # create share_logs
    op.create_table(
        "share_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("share_metadata", sa.JSON(), nullable=True),  # UPDATED: renamed from metadata
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_share_logs_user_id", "share_logs", ["user_id"])
    op.create_index("ix_share_logs_content_type", "share_logs", ["content_type"])
    op.create_index("ix_share_logs_content_id", "share_logs", ["content_id"])
    op.create_index("ix_share_logs_content", "share_logs", ["content_type", "content_id"])
    # create reports
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("report_metadata", sa.JSON(), nullable=True),  # UPDATED: renamed from metadata
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_reports_user_id", "reports", ["user_id"])
    op.create_index("ix_reports_content_type", "reports", ["content_type"])
    op.create_index("ix_reports_content_id", "reports", ["content_id"])
    op.create_index("ix_reports_content", "reports", ["content_type", "content_id"])
def downgrade():
    op.drop_index("ix_reports_content", table_name="reports")
    op.drop_index("ix_reports_content_id", table_name="reports")
    op.drop_index("ix_reports_content_type", table_name="reports")
    op.drop_index("ix_reports_user_id", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_share_logs_content", table_name="share_logs")
    op.drop_index("ix_share_logs_content_id", table_name="share_logs")
    op.drop_index("ix_share_logs_content_type", table_name="share_logs")
    op.drop_index("ix_share_logs_user_id", table_name="share_logs")
    op.drop_table("share_logs")
    op.drop_index("ix_user_interaction_user_content", table_name="user_interactions")
    op.drop_index("ix_user_interactions_content_id", table_name="user_interactions")
    op.drop_index("ix_user_interactions_content_type", table_name="user_interactions")
    op.drop_index("ix_user_interactions_user_id", table_name="user_interactions")
    op.drop_table("user_interactions")
    op.drop_column("engagement_kpis", "bookmarks_count")