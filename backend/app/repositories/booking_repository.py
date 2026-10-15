import uuid
import secrets
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.interview import (
    InterviewRequest,
    BookingInput,
    InterviewType,
    InterviewPrice,
    InterviewSchedule,
)
from app.models.file import StoredFile


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_unique_booking_reference() -> str:
    """Generate human-friendly reference e.g. MOCK-2610-A89F"""
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%y%m")
    random_part = secrets.token_hex(2).upper()
    return f"MOCK-{date_part}-{random_part}"


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_stored_file(
        self,
        user_id: str,
        file_purpose: str,
        original_filename: str,
        sanitized_filename: str,
        storage_path: str,
        file_size_bytes: int,
        mime_type: str,
        sha256_checksum: str,
    ) -> StoredFile:
        stored_file = StoredFile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            file_purpose=file_purpose,
            original_filename=original_filename,
            sanitized_filename=sanitized_filename,
            storage_path=storage_path,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            sha256_checksum=sha256_checksum,
            created_at=utc_now(),
        )
        self.db.add(stored_file)
        await self.db.commit()
        await self.db.refresh(stored_file)
        return stored_file

    async def get_stored_file(self, file_id: str) -> Optional[StoredFile]:
        stmt = select(StoredFile).where(StoredFile.id == file_id, StoredFile.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_booking_draft(
        self,
        candidate_id: str,
        interview_type_id: str,
        price_snapshot_id: str,
        amount_paise: int,
        resume_file_id: str,
        years_experience: float,
        target_role: str,
        technical_skills: List[str],
        current_company: Optional[str] = None,
        jd_file_id: Optional[str] = None,
        jd_text: Optional[str] = None,
        additional_notes: Optional[str] = None,
    ) -> InterviewRequest:
        booking_ref = generate_unique_booking_reference()

        interview_request = InterviewRequest(
            id=str(uuid.uuid4()),
            booking_reference=booking_ref,
            candidate_id=candidate_id,
            interview_type_id=interview_type_id,
            price_snapshot_id=price_snapshot_id,
            amount_paise=amount_paise,
            currency="INR",
            payment_status="CREATED",
            scheduling_status="PAID_AWAITING_CONTACT",
            contact_status="PENDING",
            created_at=utc_now(),
        )
        self.db.add(interview_request)
        await self.db.flush()

        booking_input = BookingInput(
            id=str(uuid.uuid4()),
            interview_request_id=interview_request.id,
            resume_file_id=resume_file_id,
            jd_file_id=jd_file_id,
            jd_text=jd_text,
            additional_notes=additional_notes,
            years_experience=years_experience,
            current_company=current_company,
            target_role=target_role,
            technical_skills=technical_skills,
            created_at=utc_now(),
        )
        self.db.add(booking_input)
        await self.db.commit()
        return await self.get_booking_by_id(interview_request.id)

    async def get_booking_by_id(self, booking_id: str) -> Optional[InterviewRequest]:
        stmt = (
            select(InterviewRequest)
            .where(InterviewRequest.id == booking_id)
            .options(
                selectinload(InterviewRequest.interview_type),
                selectinload(InterviewRequest.booking_input),
                selectinload(InterviewRequest.schedule),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_candidate_bookings(self, candidate_id: str) -> List[InterviewRequest]:
        stmt = (
            select(InterviewRequest)
            .where(InterviewRequest.candidate_id == candidate_id)
            .order_by(InterviewRequest.created_at.desc())
            .options(
                selectinload(InterviewRequest.interview_type),
                selectinload(InterviewRequest.booking_input),
                selectinload(InterviewRequest.schedule),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
