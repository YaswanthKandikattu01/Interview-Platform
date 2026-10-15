import os
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user, get_current_verified_user, get_optional_current_user
from app.models.user import User
from app.services.booking_service import BookingService
from app.repositories.user_repository import UserRepository
from app.schemas.booking import (
    FileUploadResponse,
    CreateBookingDraftRequest,
    BookingDetailResponse,
    InstantBookingRequest,
    InstantBookingResponse,
)
from app.schemas.user import UpdateProfileRequest, CandidateProfileResponse
from app.core.config import settings

router = APIRouter(prefix="/candidate", tags=["Candidate Experience"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    file_purpose: str = Form(..., description="'RESUME' or 'JOB_DESCRIPTION'"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Secure file upload with magic-byte validation, ZIP document inspection,
    random UUID path storage, and 5MB size limit.
    Supports guest candidate upload prior to payment checkout.
    """
    if file_purpose not in ["RESUME", "JOB_DESCRIPTION"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file_purpose must be 'RESUME' or 'JOB_DESCRIPTION'"
        )

    service = BookingService(db)
    user_id = current_user.id if current_user else None
    return await service.upload_file(user_id, file, file_purpose)


@router.post("/bookings/instant", response_model=InstantBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_instant_booking(
    payload: InstantBookingRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Frictionless instant booking: candidate provides their professional details,
    the system auto-provisions their candidate profile, generates the Razorpay order
    for 19,900 paise (₹199), and sets authentication cookies.
    Zero password or email-verification barrier before payment.
    """
    service = BookingService(db)
    res = await service.create_instant_booking(payload)

    # Set auth cookie for immediate session
    response.set_cookie(
        key="access_token",
        value=res.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    return res


@router.post("/bookings/draft", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_booking_draft(
    payload: CreateBookingDraftRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates an initial booking request for ₹199 (19,900 paise).
    Candidate must have a verified email.
    """
    service = BookingService(db)
    return await service.create_booking_draft(current_user.id, payload)


@router.get("/bookings", response_model=List[BookingDetailResponse], status_code=status.HTTP_200_OK)
async def list_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all mock interview bookings for the logged-in candidate."""
    service = BookingService(db)
    return await service.list_candidate_bookings(current_user.id)


@router.get("/bookings/{booking_id}", response_model=BookingDetailResponse, status_code=status.HTTP_200_OK)
async def get_booking_detail(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single booking detail. Anti-IDOR: Candidates can only access their own bookings."""
    service = BookingService(db)
    return await service.get_candidate_booking(current_user.id, booking_id)


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Secure authenticated file download. Candidate can only download their own uploaded files."""
    service = BookingService(db)
    file_record = await service.get_file_for_candidate(current_user.id, file_id)

    if not os.path.exists(file_record.storage_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File content does not exist on storage system"
        )

    return FileResponse(
        path=file_record.storage_path,
        media_type=file_record.mime_type,
        filename=file_record.sanitized_filename,
    )


@router.get("/profile", response_model=CandidateProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get profile of current logged-in candidate."""
    if not current_user.profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return CandidateProfileResponse.model_validate(current_user.profile)


@router.put("/profile", response_model=CandidateProfileResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile fields for the candidate."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if payload.years_experience is not None:
        profile.years_experience = payload.years_experience
    if payload.current_company is not None:
        profile.current_company = payload.current_company.strip() or None
    if payload.target_role is not None:
        profile.target_role = payload.target_role.strip()
    if payload.technical_skills is not None:
        profile.technical_skills = payload.technical_skills
    if payload.linkedin_url is not None:
        profile.linkedin_url = payload.linkedin_url.strip() or None

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return CandidateProfileResponse.model_validate(profile)
