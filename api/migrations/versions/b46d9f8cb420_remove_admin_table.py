"""Remove admin table

Revision ID: b46d9f8cb420
Revises: 0ba349cab310
Create Date: 2024-11-17 22:50:08.205272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b46d9f8cb420'
down_revision: Union[str, None] = '0ba349cab310'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin_tokens')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_tokens',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('token_hashed', mysql.TEXT(), nullable=False),
    sa.Column('token_expiration', mysql.VARCHAR(length=256), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='admin_tokens_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='latin1_swedish_ci',
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###