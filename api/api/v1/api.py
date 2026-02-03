from fastapi import APIRouter
from api.api.v1.endpoints import tenants, services, availability, blackouts, slots, bookings, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(availability.router, prefix="/availability", tags=["availability"])
api_router.include_router(blackouts.router, prefix="/blackouts", tags=["blackouts"])
api_router.include_router(slots.router, prefix="/slots", tags=["slots"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
