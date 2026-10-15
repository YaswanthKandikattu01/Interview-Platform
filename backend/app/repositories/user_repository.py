import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import User, RefreshToken, CandidateProfile
from app.core.security import hash_password, hash_token, generate_random_token
from app.core.config import settings


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.profile))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.email == email.strip().lower())
            .options(selectinload(User.profile))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        phone: str,
        role: str = "CANDIDATE",
        is_email_verified: bool = False,
        years_experience: float = 0.0,
        current_company: Optional[str] = None,
        target_role: str = "",
        technical_skills: Optional[List[str]] = None,
        raw_verify_token: Optional[str] = None,
    ) -> tuple[User, str]:
        hashed_pwd = hash_password(password)
        if not raw_verify_token:
            raw_verify_token = generate_random_token(32)
        verify_token_hash = hash_token(raw_verify_token)

        user = User(
            id=str(uuid.uuid4()),
            email=email.strip().lower(),
            password_hash=hashed_pwd,
            full_name=full_name.strip(),
            phone=phone.strip(),
            role=role,
            is_email_verified=is_email_verified,
            email_verification_token_hash=verify_token_hash,
            email_verification_sent_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.flush()

        if role == "CANDIDATE":
            profile = CandidateProfile(
                id=str(uuid.uuid4()),
                user_id=user.id,
                years_experience=years_experience,
                current_company=current_company.strip() if current_company else None,
                target_role=target_role.strip(),
                technical_skills=technical_skills or [],
            )
            self.db.add(profile)
            await self.db.flush()

        await self.db.commit()
        created_user = await self.get_by_id(user.id)
        return created_user, raw_verify_token

    async def create_refresh_token(
        self,
        user_id: str,
        raw_token: str,
        family_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> RefreshToken:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_hash = hash_token(raw_token)
        actual_family_id = family_id or str(uuid.uuid4())

        refresh_token = RefreshToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            family_id=actual_family_id,
            is_revoked=False,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            created_at=now,
        )
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, raw_token: str) -> Optional[RefreshToken]:
        token_hash = hash_token(raw_token)
        stmt = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .options(selectinload(RefreshToken.user))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_id: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def revoke_token_family(self, family_id: str) -> None:
        """Revoke all tokens in a family when reuse/theft is detected."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id)
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke all tokens for a user upon global logout or security reset."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def set_email_verified(self, user_id: str) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                is_email_verified=True,
                email_verification_token_hash=None,
                updated_at=datetime.now(timezone.utc)
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def set_password_reset_token(self, user_id: str, raw_token: str) -> None:
        token_hash = hash_token(raw_token)
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                password_reset_token_hash=token_hash,
                password_reset_sent_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def reset_password(self, user_id: str, new_password: str) -> None:
        hashed_pwd = hash_password(new_password)
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                password_hash=hashed_pwd,
                password_reset_token_hash=None,
                updated_at=datetime.now(timezone.utc)
            )
        )
        await self.db.execute(stmt)
        # Also revoke all active refresh tokens for security
        await self.revoke_all_user_tokens(user_id)
        await self.db.commit()

    async def find_user_by_verification_token(self, raw_token: str) -> Optional[User]:
        token_hash = hash_token(raw_token)
        stmt = select(User).where(User.email_verification_token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_reset_token(self, raw_token: str) -> Optional[User]:
        token_hash = hash_token(raw_token)
        stmt = select(User).where(User.password_reset_token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
