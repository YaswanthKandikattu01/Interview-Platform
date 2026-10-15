import json
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.user_repository import UserRepository
from app.repositories.booking_repository import BookingRepository
from app.integrations.razorpay_client import razorpay_client


def make_dummy_pdf() -> bytes:
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"


async def setup_candidate_and_booking(async_client: AsyncClient, db_session: AsyncSession, email: str):
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    user_repo = UserRepository(db_session)
    cand, _ = await user_repo.create_user(
        email=email,
        password="Password123!",
        full_name="Payment Candidate",
        phone="+919876543333",
        is_email_verified=True,
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload resume
    up_res = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files={"file": ("resume.pdf", make_dummy_pdf(), "application/pdf")},
        data={"file_purpose": "RESUME"}
    )
    file_id = up_res.json()["file_id"]

    # Draft booking
    draft_res = await async_client.post(
        "/api/v1/candidate/bookings/draft",
        headers=headers,
        json={
            "category_slug": "system-design",
            "resume_file_id": file_id,
            "years_experience": 3.0,
            "target_role": "Backend Architect",
        }
    )
    booking_id = draft_res.json()["id"]
    return cand, headers, booking_id


@pytest.mark.asyncio
async def test_create_order_for_booking(async_client: AsyncClient, db_session: AsyncSession):
    cand, headers, booking_id = await setup_candidate_and_booking(async_client, db_session, "order_test@example.com")

    # Create Razorpay order
    res = await async_client.post(
        "/api/v1/payments/create-order",
        headers=headers,
        json={"booking_id": booking_id}
    )
    assert res.status_code == 201
    data = res.json()
    assert "order_id" in data
    assert data["order_id"].startswith("order_")
    assert data["amount_paise"] == 19900  # Exactly ₹199 (19,900 paise)
    assert data["currency"] == "INR"
    assert data["category_title"] == "System Design Mock Interview"


@pytest.mark.asyncio
async def test_verify_checkout_signature_and_capture(async_client: AsyncClient, db_session: AsyncSession):
    cand, headers, booking_id = await setup_candidate_and_booking(async_client, db_session, "verify_test@example.com")

    # 1. Create order
    order_res = await async_client.post(
        "/api/v1/payments/create-order",
        headers=headers,
        json={"booking_id": booking_id}
    )
    order_id = order_res.json()["order_id"]

    # 2. Simulate successful payment ID & compute valid HMAC signature
    payment_id = "pay_test_99999"
    valid_signature = razorpay_client.compute_signature(f"{order_id}|{payment_id}")

    # 3. Test Invalid Signature Rejection
    bad_res = await async_client.post(
        "/api/v1/payments/verify",
        headers=headers,
        json={
            "booking_id": booking_id,
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": "invalid_tampered_signature"
        }
    )
    assert bad_res.status_code == 400
    assert "Invalid Razorpay payment signature" in bad_res.json()["detail"]

    # 4. Test Valid Signature Verification
    verify_res = await async_client.post(
        "/api/v1/payments/verify",
        headers=headers,
        json={
            "booking_id": booking_id,
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": valid_signature
        }
    )
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["payment_status"] == "CAPTURED"
    assert v_data["scheduling_status"] == "PAID_AWAITING_CONTACT"
    assert v_data["razorpay_payment_id"] == payment_id
    assert v_data["contact_deadline_ist"] is not None

    # 5. Check Candidate Dashboard shows "Payment Confirmed"
    dash_res = await async_client.get("/api/v1/candidate/bookings", headers=headers)
    assert dash_res.status_code == 200
    bookings = dash_res.json()
    assert bookings[0]["payment_status"] == "CAPTURED"
    assert "Payment Confirmed" in bookings[0]["status_headline"]


@pytest.mark.asyncio
async def test_webhook_processing_and_deduplication(async_client: AsyncClient, db_session: AsyncSession):
    cand, headers, booking_id = await setup_candidate_and_booking(async_client, db_session, "webhook_test@example.com")

    # Create order
    order_res = await async_client.post(
        "/api/v1/payments/create-order",
        headers=headers,
        json={"booking_id": booking_id}
    )
    order_id = order_res.json()["order_id"]

    # Construct standard Razorpay payment.captured webhook payload
    webhook_payload = {
        "event_id": "evt_capture_1001",
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_hook_1001",
                    "order_id": order_id,
                    "amount": 19900,
                    "currency": "INR",
                    "status": "captured",
                    "method": "upi",
                    "vpa": "candidate@upi"
                }
            }
        }
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")

    # Compute webhook HMAC signature using webhook secret
    import hmac
    import hashlib
    valid_hook_sig = hmac.new(
        razorpay_client.webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    # 1. Invalid Webhook Signature Rejected
    bad_hook = await async_client.post(
        "/api/v1/payments/webhook",
        headers={"X-Razorpay-Signature": "tampered_sig"},
        content=raw_body
    )
    assert bad_hook.status_code == 400

    # 2. Valid Webhook Processed
    good_hook = await async_client.post(
        "/api/v1/payments/webhook",
        headers={"X-Razorpay-Signature": "custom" and valid_hook_sig},
        content=raw_body
    )
    assert good_hook.status_code == 200
    assert good_hook.json()["status"] == "success"

    # 3. Duplicate Webhook Event Deduplication (Idempotency)
    dup_hook = await async_client.post(
        "/api/v1/payments/webhook",
        headers={"X-Razorpay-Signature": valid_hook_sig},
        content=raw_body
    )
    assert dup_hook.status_code == 200
    assert dup_hook.json()["status"] == "already_processed"


@pytest.mark.asyncio
async def test_admin_process_refund_flow(async_client: AsyncClient, db_session: AsyncSession):
    cand, headers, booking_id = await setup_candidate_and_booking(async_client, db_session, "refund_cand@example.com")

    # Create order & capture payment
    order_res = await async_client.post(
        "/api/v1/payments/create-order",
        headers=headers,
        json={"booking_id": booking_id}
    )
    order_id = order_res.json()["order_id"]
    payment_id = "pay_refund_test"
    valid_signature = razorpay_client.compute_signature(f"{order_id}|{payment_id}")

    await async_client.post(
        "/api/v1/payments/verify",
        headers=headers,
        json={
            "booking_id": booking_id,
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": valid_signature
        }
    )

    # 1. Candidate attempts to trigger refund directly -> 403 Forbidden
    cand_refund = await async_client.post(
        "/api/v1/payments/refund",
        headers=headers,
        json={"booking_id": booking_id, "reason": "Candidate wants refund"}
    )
    assert cand_refund.status_code == 403

    # 2. Seed Admin user & login
    user_repo = UserRepository(db_session)
    existing_admin = await user_repo.get_by_email("admin@mockinterviews.dev")
    if not existing_admin:
        await user_repo.create_user(
            email="admin@mockinterviews.dev",
            password="AdminSecurePassword123!",
            full_name="Admin User",
            phone="+919876543210",
            role="ADMIN",
            is_email_verified=True,
        )
    admin_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@mockinterviews.dev", "password": "AdminSecurePassword123!"}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Admin processes refund
    admin_refund = await async_client.post(
        "/api/v1/payments/refund",
        headers=admin_headers,
        json={"booking_id": booking_id, "reason": "Candidate schedule conflict prior to outreach"}
    )
    assert admin_refund.status_code == 200
    ref_data = admin_refund.json()
    assert ref_data["status"] == "refund_processed"
    assert ref_data["amount_paise"] == 19900
    assert "razorpay_refund_id" in ref_data
