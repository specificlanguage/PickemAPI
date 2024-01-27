"""2024-01-27_Modify user preference table field names

Revision ID: 8591270cf681
Revises: 63f204419699
Create Date: 2024-01-27 13:10:15.761894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8591270cf681'
down_revision: Union[str, None] = '63f204419699'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('favoriteTeam_id', sa.Integer(), nullable=True))
    op.drop_constraint('users_favoriteTeam_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'teams', ['favoriteTeam_id'], ['id'])
    op.drop_column('users', 'favoriteTeam')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('favoriteTeam', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key('users_favoriteTeam_fkey', 'users', 'teams', ['favoriteTeam'], ['id'])
    op.drop_column('users', 'favoriteTeam_id')
    # ### end Alembic commands ###