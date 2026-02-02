"""create availability and blackouts tables

Revision ID: 003
Revises: 002
Create Date: 2026-02-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'availability',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_availability_id'), 'availability', ['id'], unique=False)
    op.create_index(op.f('ix_availability_tenant_id'), 'availability', ['tenant_id'], unique=False)

    op.create_table(
        'blackouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('start_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blackouts_id'), 'blackouts', ['id'], unique=False)
    op.create_index(op.f('ix_blackouts_tenant_id'), 'blackouts', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blackouts_tenant_id'), table_name='blackouts')
    op.drop_index(op.f('ix_blackouts_id'), table_name='blackouts')
    op.drop_table('blackouts')
    
    op.drop_index(op.f('ix_availability_tenant_id'), table_name='availability')
    op.create_index(op.f('ix_availability_id'), 'availability', ['id'], unique=False)
    op.drop_table('availability')
