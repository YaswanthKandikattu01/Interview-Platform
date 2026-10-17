import secrets
from datetime import datetime, timezone
import zoneinfo
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.booking_repository import BookingRepository
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.user_repository import UserRepository
from app.core.file_security import process_and_store_upload
from app.models.interview import InterviewRequest
from app.models.file import StoredFile
from app.schemas.booking import (
    FileUploadResponse,
    CreateBookingDraftRequest,
    BookingDetailResponse,
    InstantBookingRequest,
    InstantBookingResponse,
)
from app.core.config import settings


class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BookingRepository(db)
        self.cat_repo = CatalogRepository(db)

    async def upload_file(
        self,
        user_id: str,
        file: UploadFile,
        purpose: str  # 'RESUME' or 'JOB_DESCRIPTION'
    ) -> FileUploadResponse:
        sanitized_name, storage_path, mime_type, file_size, checksum, original_name = (
            await process_and_store_upload(file, user_id, purpose)
        )
        stored_file = await self.repo.save_stored_file(
            user_id=user_id,
            file_purpose=purpose,
            original_filename=original_name,
            sanitized_filename=sanitized_name,
            storage_path=storage_path,
            file_size_bytes=file_size,
            mime_type=mime_type,
            sha256_checksum=checksum,
        )
        return FileUploadResponse(
            file_id=stored_file.id,
            original_filename=stored_file.original_filename,
            file_size_bytes=stored_file.file_size_bytes,
            mime_type=stored_file.mime_type,
            file_purpose=stored_file.file_purpose,
        )

    def _format_booking_response(self, booking: InterviewRequest) -> BookingDetailResponse:
        # Determine status headline and message with IST timezone awareness
        ist_tz = zoneinfo.ZoneInfo(settings.BUSINESS_TIMEZONE)
        now_ist = datetime.now(timezone.utc).astimezone(ist_tz)
        
        status_headline = "Booking Created"
        status_message = "Complete payment of ₹199 to confirm your mock interview session."

        if booking.payment_status == "CAPTURED":
            if booking.scheduling_status == "PAID_AWAITING_CONTACT":
                paid_ist = booking.paid_at.astimezone(ist_tz) if booking.paid_at else now_ist
                is_same_day = (paid_ist.date() == now_ist.date())
                
                if is_same_day:
                    status_headline = "Payment Confirmed — Awaiting Interviewer Scheduling"
                    status_message = "Our interviewer will contact you by email today to arrange your interview date and time."
                else:
                    status_headline = "Payment Confirmed — Scheduling In Progress"
                    status_message = "Our interviewer is currently coordinating your interview date and time with you via email."
            elif booking.scheduling_status == "CONTACTED":
                status_headline = "Interviewer Contacted"
                status_message = "Our interviewer has reached out to you. Please reply to finalize your interview slot."
            elif booking.scheduling_status == "SCHEDULED":
                status_headline = "Interview Scheduled"
                status_message = "Your live mock interview is confirmed. Please join using the meeting link at your scheduled time."
            elif booking.scheduling_status == "COMPLETED":
                status_headline = "Interview Completed"
                status_message = "Session successfully conducted. Best wishes on your engineering career journey!"
            elif booking.scheduling_status == "CANCELLED":
                status_headline = "Interview Cancelled"
                status_message = "This mock interview booking has been cancelled."
            elif booking.scheduling_status == "NO_SHOW":
                status_headline = "Interview Marked No-Show"
                status_message = "You were marked as no-show. Please contact support to discuss rescheduling."

        scheduled_start = booking.schedule.scheduled_start if booking.schedule else None
        scheduled_end = booking.schedule.scheduled_end if booking.schedule else None
        meeting_url = booking.schedule.meeting_url if booking.schedule else None

        years_exp = booking.booking_input.years_experience if booking.booking_input else 0.0
        target_role = booking.booking_input.target_role if booking.booking_input else ""

        return BookingDetailResponse(
            id=booking.id,
            booking_reference=booking.booking_reference,
            amount_paise=booking.amount_paise,
            currency=booking.currency,
            payment_status=booking.payment_status,
            scheduling_status=booking.scheduling_status,
            category_title=booking.interview_type.title,
            category_slug=booking.interview_type.slug,
            duration_display="45–60 minutes",
            years_experience=years_exp,
            target_role=target_role,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            meeting_url=meeting_url,
            status_headline=status_headline,
            status_message=status_message,
            created_at=booking.created_at,
        )

    async def create_booking_draft(
        self,
        candidate_id: str,
        req: CreateBookingDraftRequest
    ) -> BookingDetailResponse:
        # 1. Fetch category
        category = await self.cat_repo.get_category_by_slug(req.category_slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview category '{req.category_slug}' does not exist"
            )

        # 2. Fetch authoritative database price
        active_price = await self.cat_repo.get_active_price(category.id)
        if not active_price:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Active price package is not configured for this category"
            )

        # 3. Verify resume file ownership
        resume_file = await self.repo.get_stored_file(req.resume_file_id)
        if not resume_file or resume_file.user_id != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unauthorized resume file ID"
            )

        # 4. Verify optional JD file ownership
        if req.jd_file_id:
            jd_file = await self.repo.get_stored_file(req.jd_file_id)
            if not jd_file or jd_file.user_id != candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or unauthorized job description file ID"
                )

        # 5. Create booking draft
        booking = await self.repo.create_booking_draft(
            candidate_id=candidate_id,
            interview_type_id=category.id,
            price_snapshot_id=active_price.id,
            amount_paise=active_price.amount_paise,  # Authoritative 19900 paise
            resume_file_id=req.resume_file_id,
            years_experience=req.years_experience,
            target_role=req.target_role,
            technical_skills=req.technical_skills,
            current_company=req.current_company,
            jd_file_id=req.jd_file_id,
            jd_text=req.jd_text,
            additional_notes=req.additional_notes,
        )
        return self._format_booking_response(booking)

    async def list_candidate_bookings(self, candidate_id: str) -> List[BookingDetailResponse]:
        bookings = await self.repo.get_candidate_bookings(candidate_id)
        return [self._format_booking_response(b) for b in bookings]

    async def get_candidate_booking(self, candidate_id: str, booking_id: str) -> BookingDetailResponse:
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking or booking.candidate_id != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return self._format_booking_response(booking)

    async def get_file_for_candidate(self, candidate_id: str, file_id: str) -> StoredFile:
        file_rec = await self.repo.get_stored_file(file_id)
        if not file_rec or file_rec.user_id != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        return file_rec

    async def create_instant_booking(
        self,
        req: InstantBookingRequest
    ) -> InstantBookingResponse:
        # 1. Fetch category and authoritative active price snapshot
        category = await self.cat_repo.get_category_by_slug(req.category_slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview category '{req.category_slug}' not found."
            )

        price_snapshot = await self.cat_repo.get_active_price(category.id)
        if not price_snapshot:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No active price configuration found for category."
            )

        # 2. Get or auto-provision Candidate User
        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_email(req.email)
        phone_val = (req.phone or "").strip()
        years_exp = req.years_experience if req.years_experience is not None else 0.0
        role_target = (req.target_role or "Candidate").strip()
        comments_notes = (req.comments or req.additional_notes or "").strip() or None

        if not user:
            random_pwd = secrets.token_urlsafe(24)
            user, _ = await user_repo.create_user(
                email=req.email,
                password=random_pwd,
                full_name=req.full_name,
                phone=phone_val,
                role="CANDIDATE",
                is_email_verified=True,
                years_experience=years_exp,
                current_company=req.current_company,
                target_role=role_target,
                technical_skills=req.technical_skills,
            )
        else:
            user.full_name = req.full_name
            if phone_val:
                user.phone = phone_val
            if user.profile:
                user.profile.years_experience = years_exp
                user.profile.current_company = req.current_company.strip() if req.current_company else None
                user.profile.target_role = role_target
                user.profile.technical_skills = req.technical_skills
            await self.db.commit()

        # 3. Associate uploaded files with this user
        resume_stmt = select(StoredFile).where(StoredFile.id == req.resume_file_id)
        resume_file = (await self.db.execute(resume_stmt)).scalar_one_or_none()
        if resume_file:
            resume_file.user_id = user.id

        if req.jd_file_id:
            jd_stmt = select(StoredFile).where(StoredFile.id == req.jd_file_id)
            jd_file = (await self.db.execute(jd_stmt)).scalar_one_or_none()
            if jd_file:
                jd_file.user_id = user.id

        # 4. Create InterviewRequest draft with authoritative price snapshot
        booking = await self.repo.create_booking_draft(
            candidate_id=user.id,
            interview_type_id=category.id,
            price_snapshot_id=price_snapshot.id,
            amount_paise=price_snapshot.amount_paise,
            resume_file_id=req.resume_file_id,
            years_experience=years_exp,
            target_role=role_target,
            technical_skills=req.technical_skills,
            current_company=req.current_company,
            jd_file_id=req.jd_file_id,
            jd_text=req.jd_text,
            additional_notes=comments_notes,
        )

        # 5. Create Razorpay order
        from app.integrations.razorpay_client import razorpay_client
        from app.repositories.payment_repository import PaymentRepository
        pay_repo = PaymentRepository(self.db)
        
        rzp_order = await razorpay_client.create_order(
            amount_paise=price_snapshot.amount_paise,
            receipt=booking.booking_reference,
            notes={
                "booking_id": booking.id,
                "candidate_name": user.full_name,
                "category_slug": category.slug,
            }
        )
        await pay_repo.create_payment_order(
            interview_request_id=booking.id,
            razorpay_order_id=rzp_order["id"],
            amount_paise=price_snapshot.amount_paise,
            currency=price_snapshot.currency,
        )

        # 6. Generate access token for seamless candidate authentication
        from app.core.security import create_access_token
        access_token = create_access_token(user_id=user.id, role=user.role, email=user.email)

        return InstantBookingResponse(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            order_id=rzp_order["id"],
            amount_paise=price_snapshot.amount_paise,
            currency=price_snapshot.currency,
            key_id=settings.RAZORPAY_KEY_ID,
            access_token=access_token,
            candidate_name=user.full_name,
            candidate_email=user.email,
            category_title=category.title,
            duration_display=price_snapshot.duration_display,
        )

