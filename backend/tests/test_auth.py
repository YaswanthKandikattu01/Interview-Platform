import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["timezone"] == "Asia/Kolkata"


@pytest.mark.asyncio
async def test_candidate_registration_and_duplicate_handling(async_client: AsyncClient):
    payload = {
        "email": "testcandidate@example.com",
        "password": "StrongPassword123!",
        "full_name": "Test Candidate",
        "phone": "+919876543211",
        "years_experience": 3.5,
        "current_company": "Tech Corp",
        "target_role": "Backend Engineer",
        "technical_skills": ["Python", "FastAPI", "PostgreSQL"]
    }
    # Register candidate
    res = await async_client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "user_id" in data
    assert data["email"] == "testcandidate@example.com"
    assert data["dev_verification_token"] is not None
    verification_token = data["dev_verification_token"]

    # Duplicate registration should return 409 Conflict
    dup_res = await async_client.post("/api/v1/auth/register", json=payload)
    assert dup_res.status_code == 409

    # Verify email
    verify_res = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"token": verification_token}
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["is_email_verified"] is True


@pytest.mark.asyncio
async def test_login_and_token_rotation(async_client: AsyncClient):
    # Register candidate
    reg_payload = {
        "email": "loginuser@example.com",
        "password": "CorrectPassword123!",
        "full_name": "Login User",
        "phone": "+919876543212",
        "years_experience": 2.0,
        "target_role": "Frontend Engineer",
        "technical_skills": ["React", "TypeScript"]
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    # Test invalid password
    invalid_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "loginuser@example.com", "password": "WrongPassword!"}
    )
    assert invalid_login.status_code == 401

    # Test valid login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "loginuser@example.com", "password": "CorrectPassword123!"}
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert "csrf_token" in login_data
    assert login_data["user"]["email"] == "loginuser@example.com"
    
    # Check HttpOnly cookies received
    cookies = login_res.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies
    initial_refresh_token = cookies["refresh_token"]

    # Test /me endpoint using the access_token in Authorization header
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["user"]["email"] == "loginuser@example.com"
    assert me_res.json()["profile"]["target_role"] == "Frontend Engineer"

    # Rotate refresh token
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh_token}
    )
    assert refresh_res.status_code == 200
    refresh_data = refresh_res.json()
    assert "access_token" in refresh_data
    assert refresh_res.cookies.get("refresh_token") is not None
    second_refresh_token = refresh_res.cookies["refresh_token"]
    assert second_refresh_token != initial_refresh_token

    # CRITICAL OWASP REUSE DETECTION TEST:
    # Attempting to reuse the revoked initial_refresh_token must be caught, and the token family invalidated!
    replay_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh_token}
    )
    assert replay_res.status_code == 401
    assert "Token reuse detected" in replay_res.json()["detail"]

    # Because family was revoked, the second token must ALSO now be rejected
    second_replay_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": second_refresh_token}
    )
    assert second_replay_res.status_code == 401


@pytest.mark.asyncio
async def test_logout_and_cookie_clearing(async_client: AsyncClient):
    # Register & Login
    reg_payload = {
        "email": "logoutuser@example.com",
        "password": "Password123!",
        "full_name": "Logout User",
        "phone": "+919876543213",
        "years_experience": 1.0,
        "target_role": "Full Stack Engineer"
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "logoutuser@example.com", "password": "Password123!"}
    )
    assert login_res.status_code == 200
    refresh_token = login_res.cookies["refresh_token"]

    # Logout
    logout_res = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert logout_res.status_code == 200

    # Ensure refresh token can no longer be used
    bad_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert bad_refresh.status_code == 401
