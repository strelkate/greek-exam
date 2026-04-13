# backend/tests/test_sync.py
from datetime import datetime, timezone
import pytest
from tests.conftest import TestSessionFactory, make_fake_init_data
from app.models.curriculum import CurriculumUnit
from app.models.exercise import Exercise
from app.models.vocabulary import VocabularyCard, UserCardState
from app.models.enums import LevelEnum, ExerciseTypeEnum, CardStatusEnum


@pytest.fixture
def auth_headers():
    return {"X-Telegram-Init-Data": make_fake_init_data()}


async def setup_sync_data():
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(level=LevelEnum.A1, title="U", order_index=1, is_published=True)
        session.add(unit)
        await session.flush()
        ex = Exercise(
            unit_id=unit.id, type=ExerciseTypeEnum.TRUE_FALSE,
            order_index=1, content={}, audio_paths=[], is_published=True,
        )
        card = VocabularyCard(unit_id=unit.id, word_gr="γεια", word_ru="привет", order_index=1)
        session.add(ex)
        session.add(card)
        await session.commit()
        return ex.id, card.id


async def setup_card_state(user_id: int, card_id: int):
    async with TestSessionFactory() as session:
        state = UserCardState(user_id=user_id, card_id=card_id, status=CardStatusEnum.LEARNING)
        session.add(state)
        await session.commit()


async def test_sync_exercise_complete(client, auth_headers):
    ex_id, card_id = await setup_sync_data()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]

    response = await client.post(
        "/api/v1/sync/progress",
        json={
            "events": [
                {
                    "type": "exercise_complete",
                    "exercise_id": ex_id,
                    "score": 3,
                    "total": 3,
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["processed"] == 1
    assert data["skipped"] == 0
    assert data["xp_total_earned"] >= 10


async def test_sync_duplicate_skipped(client, auth_headers):
    ex_id, card_id = await setup_sync_data()
    await client.post("/api/v1/auth/session", headers=auth_headers)

    event = {
        "type": "exercise_complete",
        "exercise_id": ex_id,
        "score": 3,
        "total": 3,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    await client.post("/api/v1/sync/progress", json={"events": [event]}, headers=auth_headers)
    response = await client.post("/api/v1/sync/progress", json={"events": [event]}, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["skipped"] == 1
    assert data["xp_total_earned"] == 0


async def test_sync_card_review(client, auth_headers):
    ex_id, card_id = await setup_sync_data()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await setup_card_state(user_id, card_id)

    response = await client.post(
        "/api/v1/sync/progress",
        json={
            "events": [
                {
                    "type": "card_review",
                    "card_id": card_id,
                    "known": True,
                    "occurred_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["xp_total_earned"] == 2
