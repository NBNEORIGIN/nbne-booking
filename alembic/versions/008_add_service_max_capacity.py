"""add service max_capacity

Revision ID: 008
Revises: 007
Create Date: 2026-02-04 09:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('services', sa.Column('max_capacity', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('services', 'max_capacity')
