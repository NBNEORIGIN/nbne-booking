from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from api.core.database import SessionLocal
from api.core.tenant_context import resolve_tenant_from_request, set_current_tenant


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to resolve and set tenant context for each request.
    This runs before route handlers and makes tenant available throughout the request.
    """
    
    async def dispatch(self, request: Request, call_next):
        session_factory = getattr(request.app.state, "session_factory", SessionLocal)
        db = session_factory()
        try:
            # Resolve tenant from request
            tenant = resolve_tenant_from_request(request, db)
            
            # Set in context (available to all downstream code)
            set_current_tenant(tenant)
            
            # Also attach to request state for easy access
            request.state.tenant = tenant
            
            response = await call_next(request)
            return response
        finally:
            db.close()
            # Clear tenant context after request
            set_current_tenant(None)
