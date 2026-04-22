"""
Seed the database with curriculum units, exercises and vocabulary
cards from backend/seed_data/.

Works with both SQLite (dev) and PostgreSQL (production). On SQLite
it creates the schema from models; on PostgreSQL it expects Alembic
migrations to have run already.

Idempotent — if any curriculum units already exist, it exits without
doing anything.

Usage:
    uv run python seed_dev.py
"""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

SEED_DIR = Path(__file__).parent / "seed_data"
sys.path.insert(0, str(SEED_DIR))


def audio_path_for_text(text: str) -> str:
    """Public URL path for gTTS MP3, keyed by sha256(text)[:12].

    Files are baked into frontend/public/audio/ at deploy time.
    """
    filename = hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"
    return f"/audio/{filename}"


def _extract_texts_for_exercise(ex_type: str, content: dict) -> list[str]:
    """Return the list of texts that need audio, per exercise type."""
    if ex_type == "true_false":
        return [content["text"]]
    if ex_type == "matching":
        return [p["left"] for p in content.get("pairs", [])]
    if ex_type == "multiple_choice":
        return [content["question"].replace("___", "").strip()]
    if ex_type == "fill_blank":
        return [content["text_template"].replace("___", "").strip()]
    if ex_type == "image_description":
        return [content["description_text"]]
    if ex_type == "dialogue":
        return [
            line["text"].replace("___", "").strip()
            for line in content.get("dialogue_lines", [])
        ]
    return []

from curriculum_data import UNITS  # noqa: E402

DATA_DIR = SEED_DIR / "exercises"

# ── Bootstrap app so models register with Base ────────────────────────────────
import app.models  # noqa: F401
from app.database import Base, engine, patch_sqlite_types, _is_sqlite
from app.config import settings
from app.models.curriculum import CurriculumUnit
from app.models.exercise import Exercise
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


async def _backfill_audio(session) -> None:
    """Populate audio_paths/audio_path for rows seeded before the audio hookup.

    Idempotent: skips rows that already have audio. Writes deterministic
    /audio/<sha256-12>.mp3 paths matching files in frontend/public/audio/.
    """
    from sqlalchemy import select
    from sqlalchemy.orm.attributes import flag_modified

    ex_type_to_str = {v: k for k, v in EXERCISE_TYPE_MAP.items()}
    exercises = (await session.execute(select(Exercise))).scalars().all()
    ex_updated = 0
    for ex in exercises:
        if ex.audio_paths:
            continue
        ex_type_str = ex_type_to_str.get(ex.type)
        if ex_type_str is None:
            continue
        content = ex.content if isinstance(ex.content, dict) else {}
        texts = _extract_texts_for_exercise(ex_type_str, content)
        audio_paths = [audio_path_for_text(t) for t in texts if t]
        if not audio_paths:
            continue
        if ex_type_str == "dialogue":
            for j, line in enumerate(content.get("dialogue_lines", [])):
                if j < len(audio_paths):
                    line["audio_path"] = audio_paths[j]
            ex.content = content
            flag_modified(ex, "content")
        ex.audio_paths = audio_paths
        ex_updated += 1

    cards = (await session.execute(select(VocabularyCard))).scalars().all()
    vocab_updated = 0
    for card in cards:
        if card.audio_path:
            continue
        card.audio_path = audio_path_for_text(card.word_gr)
        vocab_updated += 1

    await session.commit()
    print(f"Backfill: {ex_updated} exercises, {vocab_updated} vocab cards updated.")


async def seed():
    if _is_sqlite(settings.database_url):
        patch_sqlite_types(Base)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    # On PostgreSQL the schema is managed by Alembic migrations.

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select

    async with AsyncSession(engine) as session:
        # ── 1. Units ──────────────────────────────────────────────────────────
        existing = (await session.execute(select(CurriculumUnit))).scalars().all()
        if existing:
            print(f"Already seeded: {len(existing)} units found, running audio backfill.")
            await _backfill_audio(session)
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
                texts = _extract_texts_for_exercise(ex_type_str, item)
                audio_paths = [audio_path_for_text(t) for t in texts if t]
                if ex_type_str == "dialogue":
                    for j, line in enumerate(item.get("dialogue_lines", [])):
                        if j < len(audio_paths):
                            line["audio_path"] = audio_paths[j]
                session.add(Exercise(
                    unit_id=unit_db_id,
                    type=EXERCISE_TYPE_MAP[ex_type_str],
                    order_index=i + 1,
                    content=item,
                    audio_paths=audio_paths,
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
                    audio_path=audio_path_for_text(v["word_gr"]),
                ))
                vocab_count += 1

        await session.commit()
        print(f"Done: {len(UNITS)} units, {ex_count} exercises, "
              f"{vocab_count} vocab cards.")


if __name__ == "__main__":
    asyncio.run(seed())
