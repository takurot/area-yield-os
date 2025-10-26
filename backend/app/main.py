"""FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.api.v1 import auth

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="AreaYield OS API",
    description="短期賃貸（民泊）投資の可否判定API",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.db.base import check_database
    from app.services.firestore import check_firestore

    checks = {
        "api": "ok",
        "database": await check_database(),
        "firestore": await check_firestore(),
    }

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503

    return JSONResponse(
        content={
            "status": "ok" if all_ok else "degraded",
            "version": "0.1.0",
            "environment": settings.ENV,
            "checks": checks,
        },
        status_code=status_code,
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AreaYield OS API",
        "version": "0.1.0",
        "docs": "/docs" if settings.DEBUG else "Contact support for API documentation",
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("application_startup", version="0.1.0", environment=settings.ENV)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("application_shutdown")
