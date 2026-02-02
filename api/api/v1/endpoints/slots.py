from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date, timedelta

from api.core.database import get_db
from api.core.tenant_context import require_tenant
from api.models.service import Service
from api.models.tenant import Tenant
from api.services.slot_generator import SlotGenerator

router = APIRouter()


@router.get("/")
def get_available_slots(
    service_id: int,
    start_date: date,
    end_date: Optional[date] = None,
    days: Optional[int] = Query(None, ge=1, le=90),
    timezone_offset: int = Query(0, ge=-12, le=14),
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """
    Get available booking slots for a service.
    
    Args:
        service_id: ID of the service
        start_date: Start date for slot generation
        end_date: End date for slot generation (optional, defaults to start_date + days)
        days: Number of days to generate slots for if end_date not provided
        timezone_offset: Timezone offset in hours
    
    Returns:
        List of available slots with start and end times
    """
    # Get service
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == tenant.id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Calculate end_date if not provided
    if not end_date:
        end_date = start_date + timedelta(days=days - 1)
    
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date"
        )
    
    # Limit date range to 90 days
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 90 days"
        )
    
    # Generate slots
    generator = SlotGenerator(db, tenant.id)
    slots = generator.generate_slots(
        service_id=service_id,
        start_date=start_date,
        end_date=end_date,
        timezone_offset=timezone_offset
    )
    
    return {
        "service_id": service.id,
        "service_name": service.name,
        "duration_minutes": service.duration_minutes,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "slots": slots,
        "total_slots": len(slots)
    }
