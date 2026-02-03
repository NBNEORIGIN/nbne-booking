from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy import and_, or_
from datetime import datetime

from api.core.database import get_db
from api.core.permissions import require_tenant_access, verify_resource_ownership
from api.core.auth import get_current_user
from api.core.config import settings
from api.models.booking import Booking, BookingStatus
from api.models.service import Service
from api.models.tenant import Tenant
from api.models.user import User
from api.schemas.booking import BookingCreate, BookingResponse, BookingUpdate, BookingListItem
from api.services.slot_generator import SlotGenerator
from api.services.email_service import email_service

router = APIRouter()


@router.get("/", response_model=List[BookingListItem])
def list_bookings(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status: BookingStatus = Query(None),
    service_id: int = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    tenant: Tenant = Depends(require_tenant_access),
    db = Depends(get_db)
):
    """List all bookings for the current tenant with optional filters (authenticated)."""
    query = db.query(Booking).filter(Booking.tenant_id == tenant.id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if service_id:
        query = query.filter(Booking.service_id == service_id)
    
    if start_date:
        query = query.filter(Booking.start_time >= start_date)
    
    if end_date:
        query = query.filter(Booking.start_time <= end_date)
    
    bookings = query.order_by(Booking.start_time.desc()).offset(skip).limit(limit).all()
    
    # Enrich with service names
    result = []
    for booking in bookings:
        service = db.query(Service).filter(Service.id == booking.service_id).first()
        result.append({
            "id": booking.id,
            "service_id": booking.service_id,
            "service_name": service.name if service else "Unknown",
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "customer_phone": booking.customer_phone,
            "status": booking.status,
            "created_at": booking.created_at
        })
    
    return result


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    tenant: Tenant = Depends(require_tenant_access),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific booking by ID (authenticated, must belong to current tenant)."""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.tenant_id == tenant.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify resource ownership
    verify_resource_ownership(booking.tenant_id, current_user, "booking")
    
    # Enrich with service name
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    booking_dict = {
        "id": booking.id,
        "tenant_id": booking.tenant_id,
        "service_id": booking.service_id,
        "service_name": service.name if service else None,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "customer_phone": booking.customer_phone,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return booking_dict


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    tenant: Tenant = Depends(require_tenant_access),
    db = Depends(get_db)
):
    """
    Create a new booking with double-booking prevention.
    Uses database transaction isolation to prevent race conditions.
    """
    # Verify service exists and belongs to tenant
    service = db.query(Service).filter(
        Service.id == booking_in.service_id,
        Service.tenant_id == tenant.id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Validate booking times
    if booking_in.end_time <= booking_in.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time"
        )
    
    # Verify slot is available (checks availability windows and blackouts)
    generator = SlotGenerator(db, tenant.id)
    if not generator.is_slot_available(service.id, booking_in.start_time, booking_in.end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected time slot is not available"
        )
    
    # Check for overlapping bookings (double-booking prevention)
    # Use FOR UPDATE to lock rows and prevent race conditions
    overlapping = db.query(Booking).filter(
        Booking.tenant_id == tenant.id,
        Booking.service_id == booking_in.service_id,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
        or_(
            # New booking starts during existing booking
            and_(
                Booking.start_time <= booking_in.start_time,
                Booking.end_time > booking_in.start_time
            ),
            # New booking ends during existing booking
            and_(
                Booking.start_time < booking_in.end_time,
                Booking.end_time >= booking_in.end_time
            ),
            # New booking completely contains existing booking
            and_(
                Booking.start_time >= booking_in.start_time,
                Booking.end_time <= booking_in.end_time
            )
        )
    ).with_for_update().first()
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked"
        )
    
    # Create booking
    booking = Booking(
        **booking_in.model_dump(),
        tenant_id=tenant.id,
        status=BookingStatus.CONFIRMED
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    # Send email notifications (non-blocking - don't fail booking if email fails)
    if settings.ENABLE_EMAIL_NOTIFICATIONS:
        try:
            # Send confirmation to customer
            email_service.send_booking_confirmation_to_customer(
                customer_email=booking.customer_email,
                customer_name=booking.customer_name,
                service_name=service.name,
                start_time=booking.start_time,
                end_time=booking.end_time,
                tenant_name=tenant.name,
                tenant_email=tenant.email,
                tenant_phone=tenant.phone,
                notes=booking.notes
            )
            
            # Send notification to business
            email_service.send_booking_notification_to_business(
                business_email=tenant.email,
                business_name=tenant.name,
                customer_name=booking.customer_name,
                customer_email=booking.customer_email,
                customer_phone=booking.customer_phone,
                service_name=service.name,
                start_time=booking.start_time,
                end_time=booking.end_time,
                notes=booking.notes
            )
        except Exception as e:
            # Log error but don't fail the booking
            print(f"Email notification failed: {str(e)}")
    
    # Return with service name
    return {
        "id": booking.id,
        "tenant_id": booking.tenant_id,
        "service_id": booking.service_id,
        "service_name": service.name,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "customer_phone": booking.customer_phone,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }


@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Update a booking (must belong to current tenant)."""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.tenant_id == tenant.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    update_data = booking_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    # Return with service name
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    return {
        "id": booking.id,
        "tenant_id": booking.tenant_id,
        "service_id": booking.service_id,
        "service_name": service.name if service else None,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "customer_phone": booking.customer_phone,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Cancel a booking (sets status to CANCELLED, must belong to current tenant)."""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.tenant_id == tenant.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking.status = BookingStatus.CANCELLED
    db.commit()
    return None
