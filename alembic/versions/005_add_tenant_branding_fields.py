"""add_tenant_branding_fields

Revision ID: 005
Revises: 004
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add branding columns to tenants table
    op.add_column('tenants', sa.Column('client_display_name', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('logo_url', sa.String(length=500), nullable=True))
    op.add_column('tenants', sa.Column('primary_color', sa.String(length=7), nullable=False, server_default='#2196F3'))
    op.add_column('tenants', sa.Column('secondary_color', sa.String(length=7), nullable=True))
    op.add_column('tenants', sa.Column('accent_color', sa.String(length=7), nullable=True))
    op.add_column('tenants', sa.Column('booking_page_title', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('booking_page_intro', sa.Text(), nullable=True))
    op.add_column('tenants', sa.Column('location_text', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('contact_email', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('contact_phone', sa.String(length=50), nullable=True))
    op.add_column('tenants', sa.Column('business_address', sa.Text(), nullable=True))
    op.add_column('tenants', sa.Column('social_links', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove branding columns from tenants table
    op.drop_column('tenants', 'social_links')
    op.drop_column('tenants', 'business_address')
    op.drop_column('tenants', 'contact_phone')
    op.drop_column('tenants', 'contact_email')
    op.drop_column('tenants', 'location_text')
    op.drop_column('tenants', 'booking_page_intro')
    op.drop_column('tenants', 'booking_page_title')
    op.drop_column('tenants', 'accent_color')
    op.add_column('tenants', 'secondary_color')
    op.drop_column('tenants', 'primary_color')
    op.drop_column('tenants', 'logo_url')
    op.drop_column('tenants', 'client_display_name')
