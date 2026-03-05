"""FastAPI main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events handler.
    
    Handles startup and shutdown events for the application.
    """
    # Startup: Create tables (in production use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # Application runs here
    
    # Shutdown: Close database connections
    await engine.dispose()


# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Inventory Management System API - Phase 1 Backend Foundation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
# For GitHub Codespaces, we need to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Inventory Management System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
        },
    )


# Import and include routers
from app.api.v1 import router as v1_router

# Include API v1 router
app.include_router(v1_router)
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
# app.include_router(stock.router, prefix="/api/v1/stock", tags=["Stock"])
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


# Placeholder router for future API endpoints
@app.get("/api/v1/placeholder")
async def placeholder():
    """Placeholder endpoint for Phase 2 API development."""
    return {
        "message": "API v1 endpoints - to be implemented in Phase 2",
        "available_endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users",
            "products": "/api/v1/products",
            "stock": "/api/v1/stock",
            "dashboard": "/api/v1/dashboard",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
