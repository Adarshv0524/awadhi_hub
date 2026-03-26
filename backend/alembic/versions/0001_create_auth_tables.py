"""create auth tables

Revision ID: 0001_create_auth_tables
Revises: 
Create Date: 2025-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_auth_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='registered'),
        sa.Column('permissions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('permission_scopes', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_banned', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),  # CHANGED
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('token', name='uq_refresh_token')
    )
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'])
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])

    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),  # CHANGED
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),  # CHANGED
        sa.Column('raw_profile', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user')
    )
    op.create_index('ix_oauth_provider_user', 'oauth_accounts', ['provider', 'provider_user_id'])

def downgrade():
    op.drop_index('ix_oauth_provider_user', table_name='oauth_accounts')
    op.drop_table('oauth_accounts')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
