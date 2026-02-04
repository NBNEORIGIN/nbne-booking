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
    db: Session = Depends(get_db),
    tenant: Optional[Tenant] = Depends(get_current_tenant)
):
    """
    Get tenant branding configuration for public-facing pages.
    Used by frontend to apply tenant-specific styling and content.
    Falls back to first active tenant if none specified.
    """
    # If no tenant resolved, use the first active tenant
    if not tenant:
        tenant = db.query(Tenant).filter(Tenant.is_active == True).first()
        if not tenant:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="No active tenant found")
    
    branding = tenant.get_branding()
    
    return BrandingResponse(**branding)
