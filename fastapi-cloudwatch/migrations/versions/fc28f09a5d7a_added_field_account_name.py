"""added field account name

Revision ID: fc28f09a5d7a
Revises: e7b79fd8894c
Create Date: 2023-02-26 08:41:58.292325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc28f09a5d7a'
down_revision = 'e7b79fd8894c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('r_d_s_monitor_cache', sa.Column('account_name', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('r_d_s_monitor_cache', 'account_name')
    # ### end Alembic commands ###