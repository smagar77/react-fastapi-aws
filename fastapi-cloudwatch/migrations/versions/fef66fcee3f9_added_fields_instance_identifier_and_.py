"""added fields instance_identifier and instance_status

Revision ID: fef66fcee3f9
Revises: fc28f09a5d7a
Create Date: 2023-02-26 12:46:14.206414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fef66fcee3f9'
down_revision = 'fc28f09a5d7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('r_d_s_monitor_cache', sa.Column('instance_identifier', sa.String(length=10), nullable=True))
    op.add_column('r_d_s_monitor_cache', sa.Column('instance_status', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('r_d_s_monitor_cache', 'instance_status')
    op.drop_column('r_d_s_monitor_cache', 'instance_identifier')
    # ### end Alembic commands ###
