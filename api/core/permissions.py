from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.auth import get_current_user
from api.core.tenant_context import get_tenant_context
from api.models.user import User, UserRole
from api.models.tenant import Tenant


def check_tenant_access(user: User, tenant_id: int) -> bool:
    """
    Check if user has access to a specific tenant.
    
    Rules:
    - SUPERADMIN: Access to all tenants
    - STAFF: Access to all tenants
    - CLIENT: Access only to their assigned tenant
    """
    if user.role == UserRole.SUPERADMIN:
        return True
    
    if user.role == UserRole.STAFF:
        return True
    
    if user.role == UserRole.CLIENT:
        return user.tenant_id == tenant_id
    
    return False


async def require_tenant_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Require authenticated user with access to current tenant context.
    
    This combines authentication + tenant resolution + access check.
    Use this for all tenant-scoped endpoints.
    """
    tenant_context = get_tenant_context()
    
    if not tenant_context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context required (X-Tenant-Slug header or subdomain)"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_context.id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not check_tenant_access(current_user, tenant.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    return tenant


def verify_resource_ownership(
    resource_tenant_id: int,
    user: User,
    resource_type: str = "resource"
) -> None:
    """
    Verify that a user has access to a resource belonging to a specific tenant.
    
    Raises HTTPException if access is denied.
    """
    if not check_tenant_access(user, resource_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type.capitalize()} not found"
        )


def require_admin_access(current_user: User = Depends(get_current_user)) -> User:
    """
    Require SUPERADMIN or STAFF role.
    Use for admin-only endpoints.
    """
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_superadmin_access(current_user: User = Depends(get_current_user)) -> User:
    """
    Require SUPERADMIN role only.
    Use for superadmin-only endpoints (tenant management, etc.).
    """
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user
