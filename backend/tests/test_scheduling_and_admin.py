import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.user_repository import UserRepository
from app.models.notification import Notification
from app.models.interview import InterviewRequest
from app.integrations.razorpay_client import razorpay_client


async def setup_admin_and_paid_booking(async_client: AsyncClient, db_session: AsyncSession, suffix: str):
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()
    user_repo = UserRepository(db_session)

    # 1. Admin
    admin_email = f"admin_{suffix}@mockinterviews.dev"
    admin_user = await user_repo.get_by_email(admin_email)
    if not admin_user:
        admin_user, _ = await user_repo.create_user(
            email=admin_email,
            password="AdminPassword123!",
            full_name="Interviewer Admin",
            phone="+919999988888",
            role="ADMIN",
            is_email_verified=True,
        )
    admin_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": admin_email, "password": "AdminPassword123!"}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Candidate
    cand_email = f"cand_{suffix}@example.com"
    cand_user, _ = await user_repo.create_user(
        email=cand_email,
        password="Password123!",
        full_name=f"Candidate {suffix}",
        phone="+919876543210",
        role="CANDIDATE",
        is_email_verified=True,
    )
    cand_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": cand_email, "password": "Password123!"}
    )
    cand_token = cand_login.json()["access_token"]
    cand_headers = {"Authorization": f"Bearer {cand_token}"}

    # 3. Upload resume & draft booking
    resume_res = await async_client.post(
        "/api/v1/candidate/upload",
        headers=cand_headers,
        files={"file": ("resume.pdf", b"%PDF-1.4 minimal test pdf content", "application/pdf")},
        data={"file_purpose": "RESUME"},
    )
    resume_file_id = resume_res.json()["file_id"]

    draft_res = await async_client.post(
        "/api/v1/candidate/bookings/draft",
        headers=cand_headers,
        json={
            "category_slug": "system-design",
            "years_experience": 3.5,
            "target_role": "Backend Engineer",
            "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
            "resume_file_id": resume_file_id,
            "jd_text": "Looking for backend engineer experienced in building REST APIs.",
        }
    )
    booking_id = draft_res.json()["id"]

    # 4. Create Order & Verify Payment (simulate captured payment)
    order_res = await async_client.post(
        "/api/v1/payments/create-order",
        headers=cand_headers,
        json={"booking_id": booking_id}
    )
    order_id = order_res.json()["order_id"]
    payment_id = f"pay_{suffix}_12345"
    valid_signature = razorpay_client.compute_signature(f"{order_id}|{payment_id}")

    await async_client.post(
        "/api/v1/payments/verify",
        headers=cand_headers,
        json={
            "booking_id": booking_id,
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": valid_signature
        }
    )

    return admin_headers, cand_headers, booking_id, admin_user.id


@pytest.mark.asyncio
async def test_admin_contact_recording_and_sla_update(async_client: AsyncClient, db_session: AsyncSession):
    admin_h, cand_h, booking_id, _ = await setup_admin_and_paid_booking(async_client, db_session, "contact_test")

    # 1. Candidate forbidden from recording contact
    cand_attempt = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/contact",
        headers=cand_h,
        json={"channel": "EMAIL", "notes": "Candidate tried to mark self contacted"}
    )
    assert cand_attempt.status_code == 403

    # 2. Admin records contact
    admin_contact = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/contact",
        headers=admin_h,
        json={"channel": "EMAIL", "notes": "Sent personalized introduction email coordinating interview schedule."}
    )
    assert admin_contact.status_code == 200
    c_data = admin_contact.json()
    assert c_data["status"] == "contact_recorded"
    assert c_data["contact_status"] == "CONTACTED"
    assert c_data["first_contacted_at"] is not None

    # 3. Verify in detail endpoint
    detail_res = await async_client.get(f"/api/v1/admin/bookings/{booking_id}", headers=admin_h)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["sla"]["contact_status"] == "CONTACTED"
    assert len(detail["contact_logs"]) == 1
    assert "Sent personalized introduction" in detail["contact_logs"][0]["notes"]


@pytest.mark.asyncio
async def test_interview_scheduling_duration_validation(async_client: AsyncClient, db_session: AsyncSession):
    admin_h, _, booking_id, _ = await setup_admin_and_paid_booking(async_client, db_session, "duration_test")
    base_time = datetime.now(timezone.utc) + timedelta(days=2)

    # 1. Invalid duration: 30 minutes (must be 45-60)
    res_30 = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": base_time.isoformat(),
            "scheduled_end": (base_time + timedelta(minutes=30)).isoformat(),
            "meeting_url": "https://meet.google.com/dur-30m-test",
        }
    )
    assert res_30.status_code in (400, 422)

    # 2. Invalid duration: 75 minutes (must be 45-60)
    res_75 = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": base_time.isoformat(),
            "scheduled_end": (base_time + timedelta(minutes=75)).isoformat(),
            "meeting_url": "https://meet.google.com/dur-75m-test",
        }
    )
    assert res_75.status_code in (400, 422)

    # 3. Valid duration: 50 minutes (strictly within 45-60 minutes range)
    res_50 = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": base_time.isoformat(),
            "scheduled_end": (base_time + timedelta(minutes=50)).isoformat(),
            "meeting_url": "https://meet.google.com/dur-50m-test",
            "joining_instructions": "Bring your laptop and IDE ready.",
        }
    )
    assert res_50.status_code == 200
    sched_data = res_50.json()
    assert sched_data["status"] == "scheduled"
    assert sched_data["duration_minutes"] == 50

    # 4. Verify outbox notification for candidate was enqueued
    notifs = (await db_session.execute(
        select(Notification).where(
            Notification.interview_request_id == booking_id,
            Notification.template_name == "interview_scheduled"
        )
    )).scalars().all()
    assert len(notifs) >= 1
    assert "dur-50m-test" in notifs[0].template_data["meeting_url"]


@pytest.mark.asyncio
async def test_interviewer_overlap_prevention(async_client: AsyncClient, db_session: AsyncSession):
    # Setup two distinct bookings
    admin_h, _, booking_1, _ = await setup_admin_and_paid_booking(async_client, db_session, "overlap_1")
    _, _, booking_2, _ = await setup_admin_and_paid_booking(async_client, db_session, "overlap_2")

    slot_1_start = datetime.now(timezone.utc) + timedelta(days=3, hours=10)
    slot_1_end = slot_1_start + timedelta(minutes=50)

    # Schedule booking 1: 10:00 to 10:50
    res_1 = await async_client.post(
        f"/api/v1/admin/bookings/{booking_1}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": slot_1_start.isoformat(),
            "scheduled_end": slot_1_end.isoformat(),
            "meeting_url": "https://meet.google.com/session-1",
        }
    )
    assert res_1.status_code == 200

    # Attempt to schedule booking 2 overlapping: 10:30 to 11:20 -> MUST BE REJECTED (409 Conflict)
    slot_overlap_start = slot_1_start + timedelta(minutes=30)
    slot_overlap_end = slot_overlap_start + timedelta(minutes=50)
    res_overlap = await async_client.post(
        f"/api/v1/admin/bookings/{booking_2}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": slot_overlap_start.isoformat(),
            "scheduled_end": slot_overlap_end.isoformat(),
            "meeting_url": "https://meet.google.com/session-overlap",
        }
    )
    assert res_overlap.status_code == 409
    assert "conflict" in res_overlap.json()["detail"].lower()

    # Schedule booking 2 non-overlapping: 11:00 to 11:50 -> SUCCEEDS
    slot_2_start = slot_1_end + timedelta(minutes=10)
    slot_2_end = slot_2_start + timedelta(minutes=50)
    res_2 = await async_client.post(
        f"/api/v1/admin/bookings/{booking_2}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": slot_2_start.isoformat(),
            "scheduled_end": slot_2_end.isoformat(),
            "meeting_url": "https://meet.google.com/session-2",
        }
    )
    assert res_2.status_code == 200


@pytest.mark.asyncio
async def test_reschedule_complete_and_cancel_lifecycle(async_client: AsyncClient, db_session: AsyncSession):
    admin_h, _, booking_id, _ = await setup_admin_and_paid_booking(async_client, db_session, "lifecycle")
    start = datetime.now(timezone.utc) + timedelta(days=4)
    end = start + timedelta(minutes=55)

    # 1. Schedule
    await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/schedule",
        headers=admin_h,
        json={
            "scheduled_start": start.isoformat(),
            "scheduled_end": end.isoformat(),
            "meeting_url": "https://meet.google.com/initial-meet",
        }
    )

    # 2. Reschedule
    new_start = start + timedelta(hours=3)
    new_end = new_start + timedelta(minutes=50)
    resched = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/reschedule",
        headers=admin_h,
        json={
            "scheduled_start": new_start.isoformat(),
            "scheduled_end": new_end.isoformat(),
            "reason": "Interviewer requested 3 hour shift due to tech conference",
        }
    )
    assert resched.status_code == 200
    assert resched.json()["status"] == "rescheduled"

    # 3. Complete interview
    comp = await async_client.post(
        f"/api/v1/admin/bookings/{booking_id}/complete",
        headers=admin_h,
        json={
            "strengths": "Strong knowledge of system architecture, clean database schema design.",
            "areas_for_improvement": "Could improve on distributed locking edge cases under network partitions.",
            "technical_rating": 4,
            "communication_rating": 5,
            "recommendation_summary": "Ready for Senior Backend Engineer roles.",
            "is_shared_with_candidate": True,
        }
    )
    assert comp.status_code == 200
    assert comp.json()["status"] == "completed"

    # 4. Cancel a different booking with refund
    _, _, booking_cancel, _ = await setup_admin_and_paid_booking(async_client, db_session, "cancel_flow")
    canc = await async_client.post(
        f"/api/v1/admin/bookings/{booking_cancel}/cancel",
        headers=admin_h,
        json={
            "reason": "Candidate emergency medical conflict",
            "initiate_refund": True,
        }
    )
    assert canc.status_code == 200
    assert canc.json()["status"] == "cancelled"
    assert canc.json()["refund_status"] == "refund_processed"


@pytest.mark.asyncio
async def test_admin_overview_metrics_and_search_filter(async_client: AsyncClient, db_session: AsyncSession):
    admin_h, _, booking_id, _ = await setup_admin_and_paid_booking(async_client, db_session, "metrics_filter")

    # 1. Overview metrics
    overview_res = await async_client.get("/api/v1/admin/overview", headers=admin_h)
    assert overview_res.status_code == 200
    metrics = overview_res.json()
    assert "total_revenue_paise" in metrics
    assert "total_bookings" in metrics
    assert metrics["total_bookings"] >= 1
    assert "awaiting_contact_count" in metrics
    assert "upcoming_interviews" in metrics

    # 2. List bookings with pagination and filters
    list_res = await async_client.get(
        "/api/v1/admin/bookings?search=metrics_filter",
        headers=admin_h
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["items"][0]["booking_reference"].startswith("MOCK-")
