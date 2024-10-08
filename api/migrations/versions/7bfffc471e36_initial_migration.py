"""Initial migration

Revision ID: 7bfffc471e36
Revises: 
Create Date: 2024-08-11 22:39:28.120704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bfffc471e36'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('mail', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('derivedKeySalt', sa.String(length=256), nullable=False),
    sa.Column('isVerified', sa.Boolean(), nullable=False),
    sa.Column('passphraseSalt', sa.String(length=256), nullable=False),
    sa.Column('createdAt', sa.String(length=256), nullable=False),
    sa.Column('role', sa.String(length=256), nullable=False),
    sa.Column('isBlocked', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ZKE_encryption_key',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ZKE_key', sa.String(length=256), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token_hashed', sa.Text(), nullable=False),
    sa.Column('token_expiration', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('email_verification_token',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=256), nullable=False),
    sa.Column('expiration', sa.String(length=256), nullable=False),
    sa.Column('failed_attempts', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('google_drive_integration',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('isEnabled', sa.Boolean(), nullable=False),
    sa.Column('lastBackupCleanDate', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oauth_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('enc_credentials', sa.Text(), nullable=False),
    sa.Column('cipher_nonce', sa.Text(), nullable=False),
    sa.Column('cipher_tag', sa.Text(), nullable=False),
    sa.Column('expires_at', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('preferences',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('favicon_preview_policy', sa.String(length=256), nullable=True),
    sa.Column('derivation_iteration', sa.Integer(), nullable=True),
    sa.Column('minimum_backup_kept', sa.Integer(), nullable=True),
    sa.Column('backup_lifetime', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rate_limiting',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('action_type', sa.String(length=256), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('totp_secret_enc',
    sa.Column('uuid', sa.String(length=256), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('secret_enc', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('totp_secret_enc')
    op.drop_table('rate_limiting')
    op.drop_table('preferences')
    op.drop_table('oauth_tokens')
    op.drop_table('google_drive_integration')
    op.drop_table('email_verification_token')
    op.drop_table('admin_tokens')
    op.drop_table('ZKE_encryption_key')
    op.drop_table('User')
    # ### end Alembic commands ###
