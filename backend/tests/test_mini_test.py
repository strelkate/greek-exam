# backend/tests/test_mini_test.py
import pytest
from tests.conftest import TestSessionFactory, make_fake_init_data
from app.models.curriculum import CurriculumUnit
from app.models.exercise import Exercise
from app.models.progress import UserProgress
from app.models.enums import LevelEnum, ExerciseTypeEnum


@pytest.fixture
def auth_headers():
    return {"X-Telegram-Init-Data": make_fake_init_data()}


async def setup_unit_with_completed_exercises():
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(level=LevelEnum.A1, title="U1", order_index=1, is_published=True)
        session.add(unit)
        await session.flush()
        exercises = []
        for i in range(3):
            ex = Exercise(
                unit_id=unit.id, type=ExerciseTypeEnum.MULTIPLE_CHOICE,
                order_index=i, content={"question": f"Q{i}", "options": [], "correct_id": "a"},
                is_published=True, audio_paths=[],
            )
            session.add(ex)
            exercises.append(ex)
        await session.flush()
        await session.commit()
        return unit.id, [e.id for e in exercises]


async def test_mini_test_requires_all_exercises(client, auth_headers):
    unit_id, ex_ids = await setup_unit_with_completed_exercises()
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get(f"/api/v1/units/{unit_id}/mini-test", headers=auth_headers)
    assert response.status_code == 403


async def test_mini_test_available_after_exercises(client, auth_headers):
    unit_id, ex_ids = await setup_unit_with_completed_exercises()
    await client.post("/api/v1/auth/session", headers=auth_headers)

    # Complete all exercises
    for ex_id in ex_ids:
        await client.post(
            f"/api/v1/exercises/{ex_id}/complete",
            json={"score": 3, "total": 3},
            headers=auth_headers,
        )

    response = await client.get(f"/api/v1/units/{unit_id}/mini-test", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) <= 5


async def test_mini_test_complete(client, auth_headers):
    unit_id, ex_ids = await setup_unit_with_completed_exercises()
    await client.post("/api/v1/auth/session", headers=auth_headers)

    for ex_id in ex_ids:
        await client.post(
            f"/api/v1/exercises/{ex_id}/complete",
            json={"score": 3, "total": 3},
            headers=auth_headers,
        )

    response = await client.post(
        f"/api/v1/units/{unit_id}/mini-test/complete",
        json={"score": 4, "total": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["unit_completed"] is True
    assert data["xp_earned"] == 25


async def test_mini_test_complete_idempotent(client, auth_headers):
    unit_id, ex_ids = await setup_unit_with_completed_exercises()
    await client.post("/api/v1/auth/session", headers=auth_headers)

    for ex_id in ex_ids:
        await client.post(
            f"/api/v1/exercises/{ex_id}/complete",
            json={"score": 3, "total": 3},
            headers=auth_headers,
        )

    await client.post(
        f"/api/v1/units/{unit_id}/mini-test/complete",
        json={"score": 4, "total": 5},
        headers=auth_headers,
    )
    response = await client.post(
        f"/api/v1/units/{unit_id}/mini-test/complete",
        json={"score": 4, "total": 5},
        headers=auth_headers,
    )
    assert response.status_code == 409


async def test_mini_test_flashcard_exercises_not_counted_for_gate(client, auth_headers):
    """Completing only flashcard exercises should NOT unlock the mini-test."""
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(level=LevelEnum.A1, title="UFlash", order_index=2, is_published=True)
        session.add(unit)
        await session.flush()
        # 1 real exercise + 1 flashcard
        real_ex = Exercise(
            unit_id=unit.id, type=ExerciseTypeEnum.MULTIPLE_CHOICE,
            order_index=0, content={"q": "Q0", "options": [], "correct_id": "a"},
            is_published=True, audio_paths=[],
        )
        flash_ex = Exercise(
            unit_id=unit.id, type=ExerciseTypeEnum.FLASHCARD,
            order_index=1, content={"word": "γεια"},
            is_published=True, audio_paths=[],
        )
        session.add(real_ex)
        session.add(flash_ex)
        await session.commit()
        unit_id = unit.id
        real_id = real_ex.id
        flash_id = flash_ex.id

    await client.post("/api/v1/auth/session", headers=auth_headers)

    # Complete only the flashcard — mini-test should stay locked
    await client.post(
        f"/api/v1/exercises/{flash_id}/complete",
        json={"score": 1, "total": 1},
        headers=auth_headers,
    )
    response = await client.get(f"/api/v1/units/{unit_id}/mini-test", headers=auth_headers)
    assert response.status_code == 403

    # Complete the real exercise — now mini-test unlocks
    await client.post(
        f"/api/v1/exercises/{real_id}/complete",
        json={"score": 1, "total": 1},
        headers=auth_headers,
    )
    response = await client.get(f"/api/v1/units/{unit_id}/mini-test", headers=auth_headers)
    assert response.status_code == 200
