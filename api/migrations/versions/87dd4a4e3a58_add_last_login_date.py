"""add last login date

Revision ID: 87dd4a4e3a58
Revises: 583ec4067699
Create Date: 2024-09-29 18:35:50.072103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87dd4a4e3a58'
down_revision: Union[str, None] = '583ec4067699'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('last_login_date', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'last_login_date')
    # ### end Alembic commands ###