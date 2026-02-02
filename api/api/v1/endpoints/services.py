from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from api.core.database import get_db
from api.core.tenant_context import require_tenant
from api.models.service import Service
from api.models.tenant import Tenant
from api.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate

router = APIRouter()


@router.get("/", response_model=List[ServiceResponse])
def list_services(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """List all services for the current tenant."""
    query = db.query(Service).filter(Service.tenant_id == tenant.id)
    
    if not include_inactive:
        query = query.filter(Service.is_active == True)
    
    services = query.offset(skip).limit(limit).all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Get a specific service by ID (must belong to current tenant)."""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == tenant.id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Create a new service for the current tenant."""
    service = Service(**service_in.model_dump(), tenant_id=tenant.id)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Update a service (must belong to current tenant)."""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == tenant.id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    tenant: Tenant = Depends(require_tenant),
    db = Depends(get_db)
):
    """Delete a service (soft delete by setting is_active=False, must belong to current tenant)."""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == tenant.id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    service.is_active = False
    db.commit()
    return None
