"""2024-01-27_Modify user preference table field constraints

Revision ID: 6b13cf211689
Revises: 8591270cf681
Create Date: 2024-01-27 14:51:17.083512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b13cf211689'
down_revision: Union[str, None] = '8591270cf681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_id', table_name='users')
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    # ### end Alembic commands ###
