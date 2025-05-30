"""remove donor_phone and update donor fields

Revision ID: 921549f59624
Revises: 
Create Date: 2025-04-22 16:29:31.165686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '921549f59624'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.drop_column('donor_phone')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('donor_phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
