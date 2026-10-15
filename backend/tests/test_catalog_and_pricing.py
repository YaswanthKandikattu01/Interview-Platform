import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_get_categories_returns_exactly_six(async_client: AsyncClient, db_session: AsyncSession):
    # Ensure test database has categories seeded
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    response = await async_client.get("/api/v1/categories")
    assert response.status_code == 200
    categories = response.json()

    # STRICT CRITERIA: Exactly 6 categories
    assert len(categories) == 6

    expected_slugs = [
        "system-design",
        "dsa",
        "ai-engineer",
        "full-stack",
        "frontend",
        "backend",
    ]
    actual_slugs = [cat["slug"] for cat in categories]
    assert actual_slugs == expected_slugs

    # STRICT CRITERIA: One package only: 45–60 minutes, ₹199 (19,900 paise)
    for cat in categories:
        price = cat["active_price"]
        assert price is not None
        assert price["amount_paise"] == 19900
        assert price["currency"] == "INR"
        assert price["duration_display"] == "45–60 minutes"
        assert price["duration_min_minutes"] == 45
        assert price["duration_max_minutes"] == 60
        assert len(cat["detailed_topics"]) >= 3


@pytest.mark.asyncio
async def test_get_category_by_slug_and_404(async_client: AsyncClient, db_session: AsyncSession):
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    # Valid category
    res = await async_client.get("/api/v1/categories/system-design")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "System Design Mock Interview"
    assert data["active_price"]["amount_paise"] == 19900

    # Disallowed category (e.g. data-analyst, devops) must return 404
    res_invalid = await async_client.get("/api/v1/categories/data-analyst")
    assert res_invalid.status_code == 404


@pytest.mark.asyncio
async def test_canonical_pricing_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/pricing")
    assert response.status_code == 200
    data = response.json()
    assert data["amount_paise"] == 19900
    assert data["currency"] == "INR"
    assert data["price_formatted"] == "₹199"
    assert data["duration_display"] == "45–60 minutes"
    assert "human expert interviewer" in data["guarantee"]


@pytest.mark.asyncio
async def test_admin_pricing_update_flow(async_client: AsyncClient, db_session: AsyncSession):
    cat_repo = CatalogRepository(db_session)
    await cat_repo.seed_categories_and_prices()

    # 1. Create candidate user
    user_repo = UserRepository(db_session)
    candidate_user, _ = await user_repo.create_user(
        email="candidate_price_test@example.com",
        password="Password123!",
        full_name="Price Candidate",
        phone="+919876543200",
        role="CANDIDATE",
        is_email_verified=True,
    )
    cand_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "candidate_price_test@example.com", "password": "Password123!"}
    )
    cand_token = cand_login.json()["access_token"]

    # 2. Seed admin user
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

    # 3. Get category ID for system-design
    cat = await cat_repo.get_category_by_slug("system-design")
    assert cat is not None
    cat_id = cat.id

    # 4. Candidate attempts to update price -> 403 Forbidden
    cand_attempt = await async_client.put(
        f"/api/v1/admin/categories/{cat_id}/price",
        headers={"Authorization": f"Bearer {cand_token}"},
        json={"amount_paise": 29900}
    )
    assert cand_attempt.status_code == 403

    # 5. Admin updates price to 24,900 paise
    admin_update = await async_client.put(
        f"/api/v1/admin/categories/{cat_id}/price",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paise": 24900}
    )
    assert admin_update.status_code == 200
    new_price = admin_update.json()
    assert new_price["amount_paise"] == 24900
    assert new_price["is_active"] is True

    # 6. Verify category now returns the new active price
    get_updated = await async_client.get("/api/v1/categories/system-design")
    assert get_updated.status_code == 200
    assert get_updated.json()["active_price"]["amount_paise"] == 24900

    # 7. Test invalid price validation (e.g. 0 or negative paise)
    invalid_price = await async_client.put(
        f"/api/v1/admin/categories/{cat_id}/price",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paise": 0}
    )
    assert invalid_price.status_code in [422, 400]
