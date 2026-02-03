from fastapi import APIRouter, Request, Depends, Query, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_
from datetime import datetime, date
from typing import Optional
import csv
import io

from api.core.database import get_db
from api.core.permissions import require_tenant_access, require_admin_access
from api.models.booking import Booking, BookingStatus
from api.models.service import Service
from api.models.tenant import Tenant
from api.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="api/templates")


@router.get("/bookings", response_class=HTMLResponse)
def admin_bookings_view(
    request: Request,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[BookingStatus] = Query(None),
    service_id: Optional[int] = Query(None),
    tenant: Tenant = Depends(require_tenant_access),
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Admin view for bookings with filters."""
    
    # Build query
    query = db.query(Booking).filter(Booking.tenant_id == tenant.id)
    
    # Apply filters
    if start_date:
        query = query.filter(Booking.start_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Booking.start_time <= datetime.combine(end_date, datetime.max.time()))
    if status:
        query = query.filter(Booking.status == status)
    if service_id:
        query = query.filter(Booking.service_id == service_id)
    
    # Order by start time descending (most recent first)
    bookings = query.order_by(Booking.start_time.desc()).all()
    
    # Get all services for filter dropdown
    services = db.query(Service).filter(
        Service.tenant_id == tenant.id,
        Service.is_active == True
    ).all()
    
    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "tenant": tenant,
        "bookings": bookings,
        "services": services,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "status": status.value if status else None,
            "service_id": service_id
        },
        "active_page": "bookings"
    })


@router.get("/bookings/export")
def export_bookings_csv(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[BookingStatus] = Query(None),
    service_id: Optional[int] = Query(None),
    tenant: Tenant = Depends(require_tenant_access),
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Export bookings to CSV with same filters as view."""
    
    # Build query (same as view)
    query = db.query(Booking).filter(Booking.tenant_id == tenant.id)
    
    if start_date:
        query = query.filter(Booking.start_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Booking.start_time <= datetime.combine(end_date, datetime.max.time()))
    if status:
        query = query.filter(Booking.status == status)
    if service_id:
        query = query.filter(Booking.service_id == service_id)
    
    bookings = query.order_by(Booking.start_time.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date',
        'Start Time',
        'End Time',
        'Customer Name',
        'Customer Email',
        'Customer Phone',
        'Service',
        'Duration (min)',
        'Status',
        'Notes',
        'Created At'
    ])
    
    # Write data
    for booking in bookings:
        status_value = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
        writer.writerow([
            booking.start_time.strftime('%Y-%m-%d'),
            booking.start_time.strftime('%H:%M'),
            booking.end_time.strftime('%H:%M'),
            booking.customer_name,
            booking.customer_email,
            booking.customer_phone or '',
            booking.service.name,
            booking.service.duration_minutes,
            status_value.upper(),
            booking.notes or '',
            booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Prepare response
    output.seek(0)
    filename = f"bookings_{tenant.slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/services", response_class=HTMLResponse)
def admin_services_view(
    request: Request,
    tenant: Tenant = Depends(require_tenant_access),
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Admin view for services."""
    services = db.query(Service).filter(Service.tenant_id == tenant.id).all()
    
    return templates.TemplateResponse("services.html", {
        "request": request,
        "tenant": tenant,
        "services": services,
        "active_page": "services"
    })


@router.get("/availability", response_class=HTMLResponse)
def admin_availability_view(
    request: Request,
    tenant: Tenant = Depends(require_tenant_access),
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Admin view for availability."""
    from api.models.availability import Availability
    
    availability = db.query(Availability).filter(Availability.tenant_id == tenant.id).all()
    
    return templates.TemplateResponse("availability.html", {
        "request": request,
        "tenant": tenant,
        "availability": availability,
        "blackouts": [],
        "active_page": "availability"
    })


@router.get("/branding", response_class=HTMLResponse)
def admin_branding_view(
    request: Request,
    tenant: Tenant = Depends(require_tenant_access),
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Admin view for branding settings."""
    return templates.TemplateResponse("admin/branding.html", {
        "request": request,
        "tenant": tenant,
        "active_page": "branding"
    })
