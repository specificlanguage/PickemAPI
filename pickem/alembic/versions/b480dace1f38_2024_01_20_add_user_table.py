"""2024-01-20_Add user table

Revision ID: b480dace1f38
Revises: 4eecfe1ccadb
Create Date: 2024-01-20 16:59:57.266675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b480dace1f38'
down_revision: Union[str, None] = '4eecfe1ccadb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('uid', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('imageURL', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_index(op.f('ix_users_uid'), 'users', ['uid'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_uid'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
