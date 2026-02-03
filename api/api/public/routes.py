"""
Public booking routes for tenant-branded booking interface.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from api.core.tenant_context import require_tenant
from api.core.database import get_db
from api.models.tenant import Tenant
from api.utils.branding import get_branding_css_vars

router = APIRouter()
templates = Jinja2Templates(directory="api/templates")


@router.get("/preview", response_class=HTMLResponse)
async def preview_branding(
    request: Request,
    tenant: Tenant = Depends(require_tenant)
):
    """
    Preview the branding for a tenant.
    Access via: /{tenant}/preview or with X-Tenant-Slug header
    """
    branding = tenant.get_branding()
    css_vars = get_branding_css_vars(branding)
    
    return templates.TemplateResponse(
        "public/preview.html",
        {
            "request": request,
            "tenant": tenant,
            "branding": branding,
            "css_vars": css_vars,
            "current_year": datetime.now().year
        }
    )


@router.get("/book", response_class=HTMLResponse)
async def booking_start(
    request: Request,
    tenant: Tenant = Depends(require_tenant)
):
    """
    Start the booking flow - Step 1: Service Selection
    """
    branding = tenant.get_branding()
    css_vars = get_branding_css_vars(branding)
    
    return templates.TemplateResponse(
        "public/book_step1_services.html",
        {
            "request": request,
            "tenant": tenant,
            "branding": branding,
            "css_vars": css_vars,
            "current_year": datetime.now().year,
            "current_step": 1,
            "steps": ["Choose Service", "Select Time", "Your Details", "Confirm"]
        }
    )
