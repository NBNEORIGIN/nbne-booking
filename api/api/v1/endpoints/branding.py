from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict

from api.core.database import get_db
from api.core.tenant_context import get_current_tenant
from api.models.tenant import Tenant
from pydantic import BaseModel


router = APIRouter()


class BrandingResponse(BaseModel):
    client_display_name: str
    logo_url: Optional[str]
    primary_color: str
    secondary_color: Optional[str]
    accent_color: Optional[str]
    booking_page_title: str
    booking_page_intro: str
    location_text: Optional[str]
    contact_email: str
    contact_phone: Optional[str]
    business_address: Optional[str]
    social_links: Dict[str, str]
    
    class Config:
        from_attributes = True


@router.get("/public", response_model=BrandingResponse)
async def get_tenant_branding(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get tenant branding configuration for public-facing pages.
    Used by frontend to apply tenant-specific styling and content.
    """
    branding = tenant.get_branding()
    
    return BrandingResponse(**branding)
