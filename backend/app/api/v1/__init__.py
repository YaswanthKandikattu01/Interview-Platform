from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.candidate import router as candidate_router
from app.api.v1.payments import router as payments_router
from app.api.v1.admin.pricing import router as admin_pricing_router
from app.api.v1.admin.bookings import router as admin_bookings_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(catalog_router)
api_v1_router.include_router(candidate_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(admin_pricing_router)
api_v1_router.include_router(admin_bookings_router)

__all__ = ["api_v1_router"]
