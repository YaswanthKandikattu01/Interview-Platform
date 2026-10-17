from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_id: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    file_purpose: str


class CreateBookingDraftRequest(BaseModel):
    category_slug: str = Field(..., min_length=2, max_length=50)
    resume_file_id: str = Field(..., min_length=10)
    jd_file_id: Optional[str] = None
    jd_text: Optional[str] = Field(None, max_length=10000)
    additional_notes: Optional[str] = Field(None, max_length=2000)
    years_experience: float = Field(..., ge=0.0, le=50.0)
    target_role: str = Field(..., min_length=2, max_length=150)
    current_company: Optional[str] = Field(None, max_length=150)
    technical_skills: List[str] = Field(default_factory=list)


class BookingDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    booking_reference: str
    amount_paise: int
    currency: str
    payment_status: str
    scheduling_status: str
    category_title: str
    category_slug: str
    duration_display: str
    years_experience: float
    target_role: str
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    meeting_url: Optional[str] = None
    status_headline: str
    status_message: str
    created_at: datetime


class InstantBookingRequest(BaseModel):
    category_slug: str = Field(..., min_length=2, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=150)
    email: str = Field(..., min_length=5, max_length=255)
    resume_file_id: str = Field(..., min_length=10)
    phone: Optional[str] = Field(None, max_length=25)
    comments: Optional[str] = Field(None, max_length=3000)
    years_experience: Optional[float] = Field(0.0, ge=0.0, le=50.0)
    target_role: Optional[str] = Field("Candidate", max_length=150)
    current_company: Optional[str] = Field(None, max_length=150)
    technical_skills: List[str] = Field(default_factory=list)
    jd_file_id: Optional[str] = None
    jd_text: Optional[str] = Field(None, max_length=10000)
    additional_notes: Optional[str] = Field(None, max_length=3000)


class InstantBookingResponse(BaseModel):
    booking_id: str
    booking_reference: str
    order_id: str
    amount_paise: int
    currency: str
    key_id: str
    access_token: str
    candidate_name: str
    candidate_email: str
    category_title: str
    duration_display: str

