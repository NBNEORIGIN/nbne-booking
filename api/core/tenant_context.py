from contextvars import ContextVar
from typing import Optional
from fastapi import Request, HTTPException, status, Depends

from api.core.database import get_db
from api.models.tenant import Tenant

_tenant_context: ContextVar[Optional[Tenant]] = ContextVar('tenant_context', default=None)


def get_current_tenant() -> Optional[Tenant]:
    """Get the current tenant from context."""
    return _tenant_context.get()


def set_current_tenant(tenant: Optional[Tenant]) -> None:
    """Set the current tenant in context."""
    _tenant_context.set(tenant)


def resolve_tenant_from_request(request: Request, db) -> Optional[Tenant]:
    """
    Resolve tenant from request.
    Priority:
    1. Subdomain (e.g., client1.nbnebookings.co.uk)
    2. Slug in path (e.g., /t/client1/...)
    3. X-Tenant-Slug header (for API clients)
    """
    tenant = None
    
    # Try subdomain first
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        if subdomain not in ["localhost", "127", "www", "api"]:
            tenant = db.query(Tenant).filter(
                Tenant.subdomain == subdomain,
                Tenant.is_active == True
            ).first()
    
    # Try X-Tenant-Slug header
    if not tenant:
        tenant_slug = request.headers.get("x-tenant-slug")
        if tenant_slug:
            tenant = db.query(Tenant).filter(
                Tenant.slug == tenant_slug,
                Tenant.is_active == True
            ).first()
    
    # Try path parameter (will be set by route dependencies)
    if not tenant and hasattr(request.state, "tenant_slug"):
        tenant = db.query(Tenant).filter(
            Tenant.slug == request.state.tenant_slug,
            Tenant.is_active == True
        ).first()
    
    return tenant


def require_tenant(request: Request, db = Depends(get_db)) -> Tenant:
    """
    Dependency to require a tenant in the request.
    Raises 404 if tenant not found or inactive.
    """
    tenant = resolve_tenant_from_request(request, db)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )
    
    set_current_tenant(tenant)
    return tenant
