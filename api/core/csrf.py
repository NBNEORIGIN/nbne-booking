from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import hashlib
from typing import Optional


class CSRFProtection:
    """
    CSRF token generation and validation.
    
    For server-rendered forms, tokens are embedded in hidden fields.
    For API calls, tokens can be sent in headers.
    """
    
    @staticmethod
    def generate_token() -> str:
        """Generate a cryptographically secure CSRF token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a CSRF token for storage/comparison."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def validate_token(request_token: Optional[str], session_token: Optional[str]) -> bool:
        """
        Validate CSRF token.
        
        Args:
            request_token: Token from form/header
            session_token: Token from session/cookie
            
        Returns:
            True if tokens match, False otherwise
        """
        if not request_token or not session_token:
            return False
        
        return secrets.compare_digest(request_token, session_token)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware for state-changing requests.
    
    Validates CSRF tokens on POST, PUT, PATCH, DELETE requests.
    Exempts:
    - GET, HEAD, OPTIONS requests (safe methods)
    - API endpoints using JWT authentication (stateless)
    - Public booking endpoints (customer-facing)
    """
    
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    EXEMPT_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/password-reset-request",
        "/api/v1/auth/password-reset",
        "/api/v1/services/public",
        "/api/v1/bookings/public",
        "/public/book",
        "/health",
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for app state disable flag
        if getattr(request.app.state, "disable_csrf", False):
            return await call_next(request)

        # Skip CSRF check for safe methods
        if request.method in self.SAFE_METHODS:
            return await call_next(request)
        
        # Skip CSRF check for exempt paths
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Skip CSRF check for API endpoints with JWT auth
        # (JWT tokens provide CSRF protection for stateless APIs)
        if request.url.path.startswith("/api/v1/") and "Authorization" in request.headers:
            return await call_next(request)
        
        # For admin forms and other state-changing requests, validate CSRF token
        csrf_token_header = request.headers.get("X-CSRF-Token")
        csrf_token_form = None
        
        # Try to get token from form data
        if request.method == "POST":
            try:
                form_data = await request.form()
                csrf_token_form = form_data.get("csrf_token")
            except:
                pass
        
        request_token = csrf_token_header or csrf_token_form
        
        # Get session token from cookie
        session_token = request.cookies.get("csrf_token")
        
        if not CSRFProtection.validate_token(request_token, session_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed"
            )
        
        return await call_next(request)


def get_csrf_token(request: Request) -> str:
    """
    Get or generate CSRF token for the current session.
    
    Usage in templates:
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    """
    csrf_token = request.cookies.get("csrf_token")
    
    if not csrf_token:
        csrf_token = CSRFProtection.generate_token()
    
    return csrf_token
