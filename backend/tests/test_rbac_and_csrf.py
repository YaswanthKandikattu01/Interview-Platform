import pytest
from httpx import AsyncClient
from app.api.deps import get_current_admin
from app.main import app


from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository


# Add a test admin-only route for RBAC testing
@app.get("/api/v1/test-admin-only-endpoint")
async def sample_admin_endpoint(admin=pytest.importorskip("fastapi").Depends(get_current_admin)):
    return {"message": "Welcome Admin", "admin_id": admin.id}


@pytest.mark.asyncio
async def test_rbac_candidate_blocked_from_admin(async_client: AsyncClient):
    # Register candidate
    reg_payload = {
        "email": "cand_rbac@example.com",
        "password": "Password123!",
        "full_name": "Candidate RBAC",
        "phone": "+919876543299",
        "years_experience": 2.0,
        "target_role": "Backend Engineer"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "cand_rbac@example.com", "password": "Password123!"}
    )
    token = login_res.json()["access_token"]

    # Candidate attempts to access admin-only endpoint -> must receive 403 Forbidden!
    admin_access = await async_client.get(
        "/api/v1/test-admin-only-endpoint",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert admin_access.status_code == 403
    assert "Administrative privileges required" in admin_access.json()["detail"]


@pytest.mark.asyncio
async def test_admin_login_and_access(async_client: AsyncClient, db_session: AsyncSession):
    # Seed admin user in test db
    repo = UserRepository(db_session)
    existing_admin = await repo.get_by_email("admin@mockinterviews.dev")
    if not existing_admin:
        await repo.create_user(
            email="admin@mockinterviews.dev",
            password="AdminSecurePassword123!",
            full_name="Interviewer Admin",
            phone="+919876543210",
            role="ADMIN",
            is_email_verified=True,
        )

    # Log in as the administrator
    admin_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@mockinterviews.dev", "password": "AdminSecurePassword123!"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    assert admin_login.json()["user"]["role"] == "ADMIN"

    # Admin access must succeed (200 OK)
    admin_res = await async_client.get(
        "/api/v1/test-admin-only-endpoint",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["message"] == "Welcome Admin"


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(async_client: AsyncClient):
    # 1. Register candidate
    reg_payload = {
        "email": "reset_test@example.com",
        "password": "InitialPassword123!",
        "full_name": "Reset Candidate",
        "phone": "+919876543277",
        "years_experience": 1.0,
        "target_role": "QA Engineer"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Request forgot password
    forgot_res = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset_test@example.com"}
    )
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["dev_reset_token"]
    assert reset_token is not None

    # 3. Reset password with new password
    reset_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewSecurePassword456!"}
    )
    assert reset_res.status_code == 200

    # 4. Old password must fail
    old_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "reset_test@example.com", "password": "InitialPassword123!"}
    )
    assert old_login.status_code == 401

    # 5. New password must succeed
    new_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "reset_test@example.com", "password": "NewSecurePassword456!"}
    )
    assert new_login.status_code == 200
    assert new_login.json()["user"]["email"] == "reset_test@example.com"
