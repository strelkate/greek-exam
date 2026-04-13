import pytest
from tests.conftest import TestSessionFactory, make_fake_init_data
from app.models.curriculum import CurriculumUnit
from app.models.exercise import Exercise
from app.models.enums import LevelEnum, ExerciseTypeEnum


@pytest.fixture
def auth_headers():
    return {"X-Telegram-Init-Data": make_fake_init_data()}


async def create_unit_and_exercise(ex_type=ExerciseTypeEnum.MULTIPLE_CHOICE):
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(level=LevelEnum.A1, title="U1", order_index=1, is_published=True)
        session.add(unit)
        await session.flush()
        ex = Exercise(
            unit_id=unit.id,
            type=ex_type,
            order_index=1,
            content={"question": "Τι είναι;", "options": [{"id": "a", "text": "Σπίτι"}], "correct_id": "a"},
            audio_paths=[],
            is_published=True,
        )
        session.add(ex)
        await session.commit()
        return {"unit_id": unit.id, "exercise_id": ex.id}


async def test_get_exercise(client, auth_headers):
    data = await create_unit_and_exercise()
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get(f"/api/v1/exercises/{data['exercise_id']}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == data["exercise_id"]
    assert body["type"] == "multiple_choice"
    assert "content" in body
    assert "audio_paths" in body


async def test_get_exercise_not_found(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/exercises/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_get_unpublished_exercise_returns_404(client, auth_headers):
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(level=LevelEnum.A1, title="U1", order_index=1, is_published=True)
        session.add(unit)
        await session.flush()
        ex = Exercise(
            unit_id=unit.id, type=ExerciseTypeEnum.TRUE_FALSE,
            order_index=1, content={}, audio_paths=[], is_published=False,
        )
        session.add(ex)
        await session.commit()
        ex_id = ex.id

    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get(f"/api/v1/exercises/{ex_id}", headers=auth_headers)
    assert response.status_code == 404


async def test_complete_exercise_awards_xp(client, auth_headers):
    data = await create_unit_and_exercise()
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        f"/api/v1/exercises/{data['exercise_id']}/complete",
        json={"score": 4, "total": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["xp_earned"] >= 10
    assert "exercise_complete" in body["xp_breakdown"]
    assert body["unit_progress"]["exercises_completed"] == 1
    assert body["unit_progress"]["exercises_total"] >= 1


async def test_complete_exercise_updates_streak(client, auth_headers):
    data = await create_unit_and_exercise()
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        f"/api/v1/exercises/{data['exercise_id']}/complete",
        json={"score": 5, "total": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["streak_days"] >= 1
    assert isinstance(body["streak_updated"], bool)


async def test_complete_exercise_idempotent(client, auth_headers):
    data = await create_unit_and_exercise()
    await client.post("/api/v1/auth/session", headers=auth_headers)
    await client.post(
        f"/api/v1/exercises/{data['exercise_id']}/complete",
        json={"score": 5, "total": 5},
        headers=auth_headers,
    )
    response = await client.post(
        f"/api/v1/exercises/{data['exercise_id']}/complete",
        json={"score": 5, "total": 5},
        headers=auth_headers,
    )
    assert response.status_code == 409


async def test_mini_test_unlocked_when_all_done(client, auth_headers):
    """mini_test_unlocked becomes True when all non-flashcard exercises are completed."""
    data = await create_unit_and_exercise()
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        f"/api/v1/exercises/{data['exercise_id']}/complete",
        json={"score": 5, "total": 5},
        headers=auth_headers,
    )
    body = response.json()
    assert body["unit_progress"]["mini_test_unlocked"] is True
