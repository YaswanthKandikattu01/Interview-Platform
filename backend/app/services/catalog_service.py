from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.catalog_repository import CatalogRepository
from app.models.interview import InterviewType, InterviewPrice
from app.schemas.catalog import (
    InterviewCategoryResponse,
    InterviewPriceResponse,
    CanonicalPricingResponse,
)


class CatalogService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CatalogRepository(db)

    async def _format_category_response(self, category: InterviewType) -> InterviewCategoryResponse:
        active_price_record = await self.repo.get_active_price(category.id)
        active_price = None
        if active_price_record:
            active_price = InterviewPriceResponse.model_validate(active_price_record)

        return InterviewCategoryResponse(
            id=category.id,
            slug=category.slug,
            title=category.title,
            short_description=category.short_description,
            detailed_topics=category.detailed_topics,
            display_order=category.display_order,
            is_active=category.is_active,
            active_price=active_price,
        )

    async def list_categories(self) -> List[InterviewCategoryResponse]:
        categories = await self.repo.get_all_categories()
        results = []
        for cat in categories:
            formatted = await self._format_category_response(cat)
            results.append(formatted)
        return results

    async def get_category_by_slug(self, slug: str) -> InterviewCategoryResponse:
        category = await self.repo.get_category_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview category '{slug}' was not found"
            )
        return await self._format_category_response(category)

    def get_canonical_pricing(self) -> CanonicalPricingResponse:
        return CanonicalPricingResponse()

    async def update_category_price(
        self,
        category_id: str,
        new_amount_paise: int,
        admin_id: str,
        ip_address: Optional[str] = None
    ) -> InterviewPriceResponse:
        if new_amount_paise <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Price must be a positive integer in paise"
            )

        category = await self.repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        new_price = await self.repo.update_category_price(
            category_id=category_id,
            new_amount_paise=new_amount_paise,
            admin_id=admin_id,
            ip_address=ip_address,
        )
        return InterviewPriceResponse.model_validate(new_price)
