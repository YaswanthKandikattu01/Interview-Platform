import asyncio
from app.core.database import async_session_factory
from app.repositories.user_repository import UserRepository
from app.core.config import settings


async def main():
    async with async_session_factory() as db:
        user_repo = UserRepository(db)
        admin = await user_repo.get_by_email(settings.ADMIN_EMAIL)
        if not admin:
            admin, _ = await user_repo.create_user(
                email=settings.ADMIN_EMAIL,
                password="AdminSecurePassword123!",
                full_name="Interviewer & Administrator",
                phone="+919876543210",
                role="ADMIN",
                is_email_verified=True,
            )
            print(f"Created admin: {admin.email} (Role: {admin.role})")
        else:
            admin.role = "ADMIN"
            admin.is_email_verified = True
            await db.commit()
            print(f"Updated admin: {admin.email} (Role: {admin.role})")


if __name__ == "__main__":
    asyncio.run(main())
