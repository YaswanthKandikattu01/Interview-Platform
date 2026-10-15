import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base, async_session_factory
from app.models import User, InterviewType, InterviewPrice
from app.core.security import hash_password
from app.api.v1 import api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_interview_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables if on SQLite / dev
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")

    # Seed Admin User if not existing
    async with async_session_factory() as session:
        from app.repositories.user_repository import UserRepository
        repo = UserRepository(session)
        admin_user = await repo.get_by_email(settings.ADMIN_EMAIL)
        if not admin_user:
            logger.info("Seeding initial administrator user...")
            admin_user, _ = await repo.create_user(
                email=settings.ADMIN_EMAIL,
                password="AdminSecurePassword123!",
                full_name="Interviewer Admin",
                phone="+919876543210",
                role="ADMIN",
                is_email_verified=True,
            )
            logger.info("Default administrator seeded successfully.")

    yield
    # Shutdown
    logger.info("Shutting down API service...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Premium Human-Led Mock Interview Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Our team has been notified."}
    )


# Mount API V1
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs" if settings.APP_ENV != "production" else None
    }
