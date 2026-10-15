from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    phone: str = Field(..., min_length=7, max_length=20)


class RegisterRequest(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    years_experience: float = Field(default=0.0, ge=0.0, le=50.0)
    current_company: Optional[str] = Field(default=None, max_length=150)
    target_role: str = Field(..., min_length=2, max_length=150)
    technical_skills: List[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class EmailVerificationRequest(BaseModel):
    token: str = Field(..., min_length=10)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None  # Can come from HttpOnly cookie or request body


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    phone: str
    role: str
    is_email_verified: bool
    is_active: bool


class CandidateProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    years_experience: float
    current_company: Optional[str]
    target_role: str
    technical_skills: List[str]
    linkedin_url: Optional[str]


class AuthResponse(BaseModel):
    user: UserResponse
    profile: Optional[CandidateProfileResponse] = None
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    csrf_token: str
    message: Optional[str] = None
