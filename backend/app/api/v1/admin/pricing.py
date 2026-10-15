from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.services.catalog_service import CatalogService
from app.schemas.catalog import (
    InterviewPriceResponse,
    UpdateCategoryPriceRequest,
)

router = APIRouter(prefix="/admin", tags=["Admin - Catalog & Pricing"])


@router.put("/categories/{category_id}/price", response_model=InterviewPriceResponse, status_code=status.HTTP_200_OK)
async def update_category_price(
    category_id: str,
    payload: UpdateCategoryPriceRequest,
    request: Request,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update category price. Retires previous active price and creates new snapshot without modifying existing bookings."""
    service = CatalogService(db)
    client_ip = request.client.host if request.client else None
    return await service.update_category_price(
        category_id=category_id,
        new_amount_paise=payload.amount_paise,
        admin_id=admin.id,
        ip_address=client_ip,
    )
