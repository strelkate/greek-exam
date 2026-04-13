import pytest
from tests.conftest import TestSessionFactory, make_fake_init_data
from app.models.curriculum import CurriculumUnit
from app.models.exercise import Exercise
from app.models.enums import LevelEnum, ExerciseTypeEnum


async def create_unit(level: LevelEnum, order: int, title: str = None, published: bool = True) -> CurriculumUnit:
    async with TestSessionFactory() as session:
        unit = CurriculumUnit(
            level=level,
            title=title or f"Unit {order}",
            order_index=order,
            is_published=published,
        )
        session.add(unit)
        await session.commit()
        await session.refresh(unit)
        # Return a plain dict to avoid detached instance issues
        return {"id": unit.id, "level": unit.level, "title": unit.title, "order_index": unit.order_index}


@pytest.fixture
def auth_headers():
    return {"X-Telegram-Init-Data": make_fake_init_data()}


async def test_get_levels_returns_all_three(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/curriculum/levels", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "levels" in data
    level_names = [l["level"] for l in data["levels"]]
    assert "A1" in level_names
    assert "A2" in level_names
    assert "B1" in level_names


async def test_get_levels_counts_published_units(client, auth_headers):
    await create_unit(LevelEnum.A1, 1)
    await create_unit(LevelEnum.A1, 2)
    await create_unit(LevelEnum.A2, 1)
    await create_unit(LevelEnum.A1, 3, published=False)  # unpublished, not counted

    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/curriculum/levels", headers=auth_headers)
    assert response.status_code == 200
    levels = {l["level"]: l for l in response.json()["levels"]}
    assert levels["A1"]["total_units"] == 2
    assert levels["A2"]["total_units"] == 1
    assert levels["B1"]["total_units"] == 0


async def test_get_units_by_level(client, auth_headers):
    await create_unit(LevelEnum.A1, 1)
    await create_unit(LevelEnum.A1, 2)
    await create_unit(LevelEnum.A2, 1)
    await create_unit(LevelEnum.A1, 3, published=False)

    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/curriculum/units?level=A1", headers=auth_headers)
    assert response.status_code == 200
    units = response.json()["units"]
    assert len(units) == 2  # only published
    assert all(u["order_index"] in [1, 2] for u in units)


async def test_get_unit_detail_with_exercises(client, auth_headers):
    unit_data = await create_unit(LevelEnum.A1, 1)
    unit_id = unit_data["id"]

    # Add an exercise
    async with TestSessionFactory() as session:
        ex = Exercise(
            unit_id=unit_id,
            type=ExerciseTypeEnum.MULTIPLE_CHOICE,
            order_index=1,
            content={"question": "Τι είναι;", "options": [], "correct_id": "a"},
            audio_paths=[],
            is_published=True,
        )
        session.add(ex)
        await session.commit()

    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get(f"/api/v1/curriculum/units/{unit_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == unit_id
    assert data["level"] == "A1"
    assert len(data["exercises"]) == 1
    assert data["exercises"][0]["type"] == "multiple_choice"
    assert "vocabulary_cards" in data


async def test_get_unit_not_found(client, auth_headers):
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get("/api/v1/curriculum/units/99999", headers=auth_headers)
    assert response.status_code == 404


async def test_get_unpublished_unit_returns_404(client, auth_headers):
    unit_data = await create_unit(LevelEnum.A1, 1, published=False)
    await client.post("/api/v1/auth/session", headers=auth_headers)
    response = await client.get(f"/api/v1/curriculum/units/{unit_data['id']}", headers=auth_headers)
    assert response.status_code == 404
