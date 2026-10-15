import io
import zipfile
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.user_repository import UserRepository


def make_dummy_pdf() -> bytes:
    """Generate dummy bytes matching the PDF specification magic header."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"


def make_dummy_docx() -> bytes:
    """Generate minimal valid DOCX zip archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0" encoding="UTF-8"?><Types></Types>')
        zf.writestr("word/document.xml", b'<?xml version="1.0" encoding="UTF-8"?><w:document></w:document>')
    return buf.getvalue()


@pytest.mark.asyncio
async def test_file_upload_security_valid_pdf_and_docx(async_client: AsyncClient, db_session: AsyncSession):
    # Register & Login candidate
    user_repo = UserRepository(db_session)
    cand, _ = await user_repo.create_user(
        email="upload_test@example.com",
        password="Password123!",
        full_name="Upload Candidate",
        phone="+919876543111",
        is_email_verified=True,
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "upload_test@example.com", "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Valid PDF upload
    pdf_bytes = make_dummy_pdf()
    files = {"file": ("my_resume.pdf", pdf_bytes, "application/pdf")}
    data = {"file_purpose": "RESUME"}
    res_pdf = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files=files,
        data=data
    )
    assert res_pdf.status_code == 201
    assert "file_id" in res_pdf.json()
    assert res_pdf.json()["mime_type"] == "application/pdf"

    # 2. Valid DOCX upload
    docx_bytes = make_dummy_docx()
    files = {"file": ("my_job_description.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"file_purpose": "JOB_DESCRIPTION"}
    res_docx = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files=files,
        data=data
    )
    assert res_docx.status_code == 201
    assert res_docx.json()["file_purpose"] == "JOB_DESCRIPTION"


@pytest.mark.asyncio
async def test_file_upload_security_rejections(async_client: AsyncClient, db_session: AsyncSession):
    # Register & Login
    user_repo = UserRepository(db_session)
    await user_repo.create_user(
        email="upload_reject@example.com",
        password="Password123!",
        full_name="Reject Candidate",
        phone="+919876543112",
        is_email_verified=True,
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "upload_reject@example.com", "password": "Password123!"}
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 1. Disallowed extension (e.g. .exe or .sh)
    files = {"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/octet-stream")}
    res_bad_ext = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files=files,
        data={"file_purpose": "RESUME"}
    )
    assert res_bad_ext.status_code == 400
    assert "Invalid file extension" in res_bad_ext.json()["detail"]

    # 2. Fake PDF with wrong magic bytes (shell script disguised as .pdf)
    fake_pdf = b"#!/bin/bash\necho 'hacked'"
    files = {"file": ("resume.pdf", fake_pdf, "application/pdf")}
    res_fake_pdf = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files=files,
        data={"file_purpose": "RESUME"}
    )
    assert res_fake_pdf.status_code == 400
    assert "invalid magic bytes" in res_fake_pdf.json()["detail"]

    # 3. Fake DOCX (plain text disguised as .docx)
    files = {"file": ("jd.docx", b"Hello this is not a zip archive", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    res_fake_docx = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files=files,
        data={"file_purpose": "JOB_DESCRIPTION"}
    )
    assert res_fake_docx.status_code == 400
    assert "missing ZIP header" in res_fake_docx.json()["detail"]

    # 4. Oversized file (> 5 MB)
    large_pdf = b"%PDF-1.4\n" + (b"0" * (5 * 1024 * 1024 + 100))
    files = {"file": ("giant.pdf", large_pdf, "application/pdf")}
    res_large = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files=files,
        data={"file_purpose": "RESUME"}
    )
    assert res_large.status_code == 413


@pytest.mark.asyncio
async def test_booking_draft_creation_and_listing(async_client: AsyncClient, db_session: AsyncSession):
    # Ensure categories seeded
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    # Create candidate
    user_repo = UserRepository(db_session)
    cand, _ = await user_repo.create_user(
        email="booking_cand@example.com",
        password="Password123!",
        full_name="Booking Candidate",
        phone="+919876543113",
        is_email_verified=True,
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "booking_cand@example.com", "password": "Password123!"}
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # Upload resume
    pdf_bytes = make_dummy_pdf()
    up_res = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers,
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
        data={"file_purpose": "RESUME"}
    )
    resume_file_id = up_res.json()["file_id"]

    # Create booking draft
    booking_payload = {
        "category_slug": "system-design",
        "resume_file_id": resume_file_id,
        "years_experience": 4.5,
        "target_role": "Staff Software Engineer",
        "current_company": "Apex Corp",
        "technical_skills": ["Distributed Systems", "Kafka", "PostgreSQL"],
        "jd_text": "Looking for senior distributed systems engineer...",
        "additional_notes": "Interested in deep dive on caching and fault tolerance."
    }
    draft_res = await async_client.post(
        "/api/v1/candidate/bookings/draft",
        headers=headers,
        json=booking_payload
    )
    assert draft_res.status_code == 201
    draft_data = draft_res.json()
    assert draft_data["booking_reference"].startswith("MOCK-")
    assert draft_data["amount_paise"] == 19900  # ₹199
    assert draft_data["currency"] == "INR"
    assert draft_data["category_slug"] == "system-design"
    assert draft_data["status_headline"] == "Booking Created"
    booking_id = draft_data["id"]

    # List bookings
    list_res = await async_client.get("/api/v1/candidate/bookings", headers=headers)
    assert list_res.status_code == 200
    bookings = list_res.json()
    assert len(bookings) >= 1
    assert bookings[0]["id"] == booking_id

    # Download resume
    download_res = await async_client.get(
        f"/api/v1/candidate/files/{resume_file_id}/download",
        headers=headers
    )
    assert download_res.status_code == 200
    assert download_res.content == pdf_bytes


@pytest.mark.asyncio
async def test_anti_idor_protection(async_client: AsyncClient, db_session: AsyncSession):
    # Ensure categories seeded
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    user_repo = UserRepository(db_session)
    # User A
    cand_a, _ = await user_repo.create_user(
        email="cand_a@example.com",
        password="Password123!",
        full_name="Candidate A",
        phone="+919876543114",
        is_email_verified=True,
    )
    login_a = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "cand_a@example.com", "password": "Password123!"}
    )
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

    # User B
    cand_b, _ = await user_repo.create_user(
        email="cand_b@example.com",
        password="Password123!",
        full_name="Candidate B",
        phone="+919876543115",
        is_email_verified=True,
    )
    login_b = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "cand_b@example.com", "password": "Password123!"}
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    # User A uploads resume & creates booking
    up_res = await async_client.post(
        "/api/v1/candidate/upload",
        headers=headers_a,
        files={"file": ("cand_a_resume.pdf", make_dummy_pdf(), "application/pdf")},
        data={"file_purpose": "RESUME"}
    )
    file_id_a = up_res.json()["file_id"]

    draft_res = await async_client.post(
        "/api/v1/candidate/bookings/draft",
        headers=headers_a,
        json={
            "category_slug": "dsa",
            "resume_file_id": file_id_a,
            "years_experience": 2.0,
            "target_role": "SDE 2",
            "technical_skills": ["Java", "Algorithms"]
        }
    )
    booking_id_a = draft_res.json()["id"]

    # IDOR Test 1: User B attempts to access User A's booking -> 404 Forbidden/Not Found!
    res_idor_booking = await async_client.get(
        f"/api/v1/candidate/bookings/{booking_id_a}",
        headers=headers_b
    )
    assert res_idor_booking.status_code == 404

    # IDOR Test 2: User B attempts to download User A's file -> 404 Forbidden/Not Found!
    res_idor_file = await async_client.get(
        f"/api/v1/candidate/files/{file_id_a}/download",
        headers=headers_b
    )
    assert res_idor_file.status_code == 404


@pytest.mark.asyncio
async def test_instant_frictionless_booking_flow(async_client: AsyncClient, db_session: AsyncSession):
    # Ensure categories seeded
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    # 1. Guest file upload without auth token
    pdf_bytes = make_dummy_pdf()
    up_res = await async_client.post(
        "/api/v1/candidate/upload",
        files={"file": ("guest_resume.pdf", pdf_bytes, "application/pdf")},
        data={"file_purpose": "RESUME"},
    )
    assert up_res.status_code == 201
    file_id = up_res.json()["file_id"]
    assert file_id is not None

    # 2. Instant booking creation with zero pre-sign-in barrier
    instant_payload = {
        "full_name": "Instant Test Candidate",
        "email": "instant_test@example.com",
        "phone": "+919876543999",
        "category_slug": "frontend",
        "resume_file_id": file_id,
        "years_experience": 3.5,
        "current_company": "Acme Tech",
        "target_role": "Senior Frontend Engineer",
        "technical_skills": ["React", "TypeScript", "Tailwind CSS"],
        "job_description_text": "Looking for senior Next.js architect",
        "additional_notes": "Please focus on SSR architecture",
    }

    res_booking = await async_client.post(
        "/api/v1/candidate/bookings/instant",
        json=instant_payload,
    )
    assert res_booking.status_code == 201
    booking_data = res_booking.json()

    assert booking_data["booking_reference"].startswith("MOCK-")
    assert booking_data["amount_paise"] == 19900
    assert booking_data["currency"] == "INR"
    assert booking_data["order_id"].startswith("order_")
    assert booking_data["access_token"] is not None
    assert booking_data["category_title"] == "Frontend Mock Interview"

    # 3. Candidate can immediately query booking using auto-provisioned token
    cand_token = booking_data["access_token"]
    booking_id = booking_data["booking_id"]

    res_fetch = await async_client.get(
        f"/api/v1/candidate/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {cand_token}"},
    )
    assert res_fetch.status_code == 200
    fetched_data = res_fetch.json()
    assert fetched_data["booking_reference"] == booking_data["booking_reference"]
    assert fetched_data["amount_paise"] == 19900
    assert fetched_data["currency"] == "INR"
    assert fetched_data["duration_display"] == "45–60 minutes"
    assert fetched_data["category_title"] == "Frontend Mock Interview"
    assert fetched_data["target_role"] == "Senior Frontend Engineer"

