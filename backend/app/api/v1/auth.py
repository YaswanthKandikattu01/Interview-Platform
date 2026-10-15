from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    EmailVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    AuthResponse,
    UserResponse,
    CandidateProfileResponse,
)
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
    # Set access token in HttpOnly cookie (15 mins)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    # Set refresh token in HttpOnly cookie (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/api/v1/auth",  # Restricted path for refresh token
    )
    # Set CSRF token in readable cookie for JS double-submit header
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    response.delete_cookie(key="csrf_token", path="/")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user, verify_token = await service.register(req)
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user_id": user.id,
        "email": user.email,
        # For development / testing convenience, verify_token is included when APP_ENV == 'development'
        "dev_verification_token": verify_token if settings.APP_ENV == "development" else None
    }


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    req: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user = await service.verify_email(req.token)
    return {
        "message": "Email verified successfully. You can now log in.",
        "user_id": user.id,
        "email": user.email,
        "is_email_verified": True
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None
    auth_resp, refresh_token = await service.login(req, user_agent, client_ip)
    
    set_auth_cookies(response, auth_resp.access_token, refresh_token, auth_resp.csrf_token)
    return auth_resp


@router.post("/refresh", response_model=AuthResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    raw_token = None
    if body and body.refresh_token:
        raw_token = body.refresh_token
    else:
        raw_token = request.cookies.get("refresh_token")

    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None

    auth_resp, new_refresh_token = await service.rotate_refresh_token(
        raw_refresh_token=raw_token,
        user_agent=user_agent,
        ip_address=client_ip
    )

    set_auth_cookies(response, auth_resp.access_token, new_refresh_token, auth_resp.csrf_token)
    return auth_resp


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    raw_token = None
    if body and body.refresh_token:
        raw_token = body.refresh_token
    else:
        raw_token = request.cookies.get("refresh_token")

    await service.logout(raw_token)
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    profile_data = None
    if current_user.profile:
        profile_data = CandidateProfileResponse.model_validate(current_user.profile)
    return {
        "user": UserResponse.model_validate(current_user),
        "profile": profile_data
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    reset_token = await service.forgot_password(req.email)
    return {
        "message": "If this email exists in our records, a password reset link has been dispatched.",
        "dev_reset_token": reset_token if settings.APP_ENV == "development" else None
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    await service.reset_password(req.token, req.new_password)
    return {"message": "Password reset successfully. You may now log in with your new password."}
