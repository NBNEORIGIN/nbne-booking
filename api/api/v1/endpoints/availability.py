from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from api.core.database import get_db
from api.core.tenant_context import require_tenant
from api.models.availability import Availability
from api.models.tenant import Tenant
from api.schemas.availability import AvailabilityCreate, AvailabilityResponse, AvailabilityUpdate

router = APIRouter()


@router.get("/", response_model=List[AvailabilityResponse])
def list_availability(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """List all availability windows for the current tenant."""
    availability = db.query(Availability).filter(
        Availability.tenant_id == tenant.id
    ).order_by(Availability.day_of_week, Availability.start_time).offset(skip).limit(limit).all()
    return availability


@router.get("/{availability_id}", response_model=AvailabilityResponse)
def get_availability(
    availability_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Get a specific availability window by ID (must belong to current tenant)."""
    availability = db.query(Availability).filter(
        Availability.id == availability_id,
        Availability.tenant_id == tenant.id
    ).first()
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability window not found"
        )
    
    return availability


@router.post("/", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability_in: AvailabilityCreate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Create a new availability window for the current tenant."""
    availability = Availability(**availability_in.model_dump(), tenant_id=tenant.id)
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability


@router.patch("/{availability_id}", response_model=AvailabilityResponse)
def update_availability(
    availability_id: int,
    availability_in: AvailabilityUpdate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Update an availability window (must belong to current tenant)."""
    availability = db.query(Availability).filter(
        Availability.id == availability_id,
        Availability.tenant_id == tenant.id
    ).first()
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability window not found"
        )
    
    update_data = availability_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(availability, field, value)
    
    db.commit()
    db.refresh(availability)
    return availability


@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    availability_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Delete an availability window (must belong to current tenant)."""
    availability = db.query(Availability).filter(
        Availability.id == availability_id,
        Availability.tenant_id == tenant.id
    ).first()
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability window not found"
        )
    
    db.delete(availability)
    db.commit()
    return None
