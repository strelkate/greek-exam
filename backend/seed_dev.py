"""
Seed the dev SQLite database with curriculum units, exercises,
vocabulary cards and placement questions from pipeline/data/generated/.

Usage:
    uv run python seed_dev.py
"""
import asyncio
import json
import sys
from pathlib import Path

# Allow importing pipeline modules
PIPELINE_DIR = Path(__file__).parent.parent / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

from curriculum_data import UNITS  # noqa: E402 — pipeline module

DATA_DIR = PIPELINE_DIR / "data" / "generated"

# ── Bootstrap app so models register with Base ────────────────────────────────
import app.models  # noqa: F401
from app.database import Base, engine, patch_sqlite_types, _is_sqlite
from app.config import settings
from app.models.curriculum import CurriculumUnit
from app.models.exercise import Exercise, PlacementTestQuestion
from app.models.vocabulary import VocabularyCard
from app.models.enums import ExerciseTypeEnum, LevelEnum

EXERCISE_TYPE_MAP = {
    "true_false": ExerciseTypeEnum.TRUE_FALSE,
    "multiple_choice": ExerciseTypeEnum.MULTIPLE_CHOICE,
    "matching": ExerciseTypeEnum.MATCHING,
    "fill_blank": ExerciseTypeEnum.FILL_BLANK,
    "image_description": ExerciseTypeEnum.IMAGE_DESCRIPTION,
    "dialogue": ExerciseTypeEnum.DIALOGUE,
}

LEVEL_MAP = {
    "a1": LevelEnum.A1,
    "a2": LevelEnum.A2,
    "b1": LevelEnum.B1,
}


async def seed():
    if not _is_sqlite(settings.database_url):
        print("This script is for SQLite dev only. Use import_content.py for PostgreSQL.")
        return

    patch_sqlite_types(Base)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select

    async with AsyncSession(engine) as session:
        # ── 1. Units ──────────────────────────────────────────────────────────
        existing = (await session.execute(select(CurriculumUnit))).scalars().all()
        if existing:
            print(f"Already seeded: {len(existing)} units found, skipping.")
            return

        print("Seeding curriculum units...")
        unit_id_map: dict[tuple[str, int], int] = {}  # (level, order_index) → db id

        for u in UNITS:
            unit = CurriculumUnit(
                level=LEVEL_MAP[u["level"]],
                order_index=u["order_index"],
                title=u["title_ru"],
                description=u.get("competence", ""),
                is_published=True,
            )
            session.add(unit)
            await session.flush()
            unit_id_map[(u["level"], u["order_index"])] = unit.id

        # ── 2. Exercises from JSON files ──────────────────────────────────────
        print("Seeding exercises...")
        ex_count = 0
        for json_path in sorted(DATA_DIR.glob("unit_*_*.json")):
            parts = json_path.stem.split("_")  # unit_a1_01_true_false
            if len(parts) < 4:
                continue
            level = parts[1]
            order_index = int(parts[2])
            ex_type_str = "_".join(parts[3:])

            if ex_type_str not in EXERCISE_TYPE_MAP:
                continue
            unit_db_id = unit_id_map.get((level, order_index))
            if unit_db_id is None:
                continue

            items = json.loads(json_path.read_text())
            if isinstance(items, dict):
                items = [items]

            for i, item in enumerate(items):
                session.add(Exercise(
                    unit_id=unit_db_id,
                    type=EXERCISE_TYPE_MAP[ex_type_str],
                    order_index=i + 1,
                    content=item,
                    audio_paths=[],
                    is_published=True,
                ))
                ex_count += 1

        # ── 3. Vocabulary cards ───────────────────────────────────────────────
        print("Seeding vocabulary cards...")
        vocab_count = 0
        for u in UNITS:
            unit_db_id = unit_id_map.get((u["level"], u["order_index"]))
            if unit_db_id is None:
                continue
            for v in u.get("vocab", []):
                session.add(VocabularyCard(
                    unit_id=unit_db_id,
                    word_gr=v["word_gr"],
                    word_ru=v["word_ru"],
                    example_gr=v.get("example_gr"),
                    order_index=v["order_index"],
                ))
                vocab_count += 1

        # ── 4. Placement test questions ───────────────────────────────────────
        placement_path = DATA_DIR / "placement.json"
        pt_count = 0
        if placement_path.exists():
            print("Seeding placement test questions...")
            questions = json.loads(placement_path.read_text())
            if isinstance(questions, dict):
                questions = [questions]
            for i, q in enumerate(questions):
                ex_type_str = q.get("type", "multiple_choice")
                if ex_type_str not in EXERCISE_TYPE_MAP:
                    ex_type_str = "multiple_choice"
                session.add(PlacementTestQuestion(
                    type=EXERCISE_TYPE_MAP[ex_type_str],
                    content=q,
                    correct_answer=q.get("correct_answer", {}),
                    order_index=i + 1,
                    is_active=True,
                ))
                pt_count += 1

        await session.commit()
        print(f"Done: {len(UNITS)} units, {ex_count} exercises, "
              f"{vocab_count} vocab cards, {pt_count} placement questions.")


if __name__ == "__main__":
    asyncio.run(seed())
