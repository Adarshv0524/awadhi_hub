"""add user profile fields name and bio

Revision ID: 0023_add_user_profile_fields
Revises: 0022_email_verification
Create Date: 2026-03-29 14:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0023_add_user_profile_fields"
down_revision = "0022_email_verification"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("users", "bio")
    op.drop_column("users", "name")
