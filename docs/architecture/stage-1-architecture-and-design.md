# Premium Human-Led Mock Interview Platform
## Stage 1: System Architecture, Database Schema & Operational Design Specification

**Document Version:** 1.0.0  
**Target Environment:** India (INR, Asia/Kolkata IST)  
**Author:** Principal Software Architect & Engineering Team  
**Status:** Pending Stakeholder Approval (Stage 1 Gate)

---

## 1. Executive Summary & Non-Negotiable Core Model

This platform is a commercial, human-led mock interview SaaS built specifically for technical candidates in India preparing for software engineering roles. In Version 1, exactly **one human interviewer** (who also serves as administrator) conducts all sessions. There are **no AI interviewers**, **no multiple interviewers**, and **no automated self-service scheduling calendars**.

### 1.1 Non-Negotiable Business Invariants
1. **Catalog Integrity (Exactly 6 Categories):**
   - *System Design Mock Interview*
   - *DSA Mock Interview*
   - *AI Engineer Mock Interview*
   - *Full Stack Mock Interview*
   - *Frontend Mock Interview*
   - *Backend Mock Interview*
   *(No HR, Behavioral, Data Analyst, DevOps, or auxiliary categories permitted).*
2. **Single Standard Package:**
   - **Duration:** 45–60 minutes (conducted by the human interviewer within this window; no duration dropdown or 30/60m options).
   - **Price:** Exactly **₹199** (stored as **19,900 paise** integer).
   - **No ₹399 plan, no discount codes/coupons, no subscriptions in V1.**
3. **Interviewer-Driven Scheduling:**
   - Candidates **never** select dates or slots on the site.
   - No public availability calendar, time-slot picker, temporary slot reservation, or slot-holding countdown timers.
   - Scheduling is coordinated personally by the interviewer via direct email on the same calendar day of payment.

---

## 2. Operational Risk Analysis & SLA Policies

### 2.1 The "Midnight Booking" Operational Risk
* **The Problem:** The platform guarantees personal interviewer contact on the *same calendar day* of payment in timezone `Asia/Kolkata` (IST). If a candidate pays at 11:45 PM IST, a rigid "same calendar day" rule gives the single human interviewer only 15 minutes before the SLA is breached, leading to unrealistic operational pressure and inevitable false failures.
* **Recommended & Customer-Visible Cutoff Policy:**
  - **Standard Day Window (08:00 AM IST – 08:00 PM IST):** Candidate receives guaranteed personal scheduling outreach from the interviewer by **11:59 PM IST on the same calendar day**.
  - **Evening / Night Window (08:01 PM IST – 07:59 AM IST):** Candidate receives guaranteed personal scheduling outreach within **14 hours** (and no later than **12:00 PM IST the following day**).
  - **Candidate Visibility:** This cutoff policy is explicitly rendered on the checkout summary, the post-payment success confirmation, and the candidate dashboard (e.g., *"Payment received at 10:15 PM IST. Because you booked after 8:00 PM, your interviewer will personally email you by 12:00 PM IST tomorrow."*).
  - **Admin Alerts:** If 75% of the contact deadline has elapsed without contact being logged in the admin panel, an automated high-priority reminder is dispatched to the admin.

### 2.2 Cancellation & Refund Policy Proposal
| Scenario | Eligibility | Refund / Action | Rationale |
| :--- | :--- | :--- | :--- |
| **Cancellation before interviewer outreach** | Any time prior to first personal contact | **100% Refund (₹199)** | No interviewer time was yet allocated to slot coordination. |
| **Cancellation after outreach, but >12h before scheduled time** | Candidate requests cancellation | **100% Refund or Free Reschedule** | Gives reasonable advance notice to free up the interviewer's calendar. |
| **Rescheduling requested >6h before scheduled time** | Candidate requests new time | **1 Free Reschedule** | Accommodates unexpected candidate emergencies. |
| **Cancellation / Reschedule <6h before interview** | Last-minute request | **Case-by-case / 50% refund** (Admin override enabled) | Protects interviewer from dedicated slot blocking. |
| **Candidate No-Show (15m grace period)** | Candidate fails to join | **No automatic refund** (Admin can grant one-time reschedule) | Slot was reserved and interviewer waited on call. |
| **Interviewer Contact SLA Breach (>24h without contact)** | System/Admin delay | **Automatic 100% Refund + Priority Reschedule Voucher** | Protects customer trust if the single interviewer is incapacitated. |
| **Interviewer Cancellation / Emergency** | Interviewer cancels | **100% Immediate Refund or Priority Reschedule** | Platform guarantee. |

*Refunds will be processed via Razorpay Refunds API directly to the original payment source within 5–7 business days.*

---

## 3. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Client ["Client Layer (Responsive Web)"]
        BrowserMobile["Mobile Browser (PWA / Responsive)"]
        BrowserDesktop["Desktop / Laptop Browser"]
    end

    subgraph CDN_Gateway ["Edge & Routing Layer"]
        Cloudflare["Cloudflare / Reverse Proxy (SSL, DDoS, WAF)"]
    end

    subgraph FrontendApp ["Frontend Application (Next.js 14 App Router)"]
        NextServer["Next.js Node.js Server (SSR & Static Pages)"]
        ClientPages["Public Landing, Categories, Auth, Checkout, Dashboards"]
    end

    subgraph BackendAPI ["Backend Core API (FastAPI - Modular Monolith)"]
        APIRouter["API Router (/api/v1)"]
        AuthModule["Auth Service (Argon2id, JWT, Rotating Refresh)"]
        BookingModule["Booking & Catalog Service (₹199 / 19,900 paise)"]
        PaymentModule["Payment Service (Razorpay Orders, HMAC Verification)"]
        SchedulingModule["Scheduling & SLA Engine (Asia/Kolkata)"]
        OutboxWorkerBridge["Transactional Outbox Bridge"]
    end

    subgraph DataStorage ["Data & Cache Layer"]
        PostgreSQL[("Supabase Managed PostgreSQL (authoritative)")]
        RedisQueue[("Redis (Broker, Rate Limiter & Token Revocation)")]
    end

    subgraph BackgroundAsync ["Background Processing (Arq / Celery Worker)"]
        OutboxWorker["Outbox Notification Worker"]
        ReconciliationWorker["Payment Reconciliation Job"]
        RetentionWorker["File Retention Cleanup (30 Days)"]
        SlaAlertWorker["SLA Contact Deadline Monitor"]
    end

    subgraph ExternalServices ["Third-Party Integrations"]
        RazorpayGateway["Razorpay (Orders, Webhooks, Refunds)"]
        ResendEmail["Resend API (Transactional Emails)"]
        StorageEngine["Encrypted Private File Store (Local / Supabase Bucket)"]
    end

    ClientMobile & BrowserDesktop --> Cloudflare
    Cloudflare --> NextServer
    NextServer --> ClientPages
    ClientPages -->|REST + Secure Cookies| APIRouter

    APIRouter --> AuthModule & BookingModule & PaymentModule & SchedulingModule
    AuthModule --> PostgreSQL & RedisQueue
    BookingModule --> PostgreSQL
    PaymentModule --> PostgreSQL & RazorpayGateway
    SchedulingModule --> PostgreSQL

    PaymentModule -.->|Emit Events| OutboxWorkerBridge
    OutboxWorkerBridge --> PostgreSQL

    RedisQueue --> BackgroundAsync
    PostgreSQL <--> BackgroundAsync
    OutboxWorker --> ResendEmail
    BookingModule --> StorageEngine

    RazorpayGateway -->|Signed Webhook| PaymentModule
```

---

## 4. Entity-Relationship (ER) Model & Database Schema

The database relies on **PostgreSQL 15+** with the `btree_gist` extension enabled to enforce non-overlapping scheduled interview ranges at the relational engine level.

### 4.1 ER Diagram

```mermaid
erDiagram
    USERS ||--o{ REFRESH_TOKENS : has
    USERS ||--o| CANDIDATE_PROFILES : has
    USERS ||--o{ INTERVIEW_REQUESTS : books
    USERS ||--o{ AUDIT_LOGS : triggers

    INTERVIEW_TYPES ||--|{ INTERVIEW_PRICES : defines
    INTERVIEW_TYPES ||--o{ INTERVIEW_REQUESTS : categorized_under
    INTERVIEW_PRICES ||--o{ INTERVIEW_REQUESTS : charged_at

    INTERVIEW_REQUESTS ||--|| BOOKING_INPUTS : includes
    INTERVIEW_REQUESTS ||--o| INTERVIEW_SCHEDULES : scheduled_as
    INTERVIEW_REQUESTS ||--o{ SCHEDULING_CONTACT_LOGS : tracks_contact
    INTERVIEW_REQUESTS ||--o{ PAYMENTS : paid_via
    INTERVIEW_REQUESTS ||--o{ REFUNDS : refunded_via
    INTERVIEW_REQUESTS ||--o{ NOTIFICATIONS : notifies

    BOOKING_INPUTS ||--o| STORED_FILES : resume_file
    BOOKING_INPUTS ||--o| STORED_FILES : jd_file

    INTERVIEW_SCHEDULES ||--o{ SCHEDULE_EVENTS : logs_history
    INTERVIEW_SCHEDULES ||--o| INTERVIEW_FEEDBACK : receives

    PAYMENTS ||--o{ WEBHOOK_EVENTS : associated_with
```

### 4.2 Comprehensive PostgreSQL Schema (DDL)

```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Enum Types
CREATE TYPE user_role AS ENUM ('CANDIDATE', 'ADMIN');
CREATE TYPE payment_status_enum AS ENUM ('CREATED', 'PENDING', 'CAPTURED', 'FAILED', 'REFUNDED');
CREATE TYPE scheduling_status_enum AS ENUM (
    'PAID_AWAITING_CONTACT', 
    'CONTACTED', 
    'SCHEDULED', 
    'COMPLETED', 
    'CANCELLED', 
    'NO_SHOW'
);
CREATE TYPE contact_status_enum AS ENUM ('PENDING', 'CONTACTED', 'OVERDUE');
CREATE TYPE outbox_status_enum AS ENUM ('PENDING', 'SENT', 'FAILED', 'DEAD');
CREATE TYPE refund_status_enum AS ENUM ('PENDING', 'PROCESSED', 'FAILED');

-- 1. Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role user_role NOT NULL DEFAULT 'CANDIDATE',
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token_hash VARCHAR(255),
    email_verification_sent_at TIMESTAMPTZ,
    password_reset_token_hash VARCHAR(255),
    password_reset_sent_at TIMESTAMPTZ,
    totp_secret VARCHAR(255),
    is_totp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Rotating Refresh Tokens
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    family_id UUID NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    user_agent TEXT,
    ip_address VARCHAR(45),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Candidate Profiles
CREATE TABLE candidate_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    years_experience NUMERIC(3, 1) NOT NULL CHECK (years_experience >= 0),
    current_company VARCHAR(150),
    target_role VARCHAR(150) NOT NULL,
    technical_skills TEXT[] NOT NULL DEFAULT '{}',
    linkedin_url VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Stored Files (Private storage metadata)
CREATE TABLE stored_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    file_purpose VARCHAR(50) NOT NULL CHECK (file_purpose IN ('RESUME', 'JOB_DESCRIPTION')),
    original_filename VARCHAR(255) NOT NULL,
    sanitized_filename VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    file_size_bytes INTEGER NOT NULL CHECK (file_size_bytes > 0 AND file_size_bytes <= 5242880), -- 5MB limit
    mime_type VARCHAR(100) NOT NULL CHECK (mime_type IN ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
    sha256_checksum VARCHAR(64) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    purge_scheduled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Interview Types (Fixed 6 categories)
CREATE TABLE interview_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(100) NOT NULL UNIQUE,
    short_description TEXT NOT NULL,
    detailed_topics TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    display_order INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Interview Prices (Snapshot price table)
CREATE TABLE interview_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_type_id UUID NOT NULL REFERENCES interview_types(id) ON DELETE RESTRICT,
    amount_paise INTEGER NOT NULL CHECK (amount_paise > 0), -- Exactly 19900 paise
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    duration_min_minutes INTEGER NOT NULL DEFAULT 45,
    duration_max_minutes INTEGER NOT NULL DEFAULT 60,
    duration_display VARCHAR(50) NOT NULL DEFAULT '45–60 minutes',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    retired_at TIMESTAMPTZ
);

-- 7. Interview Requests (The central booking entity)
CREATE TABLE interview_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_reference VARCHAR(20) NOT NULL UNIQUE, -- e.g. MOCK-202610-A89F
    candidate_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    interview_type_id UUID NOT NULL REFERENCES interview_types(id) ON DELETE RESTRICT,
    price_snapshot_id UUID NOT NULL REFERENCES interview_prices(id) ON DELETE RESTRICT,
    amount_paise INTEGER NOT NULL, -- 19900 paise captured at creation
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    
    -- Status partitions
    payment_status payment_status_enum NOT NULL DEFAULT 'CREATED',
    scheduling_status scheduling_status_enum NOT NULL DEFAULT 'PAID_AWAITING_CONTACT',
    
    -- SLA Contact Tracking (Asia/Kolkata)
    paid_at TIMESTAMPTZ,
    contact_deadline_at TIMESTAMPTZ, -- Computed based on cutoff policy
    contact_status contact_status_enum NOT NULL DEFAULT 'PENDING',
    first_contacted_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Booking Inputs (Resume, JD, Candidate context)
CREATE TABLE booking_inputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_request_id UUID NOT NULL UNIQUE REFERENCES interview_requests(id) ON DELETE CASCADE,
    resume_file_id UUID NOT NULL REFERENCES stored_files(id) ON DELETE RESTRICT,
    jd_file_id UUID REFERENCES stored_files(id) ON DELETE RESTRICT,
    jd_text TEXT,
    additional_notes TEXT,
    years_experience NUMERIC(3, 1) NOT NULL,
    current_company VARCHAR(150),
    target_role VARCHAR(150) NOT NULL,
    technical_skills TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Interview Schedules (Enforces overlap prevention via GiST constraint)
CREATE TABLE interview_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_request_id UUID NOT NULL UNIQUE REFERENCES interview_requests(id) ON DELETE CASCADE,
    interviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    scheduled_duration_minutes INTEGER NOT NULL CHECK (scheduled_duration_minutes BETWEEN 45 AND 60),
    time_slot TSTZRANGE NOT NULL,
    meeting_platform VARCHAR(50) NOT NULL DEFAULT 'Google Meet',
    meeting_url TEXT NOT NULL,
    joining_instructions TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'RESCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Enforce valid time range
    CONSTRAINT valid_schedule_duration CHECK (scheduled_end > scheduled_start),
    -- EXCLUSION CONSTRAINT: Prevent overlapping active interviews for the interviewer!
    CONSTRAINT no_overlapping_active_schedules EXCLUDE USING gist (
        interviewer_id WITH =,
        time_slot WITH &&
    ) WHERE (status IN ('SCHEDULED', 'RESCHEDULED'))
);

-- 10. Schedule Events (Audit log for scheduling adjustments)
CREATE TABLE schedule_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID NOT NULL REFERENCES interview_schedules(id) ON DELETE CASCADE,
    actor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    event_type VARCHAR(50) NOT NULL, -- CREATED, RESCHEDULED, CANCELLED, COMPLETED, NO_SHOW
    previous_start TIMESTAMPTZ,
    previous_end TIMESTAMPTZ,
    new_start TIMESTAMPTZ,
    new_end TIMESTAMPTZ,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. Scheduling Contact Logs (Interviewer SLA Tracking)
CREATE TABLE scheduling_contact_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_request_id UUID NOT NULL REFERENCES interview_requests(id) ON DELETE CASCADE,
    interviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    channel VARCHAR(50) NOT NULL DEFAULT 'EMAIL',
    notes TEXT NOT NULL,
    contacted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. Payments (Razorpay Transaction Ledger)
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_request_id UUID NOT NULL REFERENCES interview_requests(id) ON DELETE RESTRICT,
    razorpay_order_id VARCHAR(100) NOT NULL UNIQUE,
    razorpay_payment_id VARCHAR(100) UNIQUE,
    razorpay_signature VARCHAR(255),
    amount_paise INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status payment_status_enum NOT NULL DEFAULT 'CREATED',
    method VARCHAR(50),
    bank VARCHAR(50),
    wallet VARCHAR(50),
    vpa VARCHAR(100),
    error_code VARCHAR(100),
    error_description TEXT,
    captured_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 13. Webhook Events (Idempotent Webhook Log)
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(100) NOT NULL UNIQUE, -- Razorpay X-Razorpay-Event-Id
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    processing_error TEXT,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- 14. Refunds (Razorpay Refunds Log)
CREATE TABLE refunds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE RESTRICT,
    interview_request_id UUID NOT NULL REFERENCES interview_requests(id) ON DELETE RESTRICT,
    razorpay_refund_id VARCHAR(100) UNIQUE,
    amount_paise INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    reason TEXT NOT NULL,
    status refund_status_enum NOT NULL DEFAULT 'PENDING',
    initiated_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- 15. Transactional Outbox (Reliable Email Delivery Engine)
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_request_id UUID REFERENCES interview_requests(id) ON DELETE SET NULL,
    idempotency_key VARCHAR(150) NOT NULL UNIQUE,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(150) NOT NULL,
    template_name VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    template_data JSONB NOT NULL,
    status outbox_status_enum NOT NULL DEFAULT 'PENDING',
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 5,
    last_error TEXT,
    resend_email_id VARCHAR(100),
    scheduled_for TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 16. Interview Feedback (Admin's private evaluation notes)
CREATE TABLE interview_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_schedule_id UUID NOT NULL UNIQUE REFERENCES interview_schedules(id) ON DELETE CASCADE,
    interviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    strengths TEXT NOT NULL,
    areas_for_improvement TEXT NOT NULL,
    technical_rating INTEGER NOT NULL CHECK (technical_rating BETWEEN 1 AND 5),
    communication_rating INTEGER NOT NULL CHECK (communication_rating BETWEEN 1 AND 5),
    recommendation_summary TEXT NOT NULL,
    is_shared_with_candidate BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 17. System Settings & Policies
CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 18. Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(100) NOT NULL,
    target_id UUID,
    ip_address VARCHAR(45),
    user_agent TEXT,
    changes JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for maximum query performance
CREATE INDEX idx_interview_requests_candidate ON interview_requests(candidate_id);
CREATE INDEX idx_interview_requests_payment_status ON interview_requests(payment_status);
CREATE INDEX idx_interview_requests_scheduling_status ON interview_requests(scheduling_status);
CREATE INDEX idx_interview_requests_contact_deadline ON interview_requests(contact_deadline_at) WHERE contact_status = 'PENDING';
CREATE INDEX idx_notifications_status ON notifications(status, scheduled_for) WHERE status IN ('PENDING', 'FAILED');
CREATE INDEX idx_refresh_tokens_family ON refresh_tokens(family_id);
CREATE INDEX idx_payments_razorpay_order ON payments(razorpay_order_id);
```

---

## 5. State Machine Specifications

### 5.1 Payment Lifecycle State Machine
```mermaid
stateDiagram-v2
    [*] --> CREATED: Checkout initiated / Order created in Razorpay
    CREATED --> PENDING: Payment modal opened / Netbanking pending
    PENDING --> CAPTURED: Signature verified OR Webhook confirmed
    CREATED --> CAPTURED: Direct captured signature verified
    CREATED --> FAILED: Payment declined / user cancelled / invalid signature
    PENDING --> FAILED: Payment window timed out / gateway rejected
    CAPTURED --> REFUNDED: Admin initiates full refund
    CAPTURED --> [*]
    FAILED --> [*]
    REFUNDED --> [*]
```

### 5.2 Interview Request & Scheduling Lifecycle State Machine
```mermaid
stateDiagram-v2
    [*] --> DRAFT: Candidate fills form / uploads resume
    DRAFT --> PAID_AWAITING_CONTACT: Payment verified (19,900 paise confirmed)
    
    state PAID_AWAITING_CONTACT {
        [*] --> PendingOutreach: Compute contact_deadline_at (IST)
        PendingOutreach --> ApproachingDeadline: Within 2 hours of SLA
        ApproachingDeadline --> OverdueAlert: SLA breached without contact
    }

    PAID_AWAITING_CONTACT --> CONTACTED: Interviewer emails candidate & logs contact
    CONTACTED --> SCHEDULED: Mutual date/time assigned with Meet/Zoom URL
    
    SCHEDULED --> RESCHEDULED: Date/time updated (GiST exclusion verified)
    RESCHEDULED --> SCHEDULED: Invitation dispatched
    
    SCHEDULED --> COMPLETED: 45–60m session conducted
    SCHEDULED --> CANCELLED: Cancelled before interview (Refund evaluated)
    SCHEDULED --> NO_SHOW: Candidate failed to attend after 15m grace period
    
    CANCELLED --> [*]
    COMPLETED --> [*]
    NO_SHOW --> [*]
```

### 5.3 Transactional Outbox State Machine
```mermaid
stateDiagram-v2
    [*] --> PENDING: Notification record committed in same DB transaction
    PENDING --> SENDING: Worker claims record (SELECT ... FOR UPDATE SKIP LOCKED)
    SENDING --> SENT: Resend returns 200 OK (store resend_email_id)
    SENDING --> FAILED: Resend returns 429 / 5xx / Network Error
    FAILED --> RETRYING: Exponential backoff (1m, 5m, 15m, 1h)
    RETRYING --> SENDING: Retry count < max_retries
    FAILED --> DEAD: Retry count >= max_retries (Alert Admin)
    SENT --> [*]
    DEAD --> [*]
```

---

## 6. Payment & Verification Flow Sequence (Razorpay)

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Candidate
    participant NextClient as Next.js Frontend
    participant Backend as FastAPI Backend
    participant DB as PostgreSQL DB
    participant Razorpay as Razorpay Gateway
    participant Worker as Background Worker (Outbox)
    participant Resend as Resend Email Service
    actor Admin as Admin (Interviewer)

    Candidate->>NextClient: Select Category & Fill Profile + Resume
    Candidate->>NextClient: Click "Proceed to Pay ₹199"
    NextClient->>Backend: POST /api/v1/payments/create-order (booking_id)
    Note over Backend,DB: Backend fetches price (19,900 paise) from DB.<br/>Frontend price is never trusted!
    Backend->>Razorpay: Create Order (amount: 19900, currency: INR)
    Razorpay-->>Backend: Return order_id (e.g. order_OPQr123)
    Backend->>DB: Save Payment (status: CREATED, order_id)
    Backend-->>NextClient: Return order_id, key_id, amount: 19900
    
    NextClient->>Razorpay: Open Razorpay Standard Checkout Modal
    Candidate->>Razorpay: Complete UPI / Card / Netbanking Payment
    Razorpay-->>NextClient: Return payment_id, order_id, signature

    par Client Verification & Webhook Redundancy
        NextClient->>Backend: POST /api/v1/payments/verify (payload + signature)
        Backend->>Backend: Compute HMAC SHA-256 signature
        alt Signature Matches
            Backend->>DB: BEGIN TRANSACTION
            Backend->>DB: UPDATE payments SET status='CAPTURED', payment_id=...
            Backend->>DB: UPDATE interview_requests SET payment_status='CAPTURED',<br/>scheduling_status='PAID_AWAITING_CONTACT',<br/>paid_at=NOW(), contact_deadline_at=...
            Backend->>DB: INSERT INTO notifications (outbox for Candidate & Admin)
            Backend->>DB: COMMIT
            Backend-->>NextClient: 200 OK (Booking Confirmed)
            NextClient->>Candidate: Display Success Screen (Awaiting Contact)
        else Signature Invalid
            Backend-->>NextClient: 400 Bad Signature
        end
    and Webhook Event
        Razorpay->>Backend: POST /api/v1/payments/webhook (payment.captured)
        Backend->>Backend: Verify X-Razorpay-Signature with raw body
        Backend->>DB: Check if event_id already processed (Idempotency)
        alt Not already processed
            Backend->>DB: Ensure payment & booking marked CAPTURED
            Backend->>DB: Enqueue outbox if not already present
        end
        Backend-->>Razorpay: 200 OK
    end

    loop Outbox Worker Processing
        Worker->>DB: Claim PENDING notifications (SKIP LOCKED)
        Worker->>Resend: Send Email 1 (Payment Successful to Candidate)
        Worker->>Resend: Send Email 3 (New Booking Notification to Admin)
        Worker->>DB: Mark notifications SENT
    end

    Admin->>Candidate: Personal scheduling outreach via email before deadline
```

---

## 7. Email Architecture & Transactional Outbox Engine

Transactional emails are business-critical. We will employ the **Transactional Outbox Pattern**:
1. When a payment is marked `CAPTURED`, notification rows are written to the `notifications` table within the **exact same database transaction**.
2. If the web server crashes or Resend has a momentary hiccup, the payment remains committed, and the notification is safely waiting in the DB.
3. The background worker polls the `notifications` table every 10 seconds (or is woken up via Redis Pub/Sub), acquires pending records using `SELECT ... FOR UPDATE SKIP LOCKED`, and calls the Resend API with idempotency headers.

### 7.1 Specifications for Core Transactional Emails

#### Email 1: Payment Successful (Candidate Confirmation)
* **Trigger:** Verified payment (`CAPTURED`).
* **Recipient:** Candidate.
* **Subject:** `Payment Successful — Your Mock Interview Is Booked`
* **Body Structure:**
  ```text
  Hi {Candidate Name},

  Your payment of ₹199 for the {Interview Category} has been received successfully.

  Your mock interview duration will be 45–60 minutes.

  Our interviewer will contact you by email today to arrange your interview date and time.

  Once the schedule is confirmed, you will receive a Google Meet or Zoom invitation containing your interview date, time, and joining link.

  Booking Reference: {Booking Reference}
  Payment Reference: {Razorpay Payment ID}

  Thank you for booking your mock interview!
  Support: support@domain.com
  ```

#### Email 2: Payment Failed (Confirmed Failure Only)
* **Trigger:** Gateway reports terminal payment failure (`payment.failed` webhook). Never sent for abandoned carts.
* **Recipient:** Candidate.
* **Subject:** `Mock Interview Payment Unsuccessful`
* **Body Structure:**
  ```text
  Hi {Candidate Name},

  Unfortunately, your payment for the {Interview Category} was unsuccessful.

  Your mock interview booking has not been confirmed.

  Please return to our website and retry your payment securely.

  If money was deducted from your account, contact our support team with your payment reference ({Payment Reference}) so we can verify the transaction.
  ```

#### Email 3: Admin New Booking Notification
* **Trigger:** Verified payment.
* **Recipient:** Administrator (`ADMIN_EMAIL`).
* **Subject:** `[ACTION REQUIRED] New Paid Booking: {Category} - {Candidate Name}`
* **Content:** Candidate name, email, phone, experience, target role, technical skills, booking reference, payment ID, safe authenticated download link for resume/JD, and the calculated **Same-Day Scheduling Contact Deadline** in IST.

#### Email 4: Interview Scheduled (With ICS Calendar Attachment)
* **Trigger:** Admin schedules date, time, and provides Google Meet/Zoom link.
* **Recipient:** Candidate.
* **Subject:** `Confirmed: Your {Interview Category} Mock Interview Schedule`
* **Content:** Confirmed start time (IST), duration (45–60 min), meeting URL, prep tips, and attached standard `.ics` calendar invitation file.

---

## 8. Authentication & Security Architecture

### 8.1 Authentication Design
* **Password Hashing:** `Argon2id` (RFC 9106 recommended parameters: `m=65536` [64 MiB memory], `t=3` iterations, `p=4` parallelism).
* **Access Tokens:** Short-lived JWT (15-minute expiration) holding `sub` (User ID), `role` (`CANDIDATE` or `ADMIN`), and `jti`. Stored in an `HttpOnly`, `SameSite=Lax` (or `Strict`), `Secure` cookie.
* **Refresh Tokens:** Long-lived (7 days) cryptographically random 256-bit strings. Stored in DB as a **SHA-256 hash**.
  * **Token Rotation with Family Tracking:** Every refresh request issues a new token pair and revokes the old one. If an invalidated refresh token is ever presented (indicative of token theft), the entire token family is immediately revoked, forcing re-authentication.
* **CSRF Mitigation:** Anti-CSRF double-submit token cookie + custom header `X-CSRF-Token` verified on all state-changing endpoints (`POST`, `PUT`, `PATCH`, `DELETE`).
* **Rate Limiting:**
  * Login / Registration endpoints: 5 requests per minute per IP using Redis leaky bucket.
  * Payment initiation: 10 requests per minute per user.
* **Role-Based Access Control:** Built-in FastAPI dependency injection verifying `current_user.role == Role.ADMIN` for all management APIs.

---

## 9. File Upload Security Architecture

To prevent Remote Code Execution (RCE), Local File Inclusion (LFI), or payload delivery via resumes and job descriptions:
1. **Size Enforcement:** Maximum 5 MB per individual file; maximum 10 MB aggregate per booking.
2. **Strict Whitelist:** Only PDF (`application/pdf`) and DOCX (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
3. **Magic-Byte & Header Verification:** Inspect raw file signature in memory via pure-python header inspection:
   - PDF: Must begin with `%PDF-` bytes.
   - DOCX: Must have PK Zip header `\x50\x4B\x03\x04` and validate internal XML structure.
4. **Storage Isolation:**
   - Files are renamed to randomly generated UUIDs: `uploads/{user_id}/{uuid4()}.bin`.
   - Never stored in a publicly accessible directory.
   - Served exclusively through an authenticated streaming endpoint: `GET /api/v1/candidate/files/{file_id}` or `GET /api/v1/admin/files/{file_id}` with proper `Content-Disposition: attachment` headers.
5. **Retention Cleanup Policy:** Stored files are automatically marked for deletion and purged by a background worker 30 days after the booking reaches a terminal state (`COMPLETED`, `CANCELLED`).

---

## 10. API Specification (/api/v1)

### Public Endpoints
* `GET /api/v1/categories` — Returns the exactly 6 categories with topics, 45–60 min duration, and ₹199 price.
* `GET /api/v1/pricing` — Returns the canonical package details (₹199 / 19,900 paise).
* `GET /api/v1/policies` — Cancellation, refund, privacy, and terms policies.
* `GET /api/v1/health` & `GET /api/v1/ready` — Operational health and DB/Redis readiness probes.

### Authentication Endpoints
* `POST /api/v1/auth/register` — Candidate sign up (sends email verification token).
* `POST /api/v1/auth/verify-email` — Confirms candidate email address.
* `POST /api/v1/auth/login` — Authenticates user, issues HttpOnly cookies.
* `POST /api/v1/auth/refresh` — Rotates refresh token, issues new access token.
* `POST /api/v1/auth/logout` — Revokes current refresh token, clears cookies.
* `POST /api/v1/auth/forgot-password` — Generates reset token.
* `POST /api/v1/auth/reset-password` — Validates token and updates Argon2id hash.
* `GET /api/v1/auth/me` — Returns current logged-in user profile.

### Candidate Endpoints
* `POST /api/v1/candidate/booking-draft` — Saves interview category, details, and context.
* `POST /api/v1/candidate/upload-resume` — Validates magic bytes and stores candidate resume.
* `POST /api/v1/candidate/upload-jd` — Optional upload of JD document.
* `GET /api/v1/candidate/my-interviews` — Lists all bookings with status, scheduled times, and meeting links.
* `GET /api/v1/candidate/my-interviews/{id}` — Detailed view of a single booking.
* `POST /api/v1/candidate/my-interviews/{id}/cancel` — Requests cancellation/refund.

### Payment Endpoints
* `POST /api/v1/payments/create-order` — Creates Razorpay order for ₹199 (19,900 paise).
* `POST /api/v1/payments/verify` — Verifies checkout signature and marks booking paid.
* `POST /api/v1/payments/webhook` — Handles raw Razorpay webhook events securely.

### Admin Endpoints (Restricted to Role: ADMIN)
* `GET /api/v1/admin/metrics` — High-level dashboard counters (Revenue, Awaiting Contact, Overdue, Scheduled, Completed).
* `GET /api/v1/admin/bookings` — Filterable, searchable, paginated list of all bookings.
* `GET /api/v1/admin/bookings/{id}` — Full booking view including candidate context and files.
* `POST /api/v1/admin/bookings/{id}/mark-contacted` — Records interviewer outreach and clears SLA timer.
* `POST /api/v1/admin/bookings/{id}/schedule` — Assigns date, time, duration (45–60 min), and meeting URL (with GiST overlap validation).
* `POST /api/v1/admin/bookings/{id}/reschedule` — Adjusts scheduled date/time and notifies candidate.
* `POST /api/v1/admin/bookings/{id}/complete` — Marks interview session as completed.
* `POST /api/v1/admin/bookings/{id}/no-show` — Marks candidate no-show.
* `POST /api/v1/admin/bookings/{id}/refund` — Dispatches refund request via Razorpay API.
* `GET /api/v1/admin/files/{file_id}/download` — Authenticated stream of candidate resume/JD.
* `GET /api/v1/admin/audit-logs` — Audit log trail.

---

## 11. Premium UI/UX Design System Specification

### 11.1 Design Philosophy & Aesthetics
* **Vibe:** High-trust, executive, premium technical career accelerator (comparable to Linear, Stripe, or Vercel).
* **Avoid:** Cheap neon gradients, gamified badges, cartoon illustrations, cluttered tables, or AI-generated styling tropes.

### 11.2 Design Tokens
| Token | Value | Purpose |
| :--- | :--- | :--- |
| **Primary (Brand)** | `#0F172A` (Slate 900) / `#0284C7` (Sky 600) | Deep authority, trustworthy technical branding |
| **Accent / Highlight** | `#D97706` (Warm Amber 600) | Subtle, prestigious focus points without gaudiness |
| **Background (Light)** | `#F8FAFC` (Slate 50) | Clean, high-legibility canvas |
| **Surface Cards** | `#FFFFFF` with border `#E2E8F0` | Distinct, elevated container cards |
| **Text Primary** | `#0F172A` (Slate 900) | Maximum WCAG contrast ratio (>10:1) |
| **Text Muted** | `#64748B` (Slate 500) | Supporting metadata |
| **Success / Captured** | `#059669` (Emerald 600) | Confirmed payments & completed stages |
| **Warning / Alert** | `#DC2626` (Red 600) | SLA deadline warnings & errors |
| **Typography** | `Inter` / `Plus Jakarta Sans` | Modern geometric sans-serif |
| **Border Radius** | `rounded-lg` (8px), `rounded-xl` (12px) | Modern soft edges |

### 11.3 Responsive Viewport Strategy
* **Mobile (320px – 430px):** Single-column stacked layouts, fixed bottom action bar for primary CTA (₹199 Book Now), full-width drawer navigation, touch targets $\ge 48\text{px}$, zero horizontal overflow.
* **Tablet (768px – 1023px):** 2-column category grid, collapsed admin menu with quick access bar.
* **Laptop & Desktop (1024px – 1920px):** 3-column category grid, max content width `1280px` (`max-w-7xl`), side-by-side sticky checkout review, rich data tables with inline badges and filters.

---

## 12. Security Threat Model (OWASP ASVS Alignment)

| Threat Category | Potential Attack Vector | Mitigation in Architecture |
| :--- | :--- | :--- |
| **Price Tampering** | Malicious client alters price from ₹199 to ₹1 | Backend ignores frontend amounts entirely; fetches ₹199 from DB; Razorpay order created server-side. |
| **Signature Spoofing** | Attacker calls `/payments/verify` with fake IDs | Backend calculates HMAC-SHA256 using server-held secret; rejects mismatched hashes. |
| **Replay Attacks** | Resending valid webhook payload | Webhook events logged in `webhook_events` with unique event ID; processed idempotently. |
| **Schedule Overlap** | Race condition booking two interviews at same time | Database-level GiST exclusion constraint (`no_overlapping_active_schedules`) prevents double bookings. |
| **Malicious File Upload** | Attacker uploads web shell disguised as `.pdf` | Magic byte validation, random UUID filenames, private storage, authenticated streaming download. |
| **IDOR** | Candidate views another candidate's resume/booking | Row-level ownership validation: `WHERE id = :id AND candidate_id = :user_id`. Admin role required for others. |
| **Brute Force Login** | Password guessing on `/auth/login` | Leaky bucket rate limiting (5 req/min/IP) + Argon2id hash computation cost. |
| **Session Hijacking** | XSS stealing authentication tokens | Tokens stored in `HttpOnly`, `SameSite=Lax`, `Secure` cookies. Zero tokens in `localStorage`. |

---

## 13. Deployment Architecture & Estimated Monthly Costs

### 13.1 Production Deployment Setup
* **Web & API Host:** Dockerized containers deployed on a lightweight VPS (Hetzner / DigitalOcean $6–$12/mo) or Render/Railway Web Service.
* **Database:** Supabase Managed PostgreSQL (Free tier initially, scaling to $25/mo Pro tier).
* **Cache & Queues:** Redis (Upstash Free tier / Redis Cloud Free 30MB, or embedded Redis Docker container).
* **Storage:** Local encrypted volume in dev, private Supabase Storage bucket in production.
* **Email:** Resend (Free tier includes 3,000 emails/month; scales to $20/mo for 50,000 emails).
* **Payment Gateway:** Razorpay Standard Gateway (2% + GST per transaction).

### 13.2 Estimated Initial Monthly Run Rate
* Hosting: **$6.00 – $12.00** (~₹500 – ₹1,000 / month)
* Database (Supabase Free): **$0.00**
* Redis (Upstash / Cloud Free): **$0.00**
* Resend (Free 3,000 emails): **$0.00**
* Domain & Cloudflare SSL: **~$1.00 / month**
* **Total Base Infrastructure Cost:** **$\approx 7 – 13 / \text{month}$** (Extremely cost-effective for V1 launch).

---

## 14. Environment Configuration Guide (.env.example)

```bash
# ==============================================================================
# ENVIRONMENT CONFIGURATION
# ==============================================================================
APP_ENV=development
BUSINESS_TIMEZONE=Asia/Kolkata
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# ==============================================================================
# DATABASE (PostgreSQL / Supabase)
# ==============================================================================
# Direct connection for Alembic migrations and backend asyncpg driver
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.supabase.co:5432/postgres
DIRECT_DATABASE_URL=postgresql://postgres:your_password@db.supabase.co:5432/postgres

# ==============================================================================
# AUTHENTICATION & SECRETS (Generate with: openssl rand -hex 32)
# ==============================================================================
JWT_SECRET=replace_with_64_char_cryptographically_secure_random_hex
CSRF_SECRET=replace_with_64_char_cryptographically_secure_random_hex
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==============================================================================
# RAZORPAY PAYMENT GATEWAY
# ==============================================================================
# Obtain from https://dashboard.razorpay.com/app/keys
RAZORPAY_KEY_ID=rzp_test_YourKeyIdHere
RAZORPAY_KEY_SECRET=YourRazorpayKeySecretHere
RAZORPAY_WEBHOOK_SECRET=YourRazorpayWebhookSecretHere

# ==============================================================================
# RESEND TRANSACTIONAL EMAIL
# ==============================================================================
# Obtain from https://resend.com/api-keys
RESEND_API_KEY=re_YourResendApiKeyHere
EMAIL_FROM=Interviews <interviews@yourverifieddomain.com>
ADMIN_EMAIL=interviewer-admin@yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com

# ==============================================================================
# REDIS / QUEUE BROKER
# ==============================================================================
REDIS_URL=redis://localhost:6379/0

# ==============================================================================
# FILE STORAGE
# ==============================================================================
UPLOAD_DIR=./storage/uploads
MAX_FILE_SIZE_BYTES=5242880 # 5 MB

# ==============================================================================
# MONITORING
# ==============================================================================
SENTRY_DSN=
```

---

## 15. Phased Implementation Roadmap (Stages 2–10)

Following approval of this Stage 1 specification, execution will strictly follow the agreed sequence:

* **Stage 2: Foundation & Authentication:**
  Next.js + FastAPI scaffolding, Docker Compose, Supabase PostgreSQL schema migrations, custom Argon2id auth, rotating refresh token cookies, CSRF protection, and baseline CI.
* **Stage 3: Categories & Pricing Engine:**
  Seed database with exactly 6 categories and the ₹199 (19,900 paise) package. Enforce catalog constraints and admin pricing updates.
* **Stage 4: Candidate Experience & Upload Pipeline:**
  Build high-converting landing page, category cards, multi-step booking form, secure PDF/DOCX magic-byte upload pipeline, and candidate dashboard.
* **Stage 5: Razorpay Payment Integration:**
  Implement order creation, checkout modal, HMAC-SHA256 signature verification, idempotent webhook listener, payment failure flows, and refund engine.
* **Stage 6: Transactional Email & Outbox Worker:**
  Configure Resend API, transactional outbox worker in PostgreSQL/Redis, automatic payment confirmation, admin booking alert, failure notifications, and retry logic.
* **Stage 7: Interviewer Scheduling & Overlap Prevention:**
  Implement same-day contact SLA monitor (Asia/Kolkata), admin contact logging, interview assignment with GiST overlap protection, and Google Meet/Zoom invite dispatch with ICS attachments.
* **Stage 8: Admin Dashboard & Operations:**
  Build responsive admin control panel with metrics, booking filters, secure file streaming, candidate feedback notes, and refund processing.
* **Stage 9: UI Polish, Responsiveness & Legal Compliance:**
  Audit viewports (320px to 1920px), WCAG 2.2 AA accessibility, terms of service, privacy policy, refund policy, and contact forms.
* **Stage 10: Security Hardening, Verification & Deployment:**
  End-to-end integration tests, OWASP vulnerability audit, load testing, Git repository remote push, and Docker production deployment runbook.

---

### Acceptance Gate for Stage 1
*Review requested from user.* Once Stage 1 is reviewed and approved, implementation code for Stage 2 will commence.
