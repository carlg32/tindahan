"""API v1 router configuration."""
from fastapi import APIRouter

from app.api.v1 import auth, products, dashboard

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers
router.include_router(auth.router)
router.include_router(products.router)
router.include_router(dashboard.router)