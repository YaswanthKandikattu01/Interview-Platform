# Premium Human-Led Mock Interview Platform

A production-ready, human-led mock interview platform for technical candidates in India preparing for software engineering roles.

## Core Features & Guarantees
- **Human-Led Sessions:** Conducted by a dedicated senior technical interviewer / administrator (no AI interviewers).
- **Strict Catalog (Exactly 6 Categories):**
  1. System Design Mock Interview
  2. DSA Mock Interview
  3. AI Engineer Mock Interview
  4. Full Stack Mock Interview
  5. Frontend Mock Interview
  6. Backend Mock Interview
- **Single Standard Package:** 45–60 minutes for ₹199 (19,900 paise).
- **Interviewer-Driven Scheduling:** No public calendars or slot pickers. The interviewer coordinates date and time directly via email on the same calendar day of payment (Asia/Kolkata timezone).
- **Secure Payments:** Full Razorpay integration with backend order generation, raw HMAC signature verification, and transactional webhooks.
- **Reliable Transactional Emails:** Resend integration using a resilient Transactional Outbox pattern.
- **Enterprise-Grade Security:** Custom Argon2id authentication, rotating refresh tokens in HttpOnly cookies, CSRF protection, magic-byte file upload validation, and PostgreSQL GiST exclusion constraints to prevent overlapping interviews.

## Technology Stack
- **Frontend:** Next.js 14/15 App Router, React, TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons
- **Backend:** Python 3.11/3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x async, Alembic
- **Database:** Supabase Managed PostgreSQL
- **Worker / Queues:** Redis with Arq / Celery
- **Payment Gateway:** Razorpay
- **Email Service:** Resend

## Project Structure
```
mock-interview-platform/
├── frontend/          # Next.js App Router application
├── backend/           # FastAPI application
├── docs/              # Architectural diagrams and specifications
├── infrastructure/    # Deployment configs and scripts
├── docker-compose.yml # Local development orchestration
├── .env.example       # Sample environment configuration
└── README.md
```

## Current Status
- **Stage 1 (Architecture & System Design):** Complete. Pending final stakeholder approval before implementing Stage 2 code.
