from datetime import datetime, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user import User, RefreshToken
from app.core.security import (
    verify_password,
    create_access_token,
    generate_random_token,
    generate_csrf_token,
)
from app.core.config import settings
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse, CandidateProfileResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, req: RegisterRequest) -> Tuple[User, str]:
        existing = await self.repo.get_by_email(req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )

        user, raw_verify_token = await self.repo.create_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            phone=req.phone,
            role="CANDIDATE",
            is_email_verified=False,
            years_experience=req.years_experience,
            current_company=req.current_company,
            target_role=req.target_role,
            technical_skills=req.technical_skills,
        )
        return user, raw_verify_token

    async def verify_email(self, token: str) -> User:
        user = await self.repo.find_user_by_verification_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        await self.repo.set_email_verified(user.id)
        return user

    async def login(
        self,
        req: LoginRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[AuthResponse, str]:
        user = await self.repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been suspended"
            )

        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
        )

        raw_refresh_token = generate_random_token(48)
        await self.repo.create_refresh_token(
            user_id=user.id,
            raw_token=raw_refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        csrf_token = generate_csrf_token()

        profile_resp = None
        if user.profile:
            profile_resp = CandidateProfileResponse.model_validate(user.profile)

        auth_response = AuthResponse(
            user=UserResponse.model_validate(user),
            profile=profile_resp,
            access_token=access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            csrf_token=csrf_token,
            message="Login successful"
        )
        return auth_response, raw_refresh_token

    async def rotate_refresh_token(
        self,
        raw_refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[AuthResponse, str]:
        if not raw_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_record = await self.repo.get_refresh_token(raw_refresh_token)
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # REUSE DETECTION: If token is already revoked, an attacker or compromised client attempted replay!
        if token_record.is_revoked:
            await self.repo.revoke_token_family(token_record.family_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token reuse detected. All sessions in this family have been terminated for security.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check expiration
        now = datetime.now(timezone.utc)
        token_expires = token_record.expires_at
        if token_expires.tzinfo is None:
            token_expires = token_expires.replace(tzinfo=timezone.utc)

        if token_expires < now:
            await self.repo.revoke_refresh_token(token_record.id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Revoke the used token
        await self.repo.revoke_refresh_token(token_record.id)

        # Create new token in the same family
        new_raw_refresh_token = generate_random_token(48)
        await self.repo.create_refresh_token(
            user_id=token_record.user_id,
            raw_token=new_raw_refresh_token,
            family_id=token_record.family_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        user = await self.repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account inactive or deleted",
            )

        new_access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
        )
        new_csrf_token = generate_csrf_token()

        profile_resp = None
        if user.profile:
            profile_resp = CandidateProfileResponse.model_validate(user.profile)

        auth_response = AuthResponse(
            user=UserResponse.model_validate(user),
            profile=profile_resp,
            access_token=new_access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            csrf_token=new_csrf_token,
            message="Token refreshed successfully"
        )
        return auth_response, new_raw_refresh_token

    async def logout(self, raw_refresh_token: Optional[str]) -> None:
        if raw_refresh_token:
            token_record = await self.repo.get_refresh_token(raw_refresh_token)
            if token_record:
                await self.repo.revoke_refresh_token(token_record.id)

    async def forgot_password(self, email: str) -> Optional[str]:
        user = await self.repo.get_by_email(email)
        if not user:
            # Return None silently to avoid email enumeration
            return None
        raw_reset_token = generate_random_token(32)
        await self.repo.set_password_reset_token(user.id, raw_reset_token)
        return raw_reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        user = await self.repo.find_user_by_reset_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token"
            )
        await self.repo.reset_password(user.id, new_password)
        return True
