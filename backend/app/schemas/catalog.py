from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InterviewPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_type_id: str
    amount_paise: int
    currency: str
    duration_min_minutes: int
    duration_max_minutes: int
    duration_display: str
    is_active: bool
    created_at: datetime


class InterviewCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    title: str
    short_description: str
    detailed_topics: List[str]
    display_order: int
    is_active: bool
    active_price: Optional[InterviewPriceResponse] = None


class CanonicalPricingResponse(BaseModel):
    amount_paise: int = 19900
    currency: str = "INR"
    duration_display: str = "45–60 minutes"
    duration_min_minutes: int = 45
    duration_max_minutes: int = 60
    price_formatted: str = "₹199"
    guarantee: str = "One-on-one live mock interview conducted by a human expert interviewer."
    scheduling_promise: str = "Personal interviewer outreach on the same day of payment (Asia/Kolkata)."


class UpdateCategoryPriceRequest(BaseModel):
    amount_paise: int = Field(..., gt=0, description="Amount in integer paise (e.g. 19900 for ₹199)")
