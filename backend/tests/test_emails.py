import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.templates.email_templates import (
    render_payment_successful,
    render_payment_failed,
    render_admin_new_booking,
    render_interview_scheduled,
    render_refund_completed,
    render_template,
)
from app.core.calendar import generate_ics_calendar
from app.workers.outbox_worker import process_pending_outbox, process_single_notification
from app.integrations.resend_client import (
    resend_client,
    ResendTransientError,
    ResendFatalError,
)


def test_calendar_ics_generation():
    start = datetime(2026, 10, 20, 10, 30, tzinfo=timezone.utc)
    end = datetime(2026, 10, 20, 11, 30, tzinfo=timezone.utc)
    ics = generate_ics_calendar(
        uid="test-session-123",
        summary="DSA Mock Interview",
        description="45-60 min technical mock session.\nBring an IDE.",
        location_url="https://meet.google.com/abc-defg-hij",
        start_time_utc=start,
        end_time_utc=end,
        organizer_email="interviewer@mockinterviews.dev",
        organizer_name="Lead Interviewer",
        attendee_email="candidate@example.com",
        attendee_name="John Doe",
    )

    assert "BEGIN:VCALENDAR" in ics
    assert "METHOD:REQUEST" in ics
    assert "UID:test-session-123" in ics
    assert "LOCATION:https://meet.google.com/abc-defg-hij" in ics
    assert "SUMMARY:DSA Mock Interview" in ics
    assert "mailto:candidate@example.com" in ics
    assert "END:VCALENDAR" in ics


def test_email_1_payment_successful_template():
    data = {
        "candidate_name": "Rohan Sharma",
        "category_name": "System Design Mock Interview",
        "booking_reference": "MOCK-2610-A1B2",
        "payment_reference": "pay_test_12345",
    }
    subject, html, text = render_payment_successful(data)

    assert subject == "Payment Successful — Your Mock Interview Is Booked"
    # Mandatory text checks from business specification
    assert "Hi Rohan Sharma," in text
    assert "Your payment of ₹199 for the System Design Mock Interview has been received successfully." in text
    assert "Your mock interview duration will be 45–60 minutes." in text
    assert "Our interviewer will contact you by email today to arrange your interview date and time." in text
    assert "Booking Reference: MOCK-2610-A1B2" in text
    assert "Payment Reference: pay_test_12345" in text
    assert "support@mockinterviews.dev" in text


def test_email_2_payment_failed_template():
    data = {
        "candidate_name": "Rohan Sharma",
        "category_name": "DSA Mock Interview",
        "payment_reference": "pay_failed_67890",
    }
    subject, html, text = render_payment_failed(data)

    assert subject == "Mock Interview Payment Unsuccessful"
    assert "Hi Rohan Sharma," in text
    assert "Unfortunately, your payment for the DSA Mock Interview was unsuccessful." in text
    assert "Your mock interview booking has not been confirmed." in text
    assert "Please return to our website and retry your payment securely." in text
    assert "Payment Reference: pay_failed_67890" in text


def test_email_3_admin_new_booking_template():
    data = {
        "candidate_name": "Ananya Patel",
        "candidate_email": "ananya@example.com",
        "candidate_phone": "+919876543210",
        "years_experience": 4,
        "current_company": "Acme Tech",
        "target_role": "Senior Backend Engineer",
        "technical_skills": "Python, Go, PostgreSQL, Redis",
        "category_name": "Backend Mock Interview",
        "booking_reference": "MOCK-2610-C3D4",
        "payment_reference": "pay_test_9999",
        "resume_url": "https://api.mockinterviews.dev/storage/uploads/resume.pdf",
        "job_description": "We are seeking a senior backend engineer to design scalable systems.",
        "contact_deadline_ist": "15 Oct 2026, 11:59 PM",
        "additional_notes": "Focused on database sharding and caching strategies.",
    }
    subject, html, text = render_admin_new_booking(data)

    assert "MOCK-2610-C3D4" in subject
    assert "Backend Mock Interview" in subject
    assert "Ananya Patel" in text
    assert "+919876543210" in text
    assert "4 years" in text
    assert "Senior Backend Engineer" in text
    assert "15 Oct 2026, 11:59 PM (IST)" in text
    assert "45–60 minutes" in text
    assert "₹199" in text


def test_email_4_interview_scheduled_template():
    data = {
        "candidate_name": "Vikram Singh",
        "category_name": "Full Stack Mock Interview",
        "booking_reference": "MOCK-2610-E5F6",
        "interview_date": "Saturday, 18 Oct 2026",
        "start_time": "04:00 PM IST",
        "meeting_url": "https://meet.google.com/xyz-uvwx-rst",
    }
    subject, html, text = render_interview_scheduled(data)

    assert "Interview Scheduled — Full Stack Mock Interview" in subject
    assert "Saturday, 18 Oct 2026" in subject
    assert "Vikram Singh" in text
    assert "04:00 PM IST (Asia/Kolkata)" in text
    assert "https://meet.google.com/xyz-uvwx-rst" in text
    assert "45–60 minutes" in text
    assert "MOCK-2610-E5F6" in text


@pytest.mark.asyncio
async def test_outbox_worker_processes_pending_notification(db_session: AsyncSession):
    # Enqueue a pending notification
    notif = Notification(
        idempotency_key="test-notif-success-key",
        recipient_email="candidate_success@example.com",
        recipient_name="Success Candidate",
        template_name="payment_successful",
        subject="Payment Successful — Your Mock Interview Is Booked",
        template_data={
            "candidate_name": "Success Candidate",
            "category_name": "System Design Mock Interview",
            "booking_reference": "MOCK-2610-SUCC",
            "payment_reference": "pay_succ_111",
        },
        status="PENDING",
        scheduled_for=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db_session.add(notif)
    await db_session.commit()

    processed_count = await process_pending_outbox(db_session, limit=10)
    assert processed_count >= 1

    # Reload notification from database
    refreshed = (await db_session.execute(
        select(Notification).where(Notification.idempotency_key == "test-notif-success-key")
    )).scalar_one()

    assert refreshed.status == "SENT"
    assert refreshed.sent_at is not None
    assert refreshed.resend_email_id is not None
    assert refreshed.resend_email_id.startswith("mock_resend_")
    assert refreshed.last_error is None


@pytest.mark.asyncio
async def test_outbox_worker_handles_transient_failure_and_backoff(db_session: AsyncSession):
    notif = Notification(
        idempotency_key="test-notif-transient-retry-key",
        recipient_email="candidate_retry@example.com",
        recipient_name="Retry Candidate",
        template_name="payment_successful",
        subject="Payment Successful",
        template_data={"candidate_name": "Retry Candidate"},
        status="PENDING",
        retry_count=0,
        max_retries=3,
        scheduled_for=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db_session.add(notif)
    await db_session.commit()

    # Simulate ResendTransientError
    with patch.object(resend_client, "send_email", side_effect=ResendTransientError("Rate limit 429")):
        await process_single_notification(db_session, notif)

    refreshed = (await db_session.execute(
        select(Notification).where(Notification.idempotency_key == "test-notif-transient-retry-key")
    )).scalar_one()

    assert refreshed.status == "PENDING"
    assert refreshed.retry_count == 1
    assert "Rate limit 429" in refreshed.last_error
    assert refreshed.scheduled_for > datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_outbox_worker_marks_dead_after_max_retries(db_session: AsyncSession):
    notif = Notification(
        idempotency_key="test-notif-dead-letter-key",
        recipient_email="candidate_dead@example.com",
        recipient_name="Dead Candidate",
        template_name="payment_successful",
        subject="Payment Successful",
        template_data={"candidate_name": "Dead Candidate"},
        status="PENDING",
        retry_count=2,
        max_retries=3,
        scheduled_for=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db_session.add(notif)
    await db_session.commit()

    with patch.object(resend_client, "send_email", side_effect=ResendTransientError("Connection timed out")):
        await process_single_notification(db_session, notif)

    refreshed = (await db_session.execute(
        select(Notification).where(Notification.idempotency_key == "test-notif-dead-letter-key")
    )).scalar_one()

    assert refreshed.status == "DEAD"
    assert refreshed.retry_count == 3
    assert "Max retries exceeded" in refreshed.last_error


@pytest.mark.asyncio
async def test_outbox_worker_marks_failed_on_fatal_client_error(db_session: AsyncSession):
    notif = Notification(
        idempotency_key="test-notif-fatal-error-key",
        recipient_email="invalid_email",
        recipient_name="Invalid Candidate",
        template_name="payment_successful",
        subject="Payment Successful",
        template_data={"candidate_name": "Invalid Candidate"},
        status="PENDING",
        retry_count=0,
        max_retries=3,
        scheduled_for=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db_session.add(notif)
    await db_session.commit()

    with patch.object(resend_client, "send_email", side_effect=ResendFatalError("400 Bad Request: Invalid email format")):
        await process_single_notification(db_session, notif)

    refreshed = (await db_session.execute(
        select(Notification).where(Notification.idempotency_key == "test-notif-fatal-error-key")
    )).scalar_one()

    assert refreshed.status == "FAILED"
    assert "Fatal error" in refreshed.last_error
