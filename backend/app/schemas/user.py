from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.auth import UserResponse, CandidateProfileResponse


class UpdateProfileRequest(BaseModel):
    years_experience: Optional[float] = Field(None, ge=0.0, le=50.0)
    current_company: Optional[str] = Field(None, max_length=150)
    target_role: Optional[str] = Field(None, min_length=2, max_length=150)
    technical_skills: Optional[List[str]] = None
    linkedin_url: Optional[str] = Field(None, max_length=255)


class CandidateFullProfileResponse(BaseModel):
    user: UserResponse
    profile: Optional[CandidateProfileResponse] = None
