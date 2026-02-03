from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.core.config import settings
from api.core.database import engine, Base
from api.api.v1.api import api_router
from api.api.admin.routes import router as admin_router
from api.api.public.routes import router as public_router
from api.middleware.tenant import TenantMiddleware
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.security_headers import SecurityHeadersMiddleware
from api.core.csrf import CSRFMiddleware
from api.core.log_sanitizer import setup_sanitized_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup log sanitization to prevent sensitive data leakage
setup_sanitized_logging(mask_emails=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up NBNE Booking API")
    yield
    logger.info("Shutting down NBNE Booking API")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(api_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/admin")
app.include_router(public_router, prefix="/public")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
