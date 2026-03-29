"""Add email verification support - email_verified field and EmailVerificationToken table

Revision ID: 0022
Revises: 0021
Create Date: 2026-03-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0022_email_verification"
down_revision = "0021_ai_governance_and_retention"
branch_labels = None
depends_on = None


def upgrade():
    # Add email_verified and pending_email columns to users table
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('users', sa.Column('pending_email', sa.String(255), nullable=True))
    
    # Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_to_verify', sa.String(255), nullable=False),
        sa.Column('otp', sa.String(6), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index(op.f('ix_email_verification_tokens_user_id'), 'email_verification_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_email_verification_tokens_token'), 'email_verification_tokens', ['token'], unique=False)


def downgrade():
    # Drop indexes and table
    op.drop_index(op.f('ix_email_verification_tokens_token'), table_name='email_verification_tokens')
    op.drop_index(op.f('ix_email_verification_tokens_user_id'), table_name='email_verification_tokens')
    op.drop_table('email_verification_tokens')
    
    # Remove columns from users table
    op.drop_column('users', 'pending_email')
    op.drop_column('users', 'email_verified')
