from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from datetime import datetime

from api.core.database import get_db
from api.core.tenant_context import require_tenant
from api.models.availability import Blackout
from api.models.tenant import Tenant
from api.schemas.availability import BlackoutCreate, BlackoutResponse, BlackoutUpdate

router = APIRouter()


@router.get("/", response_model=List[BlackoutResponse])
def list_blackouts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """List all blackouts for the current tenant."""
    query = db.query(Blackout).filter(Blackout.tenant_id == tenant.id)
    
    if start_date:
        query = query.filter(Blackout.end_datetime >= start_date)
    
    if end_date:
        query = query.filter(Blackout.start_datetime <= end_date)
    
    blackouts = query.order_by(Blackout.start_datetime).offset(skip).limit(limit).all()
    return blackouts


@router.get("/{blackout_id}", response_model=BlackoutResponse)
def get_blackout(
    blackout_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Get a specific blackout by ID (must belong to current tenant)."""
    blackout = db.query(Blackout).filter(
        Blackout.id == blackout_id,
        Blackout.tenant_id == tenant.id
    ).first()
    
    if not blackout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blackout not found"
        )
    
    return blackout


@router.post("/", response_model=BlackoutResponse, status_code=status.HTTP_201_CREATED)
def create_blackout(
    blackout_in: BlackoutCreate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Create a new blackout for the current tenant."""
    blackout = Blackout(**blackout_in.model_dump(), tenant_id=tenant.id)
    db.add(blackout)
    db.commit()
    db.refresh(blackout)
    return blackout


@router.patch("/{blackout_id}", response_model=BlackoutResponse)
def update_blackout(
    blackout_id: int,
    blackout_in: BlackoutUpdate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Update a blackout (must belong to current tenant)."""
    blackout = db.query(Blackout).filter(
        Blackout.id == blackout_id,
        Blackout.tenant_id == tenant.id
    ).first()
    
    if not blackout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blackout not found"
        )
    
    update_data = blackout_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(blackout, field, value)
    
    db.commit()
    db.refresh(blackout)
    return blackout


@router.delete("/{blackout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blackout(
    blackout_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Delete a blackout (must belong to current tenant)."""
    blackout = db.query(Blackout).filter(
        Blackout.id == blackout_id,
        Blackout.tenant_id == tenant.id
    ).first()
    
    if not blackout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blackout not found"
        )
    
    db.delete(blackout)
    db.commit()
    return None
