import pytest
from datetime import date, timedelta
from tests.conftest import TestSessionFactory, make_fake_init_data
from app.models.curriculum import CurriculumUnit
from app.models.vocabulary import VocabularyCard, UserCardState
from app.models.enums import LevelEnum, CardStatusEnum


@pytest.fixture
def auth_headers():
    return {"X-Telegram-Init-Data": make_fake_init_data()}


async def create_vocab_card(word_gr: str = "γεια", word_ru: str = "привет") -> dict:
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(level=LevelEnum.A1, title="U", order_index=1, is_published=True)
        session.add(unit)
        await session.flush()
        card = VocabularyCard(
            unit_id=unit.id, word_gr=word_gr, word_ru=word_ru, order_index=1
        )
        session.add(card)
        await session.commit()
        return {"card_id": card.id, "unit_id": unit.id}


async def add_card_state(user_id: int, card_id: int, status: CardStatusEnum = CardStatusEnum.LEARNING, due_today: bool = True):
    async with TestSessionFactory() as session:
        state = UserCardState(
            user_id=user_id,
            card_id=card_id,
            status=status,
            next_review_at=date.today() if due_today else date.today() + timedelta(days=5),
        )
        session.add(state)
        await session.commit()


async def test_vocab_due_empty(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/vocabulary/due", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["due_count"] == 0
    assert data["cards"] == []


async def test_vocab_due_returns_cards_due_today(client, auth_headers):
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"], status=CardStatusEnum.LEARNING, due_today=True)

    response = await client.get("/api/v1/vocabulary/due", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["due_count"] == 1
    assert data["cards"][0]["id"] == card_data["card_id"]
    assert data["cards"][0]["word_gr"] == "γεια"


async def test_vocab_due_excludes_future_cards(client, auth_headers):
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"], status=CardStatusEnum.LEARNING, due_today=False)

    response = await client.get("/api/v1/vocabulary/due", headers=auth_headers)
    assert response.json()["due_count"] == 0


async def test_vocab_due_excludes_new_cards(client, auth_headers):
    """NEW status cards are not in the due queue (they are added via mini-test unlock)."""
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"], status=CardStatusEnum.NEW, due_today=True)

    response = await client.get("/api/v1/vocabulary/due", headers=auth_headers)
    assert response.json()["due_count"] == 0


async def test_card_review_known(client, auth_headers):
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"])

    response = await client.post(
        f"/api/v1/vocabulary/cards/{card_data['card_id']}/review",
        json={"known": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["card_id"] == card_data["card_id"]
    assert data["xp_earned"] == 2
    assert data["new_status"] in ("learning", "learned")
    assert data["interval_days"] > 0


async def test_card_review_unknown(client, auth_headers):
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"])

    response = await client.post(
        f"/api/v1/vocabulary/cards/{card_data['card_id']}/review",
        json={"known": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["xp_earned"] == 0
    assert data["interval_days"] == 1.0  # reset


async def test_card_review_not_found(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.post(
        "/api/v1/vocabulary/cards/99999/review",
        json={"known": True},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_vocab_stats(client, auth_headers):
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"], status=CardStatusEnum.LEARNING, due_today=True)

    response = await client.get("/api/v1/vocabulary/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_cards"] == 1
    assert data["due_today"] == 1
    assert data["learned_count"] == 0
    assert data["new_count"] == 0


async def test_vocab_stats_multi_card(client, auth_headers):
    """Stats counts are correct with multiple cards in different states."""
    card1 = await create_vocab_card("word1", "слово1")
    card2 = await create_vocab_card("word2", "слово2")
    card3 = await create_vocab_card("word3", "слово3")
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card1["card_id"], status=CardStatusEnum.LEARNING, due_today=True)
    await add_card_state(user_id, card2["card_id"], status=CardStatusEnum.LEARNED, due_today=False)
    await add_card_state(user_id, card3["card_id"], status=CardStatusEnum.NEW, due_today=True)

    response = await client.get("/api/v1/vocabulary/stats", headers=auth_headers)
    data = response.json()
    assert data["total_cards"] == 3
    assert data["learned_count"] == 1
    assert data["due_today"] == 1  # only LEARNING card due (NEW excluded)
    assert data["new_count"] == 1


async def test_card_review_learned_wrong_reverts_to_learning(client, auth_headers):
    """A LEARNED card answered wrong should revert to LEARNING status."""
    card_data = await create_vocab_card()
    session_resp = await client.post("/api/v1/auth/session", headers=auth_headers)
    user_id = session_resp.json()["user_id"]
    await add_card_state(user_id, card_data["card_id"], status=CardStatusEnum.LEARNED)

    response = await client.post(
        f"/api/v1/vocabulary/cards/{card_data['card_id']}/review",
        json={"known": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "learning"
    assert response.json()["xp_earned"] == 0
