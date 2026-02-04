from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent brute force and abuse.
    
    Limits:
    - Login endpoint: 5 attempts per 15 minutes per IP
    - Password reset: 3 attempts per hour per IP
    - Booking creation: 10 per hour per IP
    - General API: 100 requests per minute per IP
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = defaultdict(lambda: defaultdict(list))
        self.limits = {
            "/api/v1/auth/login": {"max": 5, "window": 900},  # 15 minutes
            "/api/v1/auth/password-reset": {"max": 3, "window": 3600},  # 1 hour
            "/api/v1/bookings/": {"max": 10, "window": 3600},  # 1 hour
            "default": {"max": 100, "window": 60}  # 1 minute
        }
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            limit_key = path if path in self.limits else "default"
            limit = self.limits[limit_key]
            
            now = datetime.now()
            cutoff = now - timedelta(seconds=limit["window"])
            
            self.request_counts[client_ip][limit_key] = [
                ts for ts in self.request_counts[client_ip][limit_key]
                if ts > cutoff
            ]
            
            if len(self.request_counts[client_ip][limit_key]) >= limit["max"]:
                logger.warning(
                    f"Rate limit exceeded for {client_ip} on {path}. "
                    f"Limit: {limit['max']} requests per {limit['window']} seconds"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Please try again later."
                )
            
            self.request_counts[client_ip][limit_key].append(now)
        
        response = await call_next(request)
        return response
