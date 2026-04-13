# backend/tests/test_placement_test.py
import pytest
from tests.conftest import TestSessionFactory, make_fake_init_data
from app.models.exercise import PlacementTestQuestion
from app.models.enums import ExerciseTypeEnum


@pytest.fixture
def auth_headers():
    return {"X-Telegram-Init-Data": make_fake_init_data()}


async def seed_placement_questions(count: int = 20):
    async with TestSessionFactory() as session:
        for i in range(count):
            q = PlacementTestQuestion(
                type=ExerciseTypeEnum.MULTIPLE_CHOICE,
                content={"question": f"Q{i}", "options": [{"id": "a", "text": "opt"}], "correct_id": "a"},
                correct_answer={"correct_id": "a"},
                order_index=i,
                is_active=True,
            )
            session.add(q)
        await session.commit()


async def test_get_placement_questions(client, auth_headers):
    await seed_placement_questions(20)
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/placement-test/questions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert 15 <= len(data["questions"]) <= 20


async def test_placement_test_pass(client, auth_headers):
    await seed_placement_questions(20)
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        "/api/v1/placement-test/complete",
        json={"score": 17, "total": 20, "skipped": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["placement_status"] == "passed"
    assert data["a1_skipped"] is True


async def test_placement_test_fail(client, auth_headers):
    await seed_placement_questions(20)
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        "/api/v1/placement-test/complete",
        json={"score": 5, "total": 20, "skipped": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["placement_status"] == "failed"
    assert response.json()["a1_skipped"] is False


async def test_placement_test_skip(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        "/api/v1/placement-test/complete",
        json={"score": 0, "total": 0, "skipped": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["placement_status"] == "skipped"


async def test_placement_cannot_repeat(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    await client.post(
        "/api/v1/placement-test/complete",
        json={"score": 0, "total": 0, "skipped": True},
        headers=auth_headers,
    )
    response = await client.post(
        "/api/v1/placement-test/complete",
        json={"score": 0, "total": 0, "skipped": True},
        headers=auth_headers,
    )
    assert response.status_code == 409


async def test_patch_settings(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.patch(
        "/api/v1/settings",
        json={"show_instruction_translation": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["show_instruction_translation"] is False
