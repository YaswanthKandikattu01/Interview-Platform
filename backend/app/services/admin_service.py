import logging
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository
from app.repositories.payment_repository import PaymentRepository
from app.models.notification import Notification
from app.models.interview import InterviewRequest, InterviewSchedule
from app.schemas.admin import (
    RecordContactRequest,
    ScheduleInterviewRequest,
    RescheduleInterviewRequest,
    CompleteInterviewRequest,
    CancelInterviewRequest,
)
from app.core.config import settings

logger = logging.getLogger("admin_service")


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdminRepository(db)
        self.user_repo = UserRepository(db)
        self.payment_repo = PaymentRepository(db)

    async def get_overview(self) -> Dict[str, Any]:
        return await self.repo.get_overview_metrics()

    async def list_bookings(
        self,
        status: Optional[str] = None,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        sla_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        offset = (page - 1) * page_size
        items, total = await self.repo.list_bookings(
            status=status,
            category_slug=category_slug,
            search=search,
            sla_filter=sla_filter,
            limit=page_size,
            offset=offset,
        )

        serialized = []
        for req in items:
            cand = await self.user_repo.get_by_id(req.candidate_id)
            sched = req.schedule
            serialized.append({
                "id": req.id,
                "booking_reference": req.booking_reference,
                "category_title": req.interview_type.title if req.interview_type else "N/A",
                "category_slug": req.interview_type.slug if req.interview_type else "N/A",
                "candidate_name": cand.full_name if cand else "Unknown",
                "candidate_email": cand.email if cand else "Unknown",
                "candidate_phone": cand.phone if cand else "N/A",
                "payment_status": req.payment_status,
                "amount_paise": req.amount_paise,
                "scheduling_status": req.scheduling_status,
                "contact_status": req.contact_status,
                "contact_deadline_at": req.contact_deadline_at.isoformat() if req.contact_deadline_at else None,
                "first_contacted_at": req.first_contacted_at.isoformat() if req.first_contacted_at else None,
                "scheduled_start": sched.scheduled_start.isoformat() if sched else None,
                "scheduled_end": sched.scheduled_end.isoformat() if sched else None,
                "meeting_url": sched.meeting_url if sched else None,
                "created_at": req.created_at.isoformat(),
            })

        return {
            "items": serialized,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        }

    async def get_booking_detail(self, booking_id: str) -> Dict[str, Any]:
        booking = await self.repo.get_booking_with_all_relations(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

        cand = await self.user_repo.get_by_id(booking.candidate_id)
        inp = booking.booking_input
        sched = booking.schedule

        contact_logs = [
            {
                "id": log.id,
                "channel": log.channel,
                "notes": log.notes,
                "contacted_at": log.contacted_at.isoformat(),
            }
            for log in (booking.contact_logs or [])
        ]

        schedule_events = []
        if sched and sched.events:
            schedule_events = [
                {
                    "event_type": ev.event_type,
                    "previous_start": ev.previous_start.isoformat() if ev.previous_start else None,
                    "previous_end": ev.previous_end.isoformat() if ev.previous_end else None,
                    "new_start": ev.new_start.isoformat() if ev.new_start else None,
                    "new_end": ev.new_end.isoformat() if ev.new_end else None,
                    "reason": ev.reason,
                    "created_at": ev.created_at.isoformat(),
                }
                for ev in sched.events
            ]

        feedback_data = None
        if sched and sched.feedback:
            feedback_data = {
                "strengths": sched.feedback.strengths,
                "areas_for_improvement": sched.feedback.areas_for_improvement,
                "technical_rating": sched.feedback.technical_rating,
                "communication_rating": sched.feedback.communication_rating,
                "recommendation_summary": sched.feedback.recommendation_summary,
                "is_shared_with_candidate": sched.feedback.is_shared_with_candidate,
            }

        return {
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "category": {
                "title": booking.interview_type.title if booking.interview_type else "N/A",
                "slug": booking.interview_type.slug if booking.interview_type else "N/A",
            },
            "candidate": {
                "id": cand.id if cand else None,
                "full_name": cand.full_name if cand else "Unknown",
                "email": cand.email if cand else "Unknown",
                "phone": cand.phone if cand else "N/A",
            },
            "professional_input": {
                "years_experience": inp.years_experience if inp else 0,
                "current_company": inp.current_company if inp else None,
                "target_role": inp.target_role if inp else None,
                "technical_skills": inp.technical_skills if inp else [],
                "resume_file_id": inp.resume_file_id if inp else None,
                "jd_file_id": inp.jd_file_id if inp else None,
                "jd_text": inp.jd_text if inp else None,
                "additional_notes": inp.additional_notes if inp else None,
            },
            "payment": {
                "status": booking.payment_status,
                "amount_paise": booking.amount_paise,
                "currency": booking.currency,
                "paid_at": booking.paid_at.isoformat() if booking.paid_at else None,
            },
            "sla": {
                "contact_status": booking.contact_status,
                "contact_deadline_at": booking.contact_deadline_at.isoformat() if booking.contact_deadline_at else None,
                "first_contacted_at": booking.first_contacted_at.isoformat() if booking.first_contacted_at else None,
            },
            "schedule": {
                "id": sched.id if sched else None,
                "status": sched.status if sched else None,
                "scheduled_start": sched.scheduled_start.isoformat() if sched else None,
                "scheduled_end": sched.scheduled_end.isoformat() if sched else None,
                "scheduled_duration_minutes": sched.scheduled_duration_minutes if sched else None,
                "meeting_platform": sched.meeting_platform if sched else None,
                "meeting_url": sched.meeting_url if sched else None,
                "joining_instructions": sched.joining_instructions if sched else None,
                "events": schedule_events,
                "feedback": feedback_data,
            } if sched else None,
            "contact_logs": contact_logs,
            "created_at": booking.created_at.isoformat(),
        }

    async def record_contact(
        self,
        admin_id: str,
        booking_id: str,
        payload: RecordContactRequest
    ) -> Dict[str, Any]:
        booking = await self.repo.get_booking_with_all_relations(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

        log = await self.repo.record_contact(
            booking=booking,
            interviewer_id=admin_id,
            channel=payload.channel,
            notes=payload.notes,
        )
        return {
            "status": "contact_recorded",
            "booking_id": booking.id,
            "contact_status": booking.contact_status,
            "first_contacted_at": booking.first_contacted_at.isoformat() if booking.first_contacted_at else None,
            "notes": log.notes,
        }

    async def schedule_interview(
        self,
        admin_id: str,
        booking_id: str,
        payload: ScheduleInterviewRequest
    ) -> Dict[str, Any]:
        booking = await self.repo.get_booking_with_all_relations(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

        if booking.payment_status != "CAPTURED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot schedule an unpaid interview booking."
            )

        # Invariant: Duration must be between 45 and 60 minutes
        duration_minutes = (payload.scheduled_end - payload.scheduled_start).total_seconds() / 60
        if duration_minutes < 45 or duration_minutes > 60:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interview duration must be between 45 and 60 minutes. Requested: {duration_minutes:.1f} minutes."
            )

        # Invariant: Zero double-booking overlap check
        conflict = await self.repo.check_interviewer_overlap(
            interviewer_id=admin_id,
            start_time=payload.scheduled_start,
            end_time=payload.scheduled_end,
            exclude_schedule_id=booking.schedule.id if booking.schedule else None,
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Scheduling conflict: You already have another session booked from {conflict.scheduled_start.isoformat()} to {conflict.scheduled_end.isoformat()}."
            )

        schedule = await self.repo.create_schedule(
            booking=booking,
            interviewer_id=admin_id,
            start_time=payload.scheduled_start,
            end_time=payload.scheduled_end,
            meeting_platform=payload.meeting_platform,
            meeting_url=payload.meeting_url,
            joining_instructions=payload.joining_instructions,
        )

        # Enqueue Email 4: interview_scheduled notification
        cand = await self.user_repo.get_by_id(booking.candidate_id)
        if cand:
            ist_tz = ZoneInfo(settings.BUSINESS_TIMEZONE)
            start_ist = payload.scheduled_start.astimezone(ist_tz)
            date_str = start_ist.strftime("%A, %d %b %Y")
            time_str = start_ist.strftime("%I:%M %p IST")

            notif = Notification(
                interview_request_id=booking.id,
                idempotency_key=f"notif-sched-{schedule.id}-{uuid.uuid4().hex[:6]}",
                recipient_email=cand.email,
                recipient_name=cand.full_name,
                template_name="interview_scheduled",
                subject=f"Interview Scheduled — {booking.interview_type.title} on {date_str}",
                template_data={
                    "candidate_name": cand.full_name,
                    "category_name": booking.interview_type.title,
                    "booking_reference": booking.booking_reference,
                    "interview_date": date_str,
                    "start_time": time_str,
                    "meeting_url": payload.meeting_url,
                    "joining_instructions": payload.joining_instructions or (
                        "Please join 5 minutes early using a laptop or desktop computer with a functional camera, microphone, "
                        "and stable internet connection. Keep an IDE or code editor ready for live technical problem solving."
                    ),
                    "start_time_iso": payload.scheduled_start.isoformat(),
                    "end_time_iso": payload.scheduled_end.isoformat(),
                },
                status="PENDING",
            )
            self.db.add(notif)
            await self.db.commit()

        return {
            "status": "scheduled",
            "schedule_id": schedule.id,
            "scheduled_start": schedule.scheduled_start.isoformat(),
            "scheduled_end": schedule.scheduled_end.isoformat(),
            "meeting_url": schedule.meeting_url,
            "duration_minutes": schedule.scheduled_duration_minutes,
        }

    async def reschedule_interview(
        self,
        admin_id: str,
        booking_id: str,
        payload: RescheduleInterviewRequest
    ) -> Dict[str, Any]:
        booking = await self.repo.get_booking_with_all_relations(booking_id)
        if not booking or not booking.schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled interview not found for this booking."
            )

        duration_minutes = (payload.scheduled_end - payload.scheduled_start).total_seconds() / 60
        if duration_minutes < 45 or duration_minutes > 60:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interview duration must be between 45 and 60 minutes. Requested: {duration_minutes:.1f} minutes."
            )

        # Overlap check excluding current schedule
        conflict = await self.repo.check_interviewer_overlap(
            interviewer_id=admin_id,
            start_time=payload.scheduled_start,
            end_time=payload.scheduled_end,
            exclude_schedule_id=booking.schedule.id,
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Scheduling conflict: You already have another session booked from {conflict.scheduled_start.isoformat()} to {conflict.scheduled_end.isoformat()}."
            )

        schedule = await self.repo.reschedule_interview(
            schedule=booking.schedule,
            booking=booking,
            interviewer_id=admin_id,
            new_start=payload.scheduled_start,
            new_end=payload.scheduled_end,
            new_url=payload.meeting_url,
            reason=payload.reason,
        )

        cand = await self.user_repo.get_by_id(booking.candidate_id)
        if cand:
            ist_tz = ZoneInfo(settings.BUSINESS_TIMEZONE)
            start_ist = payload.scheduled_start.astimezone(ist_tz)
            date_str = start_ist.strftime("%A, %d %b %Y")
            time_str = start_ist.strftime("%I:%M %p IST")

            notif = Notification(
                interview_request_id=booking.id,
                idempotency_key=f"notif-resched-{schedule.id}-{uuid.uuid4().hex[:6]}",
                recipient_email=cand.email,
                recipient_name=cand.full_name,
                template_name="interview_rescheduled",
                subject=f"Interview Rescheduled — {booking.interview_type.title} (New Time: {date_str})",
                template_data={
                    "candidate_name": cand.full_name,
                    "category_name": booking.interview_type.title,
                    "booking_reference": booking.booking_reference,
                    "interview_date": date_str,
                    "start_time": time_str,
                    "meeting_url": schedule.meeting_url,
                    "reason": payload.reason,
                    "start_time_iso": payload.scheduled_start.isoformat(),
                    "end_time_iso": payload.scheduled_end.isoformat(),
                },
                status="PENDING",
            )
            self.db.add(notif)
            await self.db.commit()

        return {
            "status": "rescheduled",
            "schedule_id": schedule.id,
            "new_start": schedule.scheduled_start.isoformat(),
            "new_end": schedule.scheduled_end.isoformat(),
            "meeting_url": schedule.meeting_url,
        }

    async def complete_interview(
        self,
        admin_id: str,
        booking_id: str,
        payload: CompleteInterviewRequest
    ) -> Dict[str, Any]:
        booking = await self.repo.get_booking_with_all_relations(booking_id)
        if not booking or not booking.schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled interview not found for this booking."
            )

        feedback = await self.repo.complete_interview(
            schedule=booking.schedule,
            booking=booking,
            interviewer_id=admin_id,
            strengths=payload.strengths,
            areas_for_improvement=payload.areas_for_improvement,
            technical_rating=payload.technical_rating,
            communication_rating=payload.communication_rating,
            recommendation_summary=payload.recommendation_summary,
            is_shared_with_candidate=payload.is_shared_with_candidate,
        )

        return {
            "status": "completed",
            "booking_id": booking.id,
            "feedback_id": feedback.id,
            "technical_rating": feedback.technical_rating,
            "communication_rating": feedback.communication_rating,
        }

    async def cancel_interview(
        self,
        admin_id: str,
        booking_id: str,
        payload: CancelInterviewRequest
    ) -> Dict[str, Any]:
        booking = await self.repo.get_booking_with_all_relations(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

        await self.repo.cancel_interview(
            booking=booking,
            interviewer_id=admin_id,
            reason=payload.reason,
        )

        cand = await self.user_repo.get_by_id(booking.candidate_id)
        if cand:
            notif = Notification(
                interview_request_id=booking.id,
                idempotency_key=f"notif-cancel-{booking.id}-{uuid.uuid4().hex[:6]}",
                recipient_email=cand.email,
                recipient_name=cand.full_name,
                template_name="interview_cancelled",
                subject=f"Interview Cancelled — {booking.booking_reference}",
                template_data={
                    "candidate_name": cand.full_name,
                    "category_name": booking.interview_type.title,
                    "booking_reference": booking.booking_reference,
                    "reason": payload.reason,
                },
                status="PENDING",
            )
            self.db.add(notif)
            await self.db.commit()

        # If refund is requested, execute refund
        refund_status = None
        if payload.initiate_refund and booking.payment_status == "CAPTURED":
            from app.services.payment_service import PaymentService
            payment_service = PaymentService(self.db)
            refund_res = await payment_service.process_refund(
                admin_id=admin_id,
                booking_id=booking.id,
                reason=f"Cancellation: {payload.reason}"
            )
            refund_status = refund_res.get("status")

        return {
            "status": "cancelled",
            "booking_id": booking.id,
            "reason": payload.reason,
            "refund_status": refund_status,
        }
