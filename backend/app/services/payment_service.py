import json
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.repositories.booking_repository import BookingRepository
from app.integrations.razorpay_client import razorpay_client
from app.schemas.payment import (
    CreateOrderResponse,
    VerifyPaymentRequest,
    PaymentStatusResponse,
)
from app.core.config import settings

logger = logging.getLogger("payment_service")


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaymentRepository(db)
        self.booking_repo = BookingRepository(db)

    async def create_order(
        self,
        candidate_id: str,
        booking_id: str
    ) -> CreateOrderResponse:
        # 1. Fetch booking and enforce candidate ownership
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking or booking.candidate_id != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or access denied."
            )

        # 2. Check if already paid
        if booking.payment_status == "CAPTURED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This booking has already been paid for."
            )

        # 3. Create order in Razorpay using authoritative price (19900 paise = ₹199)
        amount_paise = booking.amount_paise
        receipt = booking.booking_reference
        notes = {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "candidate_id": candidate_id,
            "category": booking.interview_type.title,
        }

        rzp_order = await razorpay_client.create_order(
            amount_paise=amount_paise,
            currency="INR",
            receipt=receipt,
            notes=notes,
        )

        # 4. Save payment ledger record
        await self.repo.create_payment_order(
            interview_request_id=booking.id,
            razorpay_order_id=rzp_order["id"],
            amount_paise=amount_paise,
            currency="INR",
        )

        return CreateOrderResponse(
            order_id=rzp_order["id"],
            amount_paise=amount_paise,
            currency="INR",
            key_id=settings.RAZORPAY_KEY_ID,
            booking_reference=booking.booking_reference,
            category_title=booking.interview_type.title,
        )

    async def verify_checkout(
        self,
        candidate_id: str,
        req: VerifyPaymentRequest
    ) -> PaymentStatusResponse:
        # 1. Verify HMAC signature
        is_valid = razorpay_client.verify_checkout_signature(
            razorpay_order_id=req.razorpay_order_id,
            razorpay_payment_id=req.razorpay_payment_id,
            razorpay_signature=req.razorpay_signature,
        )
        if not is_valid:
            logger.warning(f"Invalid payment signature for order {req.razorpay_order_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Razorpay payment signature. Payment could not be verified."
            )

        # 2. Fetch payment record
        payment = await self.repo.get_payment_by_order_id(req.razorpay_order_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found for this order."
            )

        # 3. Idempotently mark captured
        booking = await self.repo.mark_payment_captured(
            payment=payment,
            razorpay_payment_id=req.razorpay_payment_id,
            signature=req.razorpay_signature,
        )

        import zoneinfo
        ist_tz = zoneinfo.ZoneInfo(settings.BUSINESS_TIMEZONE)
        deadline_str = (
            booking.contact_deadline_at.astimezone(ist_tz).strftime("%I:%M %p IST on %d %b %Y")
            if booking.contact_deadline_at else None
        )

        return PaymentStatusResponse(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            payment_status=booking.payment_status,
            scheduling_status=booking.scheduling_status,
            razorpay_payment_id=req.razorpay_payment_id,
            amount_paise=booking.amount_paise,
            paid_at=booking.paid_at.isoformat() if booking.paid_at else None,
            contact_deadline_ist=deadline_str,
            message="Payment verified successfully. Your interviewer will contact you today to arrange your session.",
        )

    async def handle_webhook(
        self,
        raw_body: bytes,
        signature: str
    ) -> Dict[str, Any]:
        # 1. Verify webhook HMAC signature against raw body bytes
        is_valid = razorpay_client.verify_webhook_signature(raw_body, signature)
        if not is_valid:
            logger.warning("Rejected webhook with invalid HMAC signature.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature."
            )

        data = json.loads(raw_body.decode("utf-8"))
        event_id = data.get("event_id") or data.get("id") or f"evt_{hash(raw_body)}"
        event_type = data.get("event", "unknown")

        # 2. Idempotency Check
        existing_event = await self.repo.get_webhook_event(event_id)
        if existing_event and existing_event.is_processed:
            logger.info(f"Webhook event {event_id} already processed. Returning 200 OK.")
            return {"status": "already_processed"}

        if not existing_event:
            await self.repo.save_webhook_event(event_id, event_type, data)

        try:
            # Handle payment.captured
            if event_type == "payment.captured":
                payment_entity = data.get("payload", {}).get("payment", {}).get("entity", {})
                order_id = payment_entity.get("order_id")
                payment_id = payment_entity.get("id")
                method = payment_entity.get("method")
                vpa = payment_entity.get("vpa")
                bank = payment_entity.get("bank")

                if order_id:
                    payment = await self.repo.get_payment_by_order_id(order_id)
                    if payment and payment.status != "CAPTURED":
                        await self.repo.mark_payment_captured(
                            payment=payment,
                            razorpay_payment_id=payment_id,
                            method=method,
                            vpa=vpa,
                            bank=bank,
                        )

            # Handle payment.failed
            elif event_type == "payment.failed":
                payment_entity = data.get("payload", {}).get("payment", {}).get("entity", {})
                order_id = payment_entity.get("order_id")
                err_code = payment_entity.get("error_code", "UNKNOWN")
                err_desc = payment_entity.get("error_description", "Payment failed at gateway")

                if order_id:
                    payment = await self.repo.get_payment_by_order_id(order_id)
                    if payment and payment.status != "FAILED":
                        await self.repo.mark_payment_failed(payment, err_code, err_desc)

            await self.repo.mark_webhook_processed(event_id)
            return {"status": "success", "event": event_type}

        except Exception as e:
            logger.error(f"Error processing webhook {event_id}: {str(e)}", exc_info=True)
            await self.repo.mark_webhook_processed(event_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook handling error: {str(e)}"
            )

    async def process_refund(
        self,
        admin_id: str,
        booking_id: str,
        reason: str
    ) -> Dict[str, Any]:
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

        if booking.payment_status != "CAPTURED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot refund a booking that has not been successfully paid."
            )

        # Find captured payment
        payment_stmt = (
            select(Payment)
            .where(
                Payment.interview_request_id == booking.id,
                Payment.status == "CAPTURED"
            )
        )
        payment_res = await self.db.execute(payment_stmt)
        payment = payment_res.scalar_one_or_none()

        if not payment or not payment.razorpay_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Captured payment transaction ID not found for refund."
            )

        # Call Razorpay Refund API
        rzp_refund = await razorpay_client.initiate_refund(
            payment_id=payment.razorpay_payment_id,
            amount_paise=payment.amount_paise,
            notes={"booking_id": booking.id, "reason": reason},
        )

        # Record refund in database
        refund_record = await self.repo.create_refund(
            payment_id=payment.id,
            interview_request_id=booking.id,
            amount_paise=payment.amount_paise,
            reason=reason,
            initiated_by=admin_id,
            razorpay_refund_id=rzp_refund.get("id"),
        )

        booking.payment_status = "REFUNDED"
        booking.scheduling_status = "CANCELLED"
        self.db.add(booking)
        await self.db.commit()

        return {
            "status": "refund_processed",
            "refund_id": refund_record.id,
            "razorpay_refund_id": rzp_refund.get("id"),
            "amount_paise": payment.amount_paise,
            "booking_reference": booking.booking_reference,
        }
