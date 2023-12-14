"""2023-12-13_Add comments for picks

Revision ID: 6ed6f657e2de
Revises: 494bbca7206f
Create Date: 2023-12-13 23:35:01.229079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ed6f657e2de'
down_revision: Union[str, None] = '494bbca7206f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picks', sa.Column('comment', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('picks', 'comment')
    # ### end Alembic commands ###
