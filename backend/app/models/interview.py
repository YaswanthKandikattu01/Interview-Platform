import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InterviewType(Base):
    __tablename__ = "interview_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    prices: Mapped[List["InterviewPrice"]] = relationship("InterviewPrice", back_populates="interview_type")
    interview_requests: Mapped[List["InterviewRequest"]] = relationship("InterviewRequest", back_populates="interview_type")


class InterviewPrice(Base):
    __tablename__ = "interview_prices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_type_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_types.id", ondelete="RESTRICT"), nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, default=19900, nullable=False)  # ₹199
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    duration_min_minutes: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    duration_max_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    duration_display: Mapped[str] = mapped_column(String(50), default="45–60 minutes", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    retired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    interview_type: Mapped["InterviewType"] = relationship("InterviewType", back_populates="prices")


class InterviewRequest(Base):
    __tablename__ = "interview_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_reference: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    interview_type_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_types.id", ondelete="RESTRICT"), nullable=False)
    price_snapshot_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_prices.id", ondelete="RESTRICT"), nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    payment_status: Mapped[str] = mapped_column(String(30), default="CREATED", nullable=False, index=True)
    scheduling_status: Mapped[str] = mapped_column(String(30), default="PAID_AWAITING_CONTACT", nullable=False, index=True)

    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    contact_deadline_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    contact_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    first_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    interview_type: Mapped["InterviewType"] = relationship("InterviewType", back_populates="interview_requests")
    booking_input: Mapped[Optional["BookingInput"]] = relationship("BookingInput", back_populates="interview_request", uselist=False, cascade="all, delete-orphan")
    schedule: Mapped[Optional["InterviewSchedule"]] = relationship("InterviewSchedule", back_populates="interview_request", uselist=False, cascade="all, delete-orphan")
    contact_logs: Mapped[List["SchedulingContactLog"]] = relationship("SchedulingContactLog", back_populates="interview_request", cascade="all, delete-orphan")


class BookingInput(Base):
    __tablename__ = "booking_inputs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    resume_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("stored_files.id", ondelete="RESTRICT"), nullable=False)
    jd_file_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("stored_files.id", ondelete="RESTRICT"), nullable=True)
    jd_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    years_experience: Mapped[float] = mapped_column(Float, nullable=False)
    current_company: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    target_role: Mapped[str] = mapped_column(String(150), nullable=False)
    technical_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    interview_request: Mapped["InterviewRequest"] = relationship("InterviewRequest", back_populates="booking_input")


class InterviewSchedule(Base):
    __tablename__ = "interview_schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    interviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_duration_minutes: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    meeting_platform: Mapped[str] = mapped_column(String(50), default="Google Meet", nullable=False)
    meeting_url: Mapped[str] = mapped_column(Text, nullable=False)
    joining_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="SCHEDULED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    interview_request: Mapped["InterviewRequest"] = relationship("InterviewRequest", back_populates="schedule")
    events: Mapped[List["ScheduleEvent"]] = relationship("ScheduleEvent", back_populates="schedule", cascade="all, delete-orphan")
    feedback: Mapped[Optional["InterviewFeedback"]] = relationship("InterviewFeedback", back_populates="schedule", uselist=False, cascade="all, delete-orphan")


class ScheduleEvent(Base):
    __tablename__ = "schedule_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    schedule_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_schedules.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    previous_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    new_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    new_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    schedule: Mapped["InterviewSchedule"] = relationship("InterviewSchedule", back_populates="events")


class SchedulingContactLog(Base):
    __tablename__ = "scheduling_contact_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_requests.id", ondelete="CASCADE"), nullable=False)
    interviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="EMAIL", nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    contacted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    interview_request: Mapped["InterviewRequest"] = relationship("InterviewRequest", back_populates="contact_logs")


class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_schedule_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_schedules.id", ondelete="CASCADE"), unique=True, nullable=False)
    interviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    strengths: Mapped[str] = mapped_column(Text, nullable=False)
    areas_for_improvement: Mapped[str] = mapped_column(Text, nullable=False)
    technical_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    communication_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_summary: Mapped[str] = mapped_column(Text, nullable=False)
    is_shared_with_candidate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    schedule: Mapped["InterviewSchedule"] = relationship("InterviewSchedule", back_populates="feedback")
