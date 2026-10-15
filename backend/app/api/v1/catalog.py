from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.catalog_service import CatalogService
from app.schemas.catalog import (
    InterviewCategoryResponse,
    CanonicalPricingResponse,
)

router = APIRouter(tags=["Categories & Pricing"])


@router.get("/categories", response_model=List[InterviewCategoryResponse], status_code=status.HTTP_200_OK)
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all active mock interview categories (strictly 6 categories) with active ₹199 pricing."""
    service = CatalogService(db)
    return await service.list_categories()


@router.get("/categories/{slug}", response_model=InterviewCategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(slug: str, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a single interview category by slug."""
    service = CatalogService(db)
    return await service.get_category_by_slug(slug)


@router.get("/pricing", response_model=CanonicalPricingResponse, status_code=status.HTTP_200_OK)
async def get_canonical_pricing(db: AsyncSession = Depends(get_db)):
    """Retrieve the canonical mock interview pricing package (₹199 / 19,900 paise, 45–60 mins)."""
    service = CatalogService(db)
    return service.get_canonical_pricing()
