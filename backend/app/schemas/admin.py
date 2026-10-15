from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class RecordContactRequest(BaseModel):
    channel: str = Field(default="EMAIL", max_length=50)
    notes: str = Field(min_length=3, max_length=2000)


class ScheduleInterviewRequest(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime
    meeting_platform: str = Field(default="Google Meet", max_length=50)
    meeting_url: str = Field(min_length=5, max_length=500)
    joining_instructions: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("scheduled_end")
    @classmethod
    def validate_duration(cls, v: datetime, info):
        start = info.data.get("scheduled_start")
        if start:
            if v <= start:
                raise ValueError("scheduled_end must be strictly after scheduled_start")
            duration_minutes = (v - start).total_seconds() / 60
            if duration_minutes < 45 or duration_minutes > 60:
                raise ValueError(f"Interview duration must be between 45 and 60 minutes. Got {duration_minutes:.1f} minutes.")
        return v


class RescheduleInterviewRequest(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime
    meeting_url: Optional[str] = Field(default=None, max_length=500)
    reason: str = Field(min_length=5, max_length=1000)

    @field_validator("scheduled_end")
    @classmethod
    def validate_duration(cls, v: datetime, info):
        start = info.data.get("scheduled_start")
        if start:
            if v <= start:
                raise ValueError("scheduled_end must be strictly after scheduled_start")
            duration_minutes = (v - start).total_seconds() / 60
            if duration_minutes < 45 or duration_minutes > 60:
                raise ValueError(f"Interview duration must be between 45 and 60 minutes. Got {duration_minutes:.1f} minutes.")
        return v


class CompleteInterviewRequest(BaseModel):
    strengths: str = Field(min_length=5)
    areas_for_improvement: str = Field(min_length=5)
    technical_rating: int = Field(ge=1, le=5)
    communication_rating: int = Field(ge=1, le=5)
    recommendation_summary: str = Field(min_length=5)
    is_shared_with_candidate: bool = False


class CancelInterviewRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)
    initiate_refund: bool = False


class AdminOverviewResponse(BaseModel):
    total_revenue_paise: int
    total_revenue_inr: float
    total_bookings: int
    awaiting_contact_count: int
    overdue_contact_count: int
    scheduled_count: int
    completed_count: int
    cancelled_count: int
    upcoming_interviews: List[Dict[str, Any]]
