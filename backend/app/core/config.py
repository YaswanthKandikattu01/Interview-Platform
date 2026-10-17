from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    APP_NAME: str = "Premium Mock Interview Platform"
    BUSINESS_TIMEZONE: str = "Asia/Kolkata"
    
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./mock_interviews.db"
    DIRECT_DATABASE_URL: str = "sqlite:///./mock_interviews.db"

    # Security & Tokens
    JWT_SECRET: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    CSRF_SECRET: str = "a3f5c7e9d1b2846f0e9c8a7b6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_VERIFY_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 2

    # Cookies
    COOKIE_DOMAIN: str = ""
    COOKIE_SECURE: bool = False  # Set to True in production
    COOKIE_SAMESITE: str = "lax"

    # Razorpay
    RAZORPAY_KEY_ID: str = "rzp_test_mock_key_id"
    RAZORPAY_KEY_SECRET: str = "mock_secret"
    RAZORPAY_WEBHOOK_SECRET: str = "mock_webhook_secret"

    # Resend
    RESEND_API_KEY: str = "re_mock_key"
    EMAIL_FROM: str = "Interviews <interviews@mockinterviews.dev>"
    ADMIN_EMAIL: str = "admin@mockinterviews.dev"
    SUPPORT_EMAIL: str = "support@mockinterviews.dev"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # File Storage
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    MAX_TOTAL_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Non-negotiable catalog constants
    PACKAGE_PRICE_PAISE: int = 19900  # ₹199
    PACKAGE_DURATION_MIN_MINUTES: int = 45
    PACKAGE_DURATION_MAX_MINUTES: int = 60
    PACKAGE_DURATION_DISPLAY: str = "45–60 minutes"

    # Categories & Pricing Specifications
    ALLOWED_CATEGORIES: List[dict] = [
        {
            "slug": "system-design",
            "title": "System Design Mock Interview",
            "short_description": "Scalability, microservices, distributed caching, databases, and trade-off architecture.",
            "topics": ["High-Level Design", "Distributed Systems", "Database Sharding", "Caching Strategies", "API Gateway & Load Balancing"],
            "display_order": 1,
            "price_paise": 49900,  # ₹499
            "duration_min_minutes": 120,
            "duration_max_minutes": 120,
            "duration_display": "2 Hours (120 mins)",
        },
        {
            "slug": "dsa",
            "title": "DSA Mock Interview",
            "short_description": "Data structures, algorithms, problem decomposition, optimal complexity, and clean code.",
            "topics": ["Dynamic Programming", "Graphs & Trees", "Binary Search", "Heaps & Hash Tables", "Time & Space Complexity"],
            "display_order": 2,
            "price_paise": 19900,  # ₹199
            "duration_min_minutes": 45,
            "duration_max_minutes": 60,
            "duration_display": "45–60 minutes",
        },
        {
            "slug": "ai-engineer",
            "title": "AI Engineer Mock Interview",
            "short_description": "LLM system integration, RAG pipelines, prompt engineering, vector databases, and evaluation.",
            "topics": ["RAG Architecture", "Vector Embeddings & Search", "Fine-Tuning vs Prompting", "Agent Workflows", "LLM Guardrails & Evals"],
            "display_order": 3,
            "price_paise": 19900,  # ₹199
            "duration_min_minutes": 45,
            "duration_max_minutes": 60,
            "duration_display": "45–60 minutes",
        },
        {
            "slug": "full-stack",
            "title": "Full Stack Mock Interview",
            "short_description": "End-to-end web engineering, frontend performance, robust backend APIs, and database patterns.",
            "topics": ["REST & GraphQL APIs", "Full-Stack Security", "State Management", "Data Modeling", "Web Vitals & Performance"],
            "display_order": 4,
            "price_paise": 19900,  # ₹199
            "duration_min_minutes": 45,
            "duration_max_minutes": 60,
            "duration_display": "45–60 minutes",
        },
        {
            "slug": "frontend",
            "title": "Frontend Mock Interview",
            "short_description": "Modern React, Next.js architecture, TypeScript, responsive UX, accessibility, and optimization.",
            "topics": ["React & Component Design", "Rendering Strategies (SSR/SSG/ISR)", "Accessibility (a11y)", "Browser Performance", "State Architecture"],
            "display_order": 5,
            "price_paise": 19900,  # ₹199
            "duration_min_minutes": 45,
            "duration_max_minutes": 60,
            "duration_display": "45–60 minutes",
        },
        {
            "slug": "backend",
            "title": "Backend Mock Interview",
            "short_description": "Concurrency, API resilience, relational/NoSQL schemas, caching, queues, and security.",
            "topics": ["API Design & REST", "SQL & Database Indexing", "Message Queues & Event-Driven", "Authentication & Security", "Performance Profiling"],
            "display_order": 6,
            "price_paise": 19900,  # ₹199
            "duration_min_minutes": 45,
            "duration_max_minutes": 60,
            "duration_display": "45–60 minutes",
        },
        {
            "slug": "resume-review",
            "title": "Resume Review & Career Strategy",
            "short_description": "Detailed line-by-line ATS resume review, bullet-point impact enhancement, and role targeting.",
            "topics": ["ATS Optimization", "Quantified Bullet Points", "Project Framing", "Skills Alignment", "Actionable Improvement Plan"],
            "display_order": 7,
            "price_paise": 11900,  # ₹119
            "duration_min_minutes": 30,
            "duration_max_minutes": 45,
            "duration_display": "Detailed Review & Feedback",
        },
    ]


settings = Settings()
