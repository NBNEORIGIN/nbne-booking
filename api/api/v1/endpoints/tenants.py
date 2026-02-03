from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from api.core.database import get_db
from api.core.permissions import require_admin_access, require_superadmin_access, check_tenant_access
from api.models.tenant import Tenant
from api.models.user import User
from api.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate

router = APIRouter()


@router.get("/", response_model=List[TenantResponse])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """List all tenants (admin only)."""
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Get a specific tenant by ID (admin only)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not check_tenant_access(current_user, tenant.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


@router.get("/slug/{slug}", response_model=TenantResponse)
def get_tenant_by_slug(
    slug: str,
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Get a specific tenant by slug (admin only)."""
    tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not check_tenant_access(current_user, tenant.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_in: TenantCreate,
    current_user: User = Depends(require_superadmin_access),
    db = Depends(get_db)
):
    """Create a new tenant (superadmin only)."""
    # Check if slug already exists
    existing = db.query(Tenant).filter(Tenant.slug == tenant_in.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists"
        )
    
    # Check if subdomain already exists (if provided)
    if tenant_in.subdomain:
        existing = db.query(Tenant).filter(Tenant.subdomain == tenant_in.subdomain).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this subdomain already exists"
            )
    
    tenant = Tenant(**tenant_in.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    tenant_in: TenantUpdate,
    current_user: User = Depends(require_admin_access),
    db = Depends(get_db)
):
    """Update a tenant (admin only)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not check_tenant_access(current_user, tenant.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    update_data = tenant_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    current_user: User = Depends(require_superadmin_access),
    db = Depends(get_db)
):
    """Delete a tenant (superadmin only - soft delete by setting is_active=False)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.is_active = False
    db.commit()
    return None
