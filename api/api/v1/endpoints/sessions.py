from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, date, timedelta

from api.core.database import get_db
from api.core.tenant_context import get_current_tenant
from api.models.tenant import Tenant
from api.models.service import Service
from api.models.booking import Booking, BookingStatus
from api.models.availability import Availability
from api.schemas.service import ServiceResponse
from pydantic import BaseModel, Field


router = APIRouter()


class SessionResponse(BaseModel):
    id: int
    service_id: int
    service_name: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    price: Optional[float]
    max_capacity: Optional[int]
    booked_count: int
    spaces_left: Optional[int]
    is_available: bool
    is_sold_out: bool
    location_text: Optional[str]
    
    class Config:
        from_attributes = True


class SessionGroupResponse(BaseModel):
    group_label: str
    sessions: List[SessionResponse]


@router.get("/public", response_model=List[SessionResponse])
async def get_public_sessions(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    from_date: Optional[date] = Query(None, description="Start date for sessions (default: today)"),
    to_date: Optional[date] = Query(None, description="End date for sessions (default: 30 days from now)"),
    service_id: Optional[int] = Query(None, description="Filter by specific service")
):
    """
    Get upcoming sessions for a tenant with capacity information.
    Sessions are generated from services with availability windows.
    """
    if from_date is None:
        from_date = date.today()
    if to_date is None:
        to_date = from_date + timedelta(days=30)
    
    # Get active services for tenant
    services_query = db.query(Service).filter(
        Service.tenant_id == tenant.id,
        Service.is_active == True
    )
    
    if service_id:
        services_query = services_query.filter(Service.id == service_id)
    
    services = services_query.all()
    
    if not services:
        return []
    
    # Get availability windows
    availability_windows = db.query(Availability).filter(
        Availability.tenant_id == tenant.id
    ).all()
    
    if not availability_windows:
        return []
    
    # Generate sessions
    sessions = []
    current_date = from_date
    
    while current_date <= to_date:
        day_of_week = current_date.weekday()
        
        # Find availability for this day
        day_availability = [av for av in availability_windows if av.day_of_week == day_of_week]
        
        for availability in day_availability:
            for service in services:
                # Create session at availability start time
                session_start = datetime.combine(current_date, availability.start_time)
                session_end = session_start + timedelta(minutes=service.duration_minutes)
                
                # Skip if session end exceeds availability window
                if session_end.time() > availability.end_time:
                    continue
                
                # Skip past sessions
                if session_start < datetime.now():
                    continue
                
                # Count bookings for this session
                booked_count = db.query(func.count(Booking.id)).filter(
                    and_(
                        Booking.service_id == service.id,
                        Booking.start_time == session_start,
                        Booking.status.in_([BookingStatus.CONFIRMED])
                    )
                ).scalar() or 0
                
                # Calculate availability
                max_capacity = service.max_capacity
                spaces_left = None
                is_sold_out = False
                is_available = True
                
                if max_capacity is not None:
                    spaces_left = max_capacity - booked_count
                    is_sold_out = spaces_left <= 0
                    is_available = spaces_left > 0
                
                sessions.append(SessionResponse(
                    id=service.id * 1000000 + int(session_start.timestamp()),
                    service_id=service.id,
                    service_name=service.name,
                    description=service.description,
                    start_time=session_start,
                    end_time=session_end,
                    duration_minutes=service.duration_minutes,
                    price=service.price,
                    max_capacity=max_capacity,
                    booked_count=booked_count,
                    spaces_left=spaces_left,
                    is_available=is_available,
                    is_sold_out=is_sold_out,
                    location_text=tenant.location_text
                ))
        
        current_date += timedelta(days=1)
    
    # Sort by start time
    sessions.sort(key=lambda s: s.start_time)
    
    return sessions


@router.get("/public/grouped", response_model=List[SessionGroupResponse])
async def get_grouped_sessions(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    from_date: Optional[date] = Query(None, description="Start date for sessions (default: today)"),
    to_date: Optional[date] = Query(None, description="End date for sessions (default: 30 days from now)")
):
    """
    Get sessions grouped by time period (Today, This Week, Next Week, Later).
    """
    sessions = await get_public_sessions(tenant=tenant, db=db, from_date=from_date, to_date=to_date)
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    next_week_start = week_end + timedelta(days=1)
    next_week_end = next_week_start + timedelta(days=6)
    
    groups = {
        "Today": [],
        "This Week": [],
        "Next Week": [],
        "Later": []
    }
    
    for session in sessions:
        session_date = session.start_time.date()
        
        if session_date == today:
            groups["Today"].append(session)
        elif week_start <= session_date <= week_end:
            groups["This Week"].append(session)
        elif next_week_start <= session_date <= next_week_end:
            groups["Next Week"].append(session)
        else:
            groups["Later"].append(session)
    
    # Build response with non-empty groups
    result = []
    for label in ["Today", "This Week", "Next Week", "Later"]:
        if groups[label]:
            result.append(SessionGroupResponse(
                group_label=label,
                sessions=groups[label]
            ))
    
    return result
