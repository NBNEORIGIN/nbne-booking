"""
Public booking routes for tenant-branded booking interface.
"""
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.core.tenant_context import require_tenant
from api.core.database import get_db
from api.models.tenant import Tenant
from api.models.service import Service
from api.models.booking import Booking
from api.utils.branding import get_branding_css_vars
from api.services.slot_generator import SlotGenerator

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
async def booking_step1_services(
    request: Request,
    tenant: Tenant = Depends(require_tenant),
    db: Session = Depends(get_db)
):
    """
    Step 1: Service Selection
    """
    branding = tenant.get_branding()
    css_vars = get_branding_css_vars(branding)
    
    # Get active services for this tenant
    services = db.query(Service).filter(
        Service.tenant_id == tenant.id,
        Service.is_active == True
    ).all()
    
    return templates.TemplateResponse(
        "public/book_step1_services.html",
        {
            "request": request,
            "tenant": tenant,
            "branding": branding,
            "css_vars": css_vars,
            "current_year": datetime.now().year,
            "current_step": 1,
            "steps": ["Choose Service", "Select Time", "Your Details", "Confirm"],
            "services": services
        }
    )


@router.get("/book/slots", response_class=HTMLResponse)
async def booking_step2_slots(
    request: Request,
    service_id: int = Query(...),
    date: str = Query(None),
    tenant: Tenant = Depends(require_tenant),
    db: Session = Depends(get_db)
):
    """
    Step 2: Time Slot Selection
    """
    branding = tenant.get_branding()
    css_vars = get_branding_css_vars(branding)
    
    # Get service
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == tenant.id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Generate next 7 days for date selection
    today = datetime.now().date()
    available_dates = []
    for i in range(7):
        date_obj = today + timedelta(days=i)
        available_dates.append({
            "date": date_obj.isoformat(),
            "day_name": date_obj.strftime("%a"),
            "day": date_obj.strftime("%d"),
            "month": date_obj.strftime("%b")
        })
    
    # Get slots for selected date
    slots = []
    selected_date = date or today.isoformat()
    
    if date:
        slot_generator = SlotGenerator(db)
        start_date = datetime.fromisoformat(selected_date)
        end_date = start_date + timedelta(days=1)
        
        available_slots = slot_generator.generate_slots(
            service_id=service_id,
            start_date=start_date,
            end_date=end_date,
            tenant_id=tenant.id
        )
        
        slots = [{
            "start_time": slot["start_time"].isoformat(),
            "time_display": slot["start_time"].strftime("%I:%M %p"),
            "available": True
        } for slot in available_slots]
    
    return templates.TemplateResponse(
        "public/book_step2_slots.html",
        {
            "request": request,
            "tenant": tenant,
            "branding": branding,
            "css_vars": css_vars,
            "current_year": datetime.now().year,
            "current_step": 2,
            "steps": ["Choose Service", "Select Time", "Your Details", "Confirm"],
            "service": service,
            "available_dates": available_dates,
            "selected_date": selected_date,
            "slots": slots
        }
    )


@router.get("/book/details", response_class=HTMLResponse)
async def booking_step3_details(
    request: Request,
    service_id: int = Query(...),
    date: str = Query(...),
    time: str = Query(...),
    tenant: Tenant = Depends(require_tenant),
    db: Session = Depends(get_db)
):
    """
    Step 3: Customer Details
    """
    branding = tenant.get_branding()
    css_vars = get_branding_css_vars(branding)
    
    # Get service
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == tenant.id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Parse booking datetime
    booking_datetime = datetime.fromisoformat(f"{date}T{time}")
    
    return templates.TemplateResponse(
        "public/book_step3_details.html",
        {
            "request": request,
            "tenant": tenant,
            "branding": branding,
            "css_vars": css_vars,
            "current_year": datetime.now().year,
            "current_step": 3,
            "steps": ["Choose Service", "Select Time", "Your Details", "Confirm"],
            "service": service,
            "booking_date": booking_datetime.strftime("%A, %B %d, %Y"),
            "booking_time": booking_datetime.strftime("%I:%M %p")
        }
    )


@router.get("/book/confirmation", response_class=HTMLResponse)
async def booking_step4_confirmation(
    request: Request,
    booking_id: int = Query(...),
    tenant: Tenant = Depends(require_tenant),
    db: Session = Depends(get_db)
):
    """
    Step 4: Booking Confirmation
    """
    branding = tenant.get_branding()
    css_vars = get_branding_css_vars(branding)
    
    # Get booking with service
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.tenant_id == tenant.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get service details
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    booking.service = service
    
    return templates.TemplateResponse(
        "public/book_step4_confirmation.html",
        {
            "request": request,
            "tenant": tenant,
            "branding": branding,
            "css_vars": css_vars,
            "current_year": datetime.now().year,
            "steps": ["Choose Service", "Select Time", "Your Details", "Confirm"],
            "booking": booking
        }
    )
