# alembic/versions/0002_add_users_role_index.py
"""add index on users.role

Revision ID: 0002_add_users_role_index
Revises: 0001_create_auth_tables
Create Date: 2025-12-01 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_users_role_index'
down_revision = '0001_create_auth_tables'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index("ix_users_role", "users", ["role"])

def downgrade():
    op.drop_index("ix_users_role", table_name="users")
