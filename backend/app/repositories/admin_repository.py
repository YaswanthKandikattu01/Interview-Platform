import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.interview import (
    InterviewRequest,
    InterviewSchedule,
    ScheduleEvent,
    SchedulingContactLog,
    InterviewFeedback,
    InterviewType,
    BookingInput,
)
from app.models.user import User
from app.models.payment import Payment

logger = logging.getLogger("admin_repository")


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_booking_with_all_relations(self, booking_id: str) -> Optional[InterviewRequest]:
        stmt = (
            select(InterviewRequest)
            .where(InterviewRequest.id == booking_id)
            .options(
                selectinload(InterviewRequest.interview_type),
                selectinload(InterviewRequest.booking_input),
                selectinload(InterviewRequest.schedule).selectinload(InterviewSchedule.events),
                selectinload(InterviewRequest.schedule).selectinload(InterviewSchedule.feedback),
                selectinload(InterviewRequest.contact_logs),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def check_interviewer_overlap(
        self,
        interviewer_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_schedule_id: Optional[str] = None
    ) -> Optional[InterviewSchedule]:
        """
        Detects if another active scheduled interview overlaps with [start_time, end_time).
        Overlap formula: (existing.start < new.end) AND (existing.end > new.start)
        """
        conditions = [
            InterviewSchedule.interviewer_id == interviewer_id,
            InterviewSchedule.status == "SCHEDULED",
            InterviewSchedule.scheduled_start < end_time,
            InterviewSchedule.scheduled_end > start_time,
        ]
        if exclude_schedule_id:
            conditions.append(InterviewSchedule.id != exclude_schedule_id)

        stmt = select(InterviewSchedule).where(and_(*conditions))
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def record_contact(
        self,
        booking: InterviewRequest,
        interviewer_id: str,
        channel: str,
        notes: str
    ) -> SchedulingContactLog:
        now = datetime.now(timezone.utc)
        log = SchedulingContactLog(
            interview_request_id=booking.id,
            interviewer_id=interviewer_id,
            channel=channel,
            notes=notes,
            contacted_at=now,
        )
        self.db.add(log)

        booking.contact_status = "CONTACTED"
        if not booking.first_contacted_at:
            booking.first_contacted_at = now

        if booking.scheduling_status == "PAID_AWAITING_CONTACT":
            booking.scheduling_status = "CONTACTED"

        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def create_schedule(
        self,
        booking: InterviewRequest,
        interviewer_id: str,
        start_time: datetime,
        end_time: datetime,
        meeting_platform: str,
        meeting_url: str,
        joining_instructions: Optional[str] = None
    ) -> InterviewSchedule:
        now = datetime.now(timezone.utc)
        duration_minutes = int((end_time - start_time).total_seconds() / 60)

        schedule = InterviewSchedule(
            interview_request_id=booking.id,
            interviewer_id=interviewer_id,
            scheduled_start=start_time,
            scheduled_end=end_time,
            scheduled_duration_minutes=duration_minutes,
            meeting_platform=meeting_platform,
            meeting_url=meeting_url,
            joining_instructions=joining_instructions,
            status="SCHEDULED",
        )
        self.db.add(schedule)
        await self.db.flush()

        event = ScheduleEvent(
            schedule_id=schedule.id,
            actor_id=interviewer_id,
            event_type="INITIAL_SCHEDULE",
            new_start=start_time,
            new_end=end_time,
            reason="Confirmed schedule by interviewer",
        )
        self.db.add(event)

        booking.scheduling_status = "SCHEDULED"
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def reschedule_interview(
        self,
        schedule: InterviewSchedule,
        booking: InterviewRequest,
        interviewer_id: str,
        new_start: datetime,
        new_end: datetime,
        new_url: Optional[str],
        reason: str
    ) -> InterviewSchedule:
        duration_minutes = int((new_end - new_start).total_seconds() / 60)

        event = ScheduleEvent(
            schedule_id=schedule.id,
            actor_id=interviewer_id,
            event_type="RESCHEDULED",
            previous_start=schedule.scheduled_start,
            previous_end=schedule.scheduled_end,
            new_start=new_start,
            new_end=new_end,
            reason=reason,
        )
        self.db.add(event)

        schedule.scheduled_start = new_start
        schedule.scheduled_end = new_end
        schedule.scheduled_duration_minutes = duration_minutes
        if new_url:
            schedule.meeting_url = new_url
        schedule.status = "SCHEDULED"

        booking.scheduling_status = "SCHEDULED"

        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def complete_interview(
        self,
        schedule: InterviewSchedule,
        booking: InterviewRequest,
        interviewer_id: str,
        strengths: str,
        areas_for_improvement: str,
        technical_rating: int,
        communication_rating: int,
        recommendation_summary: str,
        is_shared_with_candidate: bool
    ) -> InterviewFeedback:
        schedule.status = "COMPLETED"
        booking.scheduling_status = "COMPLETED"

        feedback = InterviewFeedback(
            interview_schedule_id=schedule.id,
            interviewer_id=interviewer_id,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            technical_rating=technical_rating,
            communication_rating=communication_rating,
            recommendation_summary=recommendation_summary,
            is_shared_with_candidate=is_shared_with_candidate,
        )
        self.db.add(feedback)

        event = ScheduleEvent(
            schedule_id=schedule.id,
            actor_id=interviewer_id,
            event_type="COMPLETED",
            reason="Interview completed successfully by interviewer",
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def cancel_interview(
        self,
        booking: InterviewRequest,
        interviewer_id: str,
        reason: str
    ):
        booking.scheduling_status = "CANCELLED"
        if booking.schedule:
            booking.schedule.status = "CANCELLED"
            event = ScheduleEvent(
                schedule_id=booking.schedule.id,
                actor_id=interviewer_id,
                event_type="CANCELLED",
                reason=reason,
            )
            self.db.add(event)

        await self.db.commit()

    async def get_overview_metrics(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)

        # Revenue
        rev_stmt = select(func.coalesce(func.sum(Payment.amount_paise), 0)).where(Payment.status == "CAPTURED")
        rev_res = await self.db.execute(rev_stmt)
        total_rev_paise = rev_res.scalar_one()

        # Status counts
        total_bookings_stmt = select(func.count(InterviewRequest.id))
        total_bookings = (await self.db.execute(total_bookings_stmt)).scalar_one()

        awaiting_contact_stmt = select(func.count(InterviewRequest.id)).where(
            InterviewRequest.payment_status == "CAPTURED",
            InterviewRequest.contact_status == "PENDING"
        )
        awaiting_contact = (await self.db.execute(awaiting_contact_stmt)).scalar_one()

        overdue_stmt = select(func.count(InterviewRequest.id)).where(
            InterviewRequest.payment_status == "CAPTURED",
            InterviewRequest.contact_status == "PENDING",
            InterviewRequest.contact_deadline_at < now
        )
        overdue_contact = (await self.db.execute(overdue_stmt)).scalar_one()

        scheduled_stmt = select(func.count(InterviewRequest.id)).where(
            InterviewRequest.scheduling_status == "SCHEDULED"
        )
        scheduled_count = (await self.db.execute(scheduled_stmt)).scalar_one()

        completed_stmt = select(func.count(InterviewRequest.id)).where(
            InterviewRequest.scheduling_status == "COMPLETED"
        )
        completed_count = (await self.db.execute(completed_stmt)).scalar_one()

        cancelled_stmt = select(func.count(InterviewRequest.id)).where(
            InterviewRequest.scheduling_status == "CANCELLED"
        )
        cancelled_count = (await self.db.execute(cancelled_stmt)).scalar_one()

        # Upcoming interviews
        upcoming_stmt = (
            select(InterviewSchedule)
            .where(
                InterviewSchedule.status == "SCHEDULED",
                InterviewSchedule.scheduled_start >= now
            )
            .order_by(InterviewSchedule.scheduled_start.asc())
            .limit(5)
            .options(
                selectinload(InterviewSchedule.interview_request).selectinload(InterviewRequest.interview_type),
                selectinload(InterviewSchedule.interview_request).selectinload(InterviewRequest.booking_input),
            )
        )
        upcoming_res = await self.db.execute(upcoming_stmt)
        upcoming_schedules = upcoming_res.scalars().all()

        upcoming_list = []
        for s in upcoming_schedules:
            req = s.interview_request
            inp = req.booking_input if req else None
            upcoming_list.append({
                "schedule_id": s.id,
                "booking_id": req.id if req else None,
                "booking_reference": req.booking_reference if req else "N/A",
                "category_title": req.interview_type.title if req and req.interview_type else "N/A",
                "scheduled_start": s.scheduled_start.isoformat(),
                "scheduled_end": s.scheduled_end.isoformat(),
                "meeting_url": s.meeting_url,
                "candidate_target_role": inp.target_role if inp else "N/A",
            })

        return {
            "total_revenue_paise": total_rev_paise,
            "total_revenue_inr": total_rev_paise / 100.0,
            "total_bookings": total_bookings,
            "awaiting_contact_count": awaiting_contact,
            "overdue_contact_count": overdue_contact,
            "scheduled_count": scheduled_count,
            "completed_count": completed_count,
            "cancelled_count": cancelled_count,
            "upcoming_interviews": upcoming_list,
        }

    async def list_bookings(
        self,
        status: Optional[str] = None,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        sla_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[InterviewRequest], int]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(InterviewRequest)
            .join(InterviewRequest.interview_type)
            .join(User, InterviewRequest.candidate_id == User.id)
            .options(
                selectinload(InterviewRequest.interview_type),
                selectinload(InterviewRequest.booking_input),
                selectinload(InterviewRequest.schedule),
                selectinload(InterviewRequest.contact_logs),
            )
        )

        conditions = []
        if status:
            conditions.append(InterviewRequest.scheduling_status == status)

        if category_slug:
            conditions.append(InterviewType.slug == category_slug)

        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    InterviewRequest.booking_reference.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )

        if sla_filter == "pending":
            conditions.append(InterviewRequest.contact_status == "PENDING")
        elif sla_filter == "overdue":
            conditions.append(
                and_(
                    InterviewRequest.contact_status == "PENDING",
                    InterviewRequest.contact_deadline_at < now
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        # Paginated results
        stmt = stmt.order_by(InterviewRequest.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total_count
