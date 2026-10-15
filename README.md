# Premium Human-Led Mock Interview Platform

A production-ready, paid human-led mock interview platform for technical candidates in India preparing for software engineering roles.

---

## 1. Architectural Invariants & Non-Negotiables
- **100% Human-Led Sessions:** All interviews are conducted live by a senior technical interviewer (who also acts as the administrator in V1). Zero AI bots or synthetic interviewers.
- **Exactly 6 Interview Categories:**
  1. System Design Mock Interview
  2. DSA Mock Interview
  3. AI Engineer Mock Interview
  4. Full Stack Mock Interview
  5. Frontend Mock Interview
  6. Backend Mock Interview
  *(No DevOps, Data Analyst, Behavioral, or other categories).*
- **Single Standard Package:** Advertised as **45–60 minutes for ₹199** (19,900 paise stored in database as integer). No 30m/60m options, no duration selection dropdown, no ₹399 plan.
- **Interviewer-Driven Scheduling:** Absolutely **no public availability calendar or time-slot picker**. The interviewer coordinates schedule directly via email on the same calendar day of payment.
- **Business Timezone:** `Asia/Kolkata` (IST).
- **Same-Day Contact Guarantee:** Candidates who pay between 08:00 AM – 08:00 PM IST receive personal contact by 11:59 PM IST same day; payments after 08:00 PM IST receive contact by 12:00 PM IST next day (14h buffer).

---

## 2. Technology Stack
- **Frontend:** Next.js 14 App Router, React 18, TypeScript (strict mode), Tailwind CSS, Lucide Icons.
- **Backend:** Python 3.11/3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x async, Alembic migrations.
- **Database:** Supabase Managed PostgreSQL (PostgreSQL 16).
- **Background Worker:** Redis 7 with Transactional Outbox pattern worker (`app.workers.outbox_worker`).
- **Payments:** Razorpay Orders, HMAC-SHA256 signature verification, idempotent webhooks, and admin refunds.
- **Transactional Emails:** Resend API integration with retry backoff, dead-letter queue, and RFC 5545 `.ics` calendar generation.

---

## 3. Security Highlights
- **Argon2id Password Hashing:** Memory-hard password hashing with salt and pepper.
- **Token Security:** Short-lived JWT access tokens (15 mins), rotating refresh tokens (7 days) with SHA-256 hash storage and OWASP family-based token reuse detection.
- **Double Submit CSRF Protection:** Cryptographically bound tokens for all mutation requests.
- **File Upload Protection:** True magic-byte verification (`%PDF-` for PDF, internal ZIP XML examination for DOCX), 5 MB file size limit, randomized UUID storage paths.
- **Anti-IDOR:** Strict user ownership boundaries enforced on all bookings and file downloads.
- **Zero Double-Booking Invariant:** Interviewer schedule overlap prevention preventing collision of active sessions.

---

## 4. Getting Started

### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ and npm
- PostgreSQL 16 (or Docker Compose)
- Redis 7

### Backend Setup
```bash
# Navigate to repository root
cd mock-interview-platform

# Activate Python virtual environment
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt

# Setup environment variables
cp .env.example .env

# Run database migrations
alembic -c backend/alembic.ini upgrade head

# Start FastAPI server
uvicorn app.main:app --app-dir backend --reload --port 8000
```
Backend runs at `http://localhost:8000` (Interactive Swagger docs: `http://localhost:8000/docs`).

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
npm start
```
Frontend runs at `http://localhost:3000`.

---

## 5. Running the Test Suite
The backend includes 33 comprehensive automated tests covering authentication, catalog, candidate experience, file security, anti-IDOR, payments, webhooks, outbox worker, email rendering, calendar generation, and interviewer scheduling overlap prevention:

```powershell
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest -v backend\tests
```

All 33 tests execute in under 7 seconds with 100% pass rate.

---

## 6. Project Directory Map
```
mock-interview-platform/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI API routers (auth, candidate, catalog, payments, admin)
│   │   ├── core/            # Database engine, security, JWT/CSRF, calendar generation, config
│   │   ├── integrations/    # Razorpay client & Resend client
│   │   ├── models/          # SQLAlchemy 2.x declarative models
│   │   ├── repositories/    # Database query layer (Admin, Booking, Catalog, Payment, User)
│   │   ├── schemas/         # Pydantic v2 validation contracts
│   │   ├── services/        # Business logic services
│   │   ├── templates/       # HTML & text transactional email templates
│   │   └── workers/         # Transactional outbox polling worker
│   ├── tests/               # 33 unit and integration tests
│   ├── alembic/             # Database schema migrations
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── admin/           # Interviewer operations & metrics portal
│   │   ├── book/[slug]/     # Multi-step candidate booking journey
│   │   ├── dashboard/       # Candidate dashboard & session viewer
│   │   ├── login/           # Secure login
│   │   ├── register/        # Candidate registration
│   │   ├── verify-email/    # Email verification
│   │   ├── terms/           # Terms of Service
│   │   ├── privacy/         # Privacy Policy
│   │   └── refund-policy/   # Cancellation & Refund Policy
│   ├── components/          # Reusable UI components (Navbar, Footer)
│   ├── services/            # API client with credentials & CSRF
│   └── types/               # TypeScript interfaces
├── docs/                    # Architecture diagrams & specifications
├── docker-compose.yml       # Local PostgreSQL + Redis + Backend containerization
└── README.md
```

---

## 7. Operational Runbook

### Interviewer Personal Contact Workflow
1. Candidate books and completes payment (₹199 / 19,900 paise).
2. Payment is verified via Razorpay webhook / checkout verification.
3. An automatic confirmation email is dispatched to the candidate and an alert email is dispatched to the interviewer with candidate dossier and the Asia/Kolkata SLA deadline.
4. Interviewer logs into `/admin`, opens the candidate dossier, and sends a personal scheduling email before the deadline.
5. Interviewer clicks **Log Contact** to record the outreach notes, which satisfies the SLA audit trail.
6. Once a mutually agreeable time is decided, the interviewer clicks **Schedule**, selects a 45–60 minute slot, enters the Google Meet / Zoom link, and confirms.
7. An email with meeting details and an RFC 5545 `.ics` calendar invitation is automatically dispatched to the candidate.
8. After conducting the session, the interviewer clicks **Complete** and inputs structured rating evaluation feedback (1–5 scale, strengths, areas of improvement).
