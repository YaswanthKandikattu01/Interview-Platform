from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.schemas.admin import (
    RecordContactRequest,
    ScheduleInterviewRequest,
    RescheduleInterviewRequest,
    CompleteInterviewRequest,
    CancelInterviewRequest,
)

router = APIRouter(prefix="/admin", tags=["Admin & Interviewer Management"])


@router.get("/overview")
async def get_overview(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.get_overview()


@router.get("/bookings")
async def list_bookings(
    status: Optional[str] = Query(None),
    category_slug: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sla_filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.list_bookings(
        status=status,
        category_slug=category_slug,
        search=search,
        sla_filter=sla_filter,
        page=page,
        page_size=page_size
    )


@router.get("/bookings/{booking_id}")
async def get_booking_detail(
    booking_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.get_booking_detail(booking_id)


@router.post("/bookings/{booking_id}/contact")
async def record_contact(
    booking_id: str,
    payload: RecordContactRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.record_contact(admin.id, booking_id, payload)


@router.post("/bookings/{booking_id}/schedule")
async def schedule_interview(
    booking_id: str,
    payload: ScheduleInterviewRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.schedule_interview(admin.id, booking_id, payload)


@router.post("/bookings/{booking_id}/reschedule")
async def reschedule_interview(
    booking_id: str,
    payload: RescheduleInterviewRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.reschedule_interview(admin.id, booking_id, payload)


@router.post("/bookings/{booking_id}/complete")
async def complete_interview(
    booking_id: str,
    payload: CompleteInterviewRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.complete_interview(admin.id, booking_id, payload)


@router.post("/bookings/{booking_id}/cancel")
async def cancel_interview(
    booking_id: str,
    payload: CancelInterviewRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.cancel_interview(admin.id, booking_id, payload)
