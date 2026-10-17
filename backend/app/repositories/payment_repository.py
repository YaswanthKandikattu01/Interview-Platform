import uuid
from datetime import datetime, timezone, time, timedelta
import zoneinfo
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.payment import Payment, WebhookEvent, Refund
from app.models.interview import InterviewRequest
from app.models.notification import Notification
from app.models.user import User
from app.core.config import settings


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_contact_deadline(paid_at_utc: datetime) -> datetime:
    """
    Calculate the interviewer personal contact deadline in Asia/Kolkata (IST).
    - If paid between 08:00 AM IST and 08:00 PM IST: Deadline is 11:59:59 PM IST of the same calendar day.
    - If paid after 08:00 PM IST: Deadline is 12:00:00 PM IST the following day (14h+ buffer).
    - If paid between 12:00 AM IST and 07:59 AM IST: Deadline is 12:00:00 PM IST of the same day.
    """
    ist_tz = zoneinfo.ZoneInfo(settings.BUSINESS_TIMEZONE)
    paid_ist = paid_at_utc.astimezone(ist_tz)
    paid_time = paid_ist.time()

    if time(8, 0) <= paid_time <= time(20, 0):
        # Same calendar day by 11:59:59 PM IST
        deadline_ist = paid_ist.replace(hour=23, minute=59, second=59, microsecond=0)
    elif paid_time > time(20, 0):
        # Next calendar day by 12:00:00 PM IST
        next_day = paid_ist + timedelta(days=1)
        deadline_ist = next_day.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        # Early morning (before 8 AM IST) -> by 12:00:00 PM IST today
        deadline_ist = paid_ist.replace(hour=12, minute=0, second=0, microsecond=0)

    return deadline_ist.astimezone(timezone.utc)


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_order(
        self,
        interview_request_id: str,
        razorpay_order_id: str,
        amount_paise: int,
        currency: str = "INR"
    ) -> Payment:
        payment = Payment(
            id=str(uuid.uuid4()),
            interview_request_id=interview_request_id,
            razorpay_order_id=razorpay_order_id,
            amount_paise=amount_paise,
            currency=currency,
            status="CREATED",
            created_at=utc_now(),
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_payment_by_order_id(self, order_id: str) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.razorpay_order_id == order_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_payment_by_payment_id(self, payment_id: str) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.razorpay_payment_id == payment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_webhook_event(self, event_id: str) -> Optional[WebhookEvent]:
        stmt = select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_webhook_event(
        self,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> WebhookEvent:
        event = WebhookEvent(
            id=str(uuid.uuid4()),
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            is_processed=False,
            received_at=utc_now(),
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def mark_webhook_processed(self, event_id: str, error: Optional[str] = None) -> None:
        stmt = (
            update(WebhookEvent)
            .where(WebhookEvent.event_id == event_id)
            .values(
                is_processed=True,
                processing_error=error,
                processed_at=utc_now(),
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_payment_captured(
        self,
        payment: Payment,
        razorpay_payment_id: str,
        signature: Optional[str] = None,
        method: Optional[str] = None,
        vpa: Optional[str] = None,
        bank: Optional[str] = None,
    ) -> InterviewRequest:
        """
        Idempotent transactional capture:
        1. Updates payment status to CAPTURED.
        2. Updates interview_request to CAPTURED and PAID_AWAITING_CONTACT.
        3. Computes contact_deadline_at using the Asia/Kolkata midnight SLA cutoff policy.
        4. Writes outbox notification records for Candidate (Payment Success) and Admin (New Booking).
        """
        now = utc_now()
        deadline = compute_contact_deadline(now)

        payment.status = "CAPTURED"
        payment.razorpay_payment_id = razorpay_payment_id
        if signature:
            payment.razorpay_signature = signature
        if method:
            payment.method = method
        if vpa:
            payment.vpa = vpa
        if bank:
            payment.bank = bank
        payment.captured_at = now
        self.db.add(payment)

        # Load interview request with candidate & category
        stmt = (
            select(InterviewRequest)
            .where(InterviewRequest.id == payment.interview_request_id)
            .options(
                selectinload(InterviewRequest.interview_type),
                selectinload(InterviewRequest.booking_input),
            )
        )
        res = await self.db.execute(stmt)
        booking = res.scalar_one()

        booking.payment_status = "CAPTURED"
        booking.scheduling_status = "PAID_AWAITING_CONTACT"
        booking.paid_at = now
        booking.contact_deadline_at = deadline
        booking.contact_status = "PENDING"
        self.db.add(booking)

        # Fetch candidate user
        user_stmt = select(User).where(User.id == booking.candidate_id)
        user_res = await self.db.execute(user_stmt)
        candidate = user_res.scalar_one()

        # Enqueue Outbox Notification 1: Candidate Payment Successful
        cand_notif_key = f"payment_success_{booking.id}_{razorpay_payment_id}"
        existing_cand_notif = await self.db.execute(
            select(Notification).where(Notification.idempotency_key == cand_notif_key)
        )
        if not existing_cand_notif.scalar_one_or_none():
            category_slug = booking.interview_type.slug
            duration_text = (
                "2 Hours (120 mins)"
                if category_slug == "system-design"
                else ("Detailed Review & Feedback" if category_slug == "resume-review" else "45–60 minutes")
            )
            amount_text = f"₹{booking.amount_paise // 100}"

            cand_notif = Notification(
                id=str(uuid.uuid4()),
                interview_request_id=booking.id,
                idempotency_key=cand_notif_key,
                recipient_email=candidate.email,
                recipient_name=candidate.full_name,
                template_name="PAYMENT_SUCCESSFUL",
                subject="Payment Successful — Your Mock Interview Is Booked",
                template_data={
                    "candidate_name": candidate.full_name,
                    "category_title": booking.interview_type.title,
                    "duration_display": duration_text,
                    "amount_display": amount_text,
                    "booking_reference": booking.booking_reference,
                    "payment_reference": razorpay_payment_id,
                },
                status="PENDING",
            )
            self.db.add(cand_notif)

        # Enqueue Outbox Notification 3: Admin New Booking Alert
        admin_notif_key = f"admin_new_booking_{booking.id}_{razorpay_payment_id}"
        existing_admin_notif = await self.db.execute(
            select(Notification).where(Notification.idempotency_key == admin_notif_key)
        )
        if not existing_admin_notif.scalar_one_or_none():
            ist_tz = zoneinfo.ZoneInfo(settings.BUSINESS_TIMEZONE)
            deadline_ist_str = deadline.astimezone(ist_tz).strftime("%d %b %Y, %I:%M %p IST")

            admin_notif = Notification(
                id=str(uuid.uuid4()),
                interview_request_id=booking.id,
                idempotency_key=admin_notif_key,
                recipient_email=settings.ADMIN_EMAIL,
                recipient_name="Mock Interview Team",
                template_name="ADMIN_NEW_BOOKING",
                subject=f"[NEW BOOKING] {booking.interview_type.title} - {candidate.full_name}",
                template_data={
                    "candidate_name": candidate.full_name,
                    "candidate_email": candidate.email,
                    "candidate_phone": candidate.phone,
                    "category_title": booking.interview_type.title,
                    "duration_display": duration_text,
                    "amount_display": amount_text,
                    "booking_reference": booking.booking_reference,
                    "payment_reference": razorpay_payment_id,
                    "contact_deadline_ist": deadline_ist_str,
                    "comments": booking.booking_input.additional_notes if booking.booking_input else "None provided",
                    "target_role": booking.booking_input.target_role if booking.booking_input else "N/A",
                    "years_experience": booking.booking_input.years_experience if booking.booking_input else 0,
                },
                status="PENDING",
            )
            self.db.add(admin_notif)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def mark_payment_failed(
        self,
        payment: Payment,
        error_code: str,
        error_description: str
    ) -> None:
        payment.status = "FAILED"
        payment.error_code = error_code
        payment.error_description = error_description
        self.db.add(payment)

        # Also queue failed payment email
        stmt = (
            select(InterviewRequest)
            .where(InterviewRequest.id == payment.interview_request_id)
            .options(selectinload(InterviewRequest.interview_type))
        )
        res = await self.db.execute(stmt)
        booking = res.scalar_one()

        user_stmt = select(User).where(User.id == booking.candidate_id)
        user_res = await self.db.execute(user_stmt)
        candidate = user_res.scalar_one()

        fail_notif_key = f"payment_failed_{payment.id}"
        fail_notif = Notification(
            id=str(uuid.uuid4()),
            interview_request_id=booking.id,
            idempotency_key=fail_notif_key,
            recipient_email=candidate.email,
            recipient_name=candidate.full_name,
            template_name="PAYMENT_FAILED",
            subject="Mock Interview Payment Unsuccessful",
            template_data={
                "candidate_name": candidate.full_name,
                "category_title": booking.interview_type.title,
                "payment_reference": payment.razorpay_order_id,
            },
            status="PENDING",
        )
        self.db.add(fail_notif)
        await self.db.commit()

    async def create_refund(
        self,
        payment_id: str,
        interview_request_id: str,
        amount_paise: int,
        reason: str,
        initiated_by: str,
        razorpay_refund_id: Optional[str] = None
    ) -> Refund:
        refund = Refund(
            id=str(uuid.uuid4()),
            payment_id=payment_id,
            interview_request_id=interview_request_id,
            razorpay_refund_id=razorpay_refund_id,
            amount_paise=amount_paise,
            currency="INR",
            reason=reason,
            status="PROCESSED" if razorpay_refund_id else "PENDING",
            initiated_by=initiated_by,
            created_at=utc_now(),
            processed_at=utc_now() if razorpay_refund_id else None,
        )
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
