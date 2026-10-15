import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.interview import InterviewType, InterviewPrice
from app.models.audit import AuditLog
from app.core.config import settings


class CatalogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def seed_categories_and_prices(self) -> None:
        """Seed exactly the 6 allowed interview categories and active ₹199 price packages."""
        for cat_data in settings.ALLOWED_CATEGORIES:
            slug = cat_data["slug"]
            stmt = select(InterviewType).where(InterviewType.slug == slug)
            result = await self.db.execute(stmt)
            category = result.scalar_one_or_none()

            if not category:
                category = InterviewType(
                    id=str(uuid.uuid4()),
                    slug=slug,
                    title=cat_data["title"],
                    short_description=cat_data["short_description"],
                    detailed_topics=cat_data["topics"],
                    display_order=cat_data["display_order"],
                    is_active=True,
                )
                self.db.add(category)
                await self.db.flush()

            # Check if active price exists for this category
            price_stmt = (
                select(InterviewPrice)
                .where(
                    InterviewPrice.interview_type_id == category.id,
                    InterviewPrice.is_active == True  # noqa: E712
                )
            )
            price_res = await self.db.execute(price_stmt)
            active_price = price_res.scalar_one_or_none()

            if not active_price:
                price = InterviewPrice(
                    id=str(uuid.uuid4()),
                    interview_type_id=category.id,
                    amount_paise=settings.PACKAGE_PRICE_PAISE,  # 19900 paise = ₹199
                    currency="INR",
                    duration_min_minutes=settings.PACKAGE_DURATION_MIN_MINUTES,
                    duration_max_minutes=settings.PACKAGE_DURATION_MAX_MINUTES,
                    duration_display=settings.PACKAGE_DURATION_DISPLAY,
                    is_active=True,
                )
                self.db.add(price)
                await self.db.flush()

        await self.db.commit()

    async def get_all_categories(self) -> List[InterviewType]:
        stmt = (
            select(InterviewType)
            .where(InterviewType.is_active == True)  # noqa: E712
            .order_by(InterviewType.display_order.asc())
            .options(selectinload(InterviewType.prices))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_category_by_slug(self, slug: str) -> Optional[InterviewType]:
        stmt = (
            select(InterviewType)
            .where(InterviewType.slug == slug, InterviewType.is_active == True)  # noqa: E712
            .options(selectinload(InterviewType.prices))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_category_by_id(self, category_id: str) -> Optional[InterviewType]:
        stmt = (
            select(InterviewType)
            .where(InterviewType.id == category_id)
            .options(selectinload(InterviewType.prices))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_price(self, interview_type_id: str) -> Optional[InterviewPrice]:
        stmt = select(InterviewPrice).where(
            InterviewPrice.interview_type_id == interview_type_id,
            InterviewPrice.is_active == True  # noqa: E712
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_category_price(
        self,
        category_id: str,
        new_amount_paise: int,
        admin_id: str,
        ip_address: Optional[str] = None
    ) -> InterviewPrice:
        now = datetime.now(timezone.utc)
        # 1. Fetch current active price
        current_price = await self.get_active_price(category_id)
        if current_price:
            # 2. Retire current active price
            current_price.is_active = False
            current_price.retired_at = now
            self.db.add(current_price)
            old_amount = current_price.amount_paise
        else:
            old_amount = 0

        # 3. Insert new active price snapshot
        new_price = InterviewPrice(
            id=str(uuid.uuid4()),
            interview_type_id=category_id,
            amount_paise=new_amount_paise,
            currency="INR",
            duration_min_minutes=settings.PACKAGE_DURATION_MIN_MINUTES,
            duration_max_minutes=settings.PACKAGE_DURATION_MAX_MINUTES,
            duration_display=settings.PACKAGE_DURATION_DISPLAY,
            is_active=True,
            created_at=now,
        )
        self.db.add(new_price)

        # 4. Record audit log
        audit = AuditLog(
            id=str(uuid.uuid4()),
            actor_id=admin_id,
            action="UPDATE_CATEGORY_PRICE",
            target_type="interview_prices",
            target_id=new_price.id,
            ip_address=ip_address,
            changes={
                "category_id": category_id,
                "old_amount_paise": old_amount,
                "new_amount_paise": new_amount_paise,
            },
            created_at=now,
        )
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(new_price)
        return new_price
