import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.curriculum import CurriculumUnit
from app.models.enums import ExerciseTypeEnum, LevelEnum
from app.models.exercise import Exercise
from app.models.progress import UserProgress
from app.models.user import User
from app.models.vocabulary import VocabularyCard
from app.schemas.curriculum import (
    ExerciseMeta, LevelProgress, LevelsResponse,
    UnitDetailResponse, UnitSummary, UnitsResponse, VocabCardMeta,
)

router = APIRouter(prefix="/api/v1/curriculum", tags=["curriculum"])


@router.get("/levels", response_model=LevelsResponse)
async def get_levels(
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    levels_data = []

    for level in LevelEnum:
        total = await session.scalar(
            select(func.count()).where(
                CurriculumUnit.level == level,
                CurriculumUnit.is_published == True,
            )
        ) or 0

        completed = 0
        if total > 0:
            unit_ids_result = await session.scalars(
                select(CurriculumUnit.id).where(
                    CurriculumUnit.level == level,
                    CurriculumUnit.is_published == True,
                )
            )
            unit_ids = list(unit_ids_result.all())
            if unit_ids:
                completed = await session.scalar(
                    select(func.count()).where(
                        UserProgress.user_id == user.id,
                        UserProgress.unit_id.in_(unit_ids),
                        UserProgress.unit_completed == True,
                    )
                ) or 0

        pct = int(completed / total * 100) if total > 0 else 0
        levels_data.append(LevelProgress(
            level=level,
            total_units=total,
            completed_units=completed,
            progress_percent=pct,
        ))

    return LevelsResponse(levels=levels_data)


@router.get("/units", response_model=UnitsResponse)
async def get_units(
    level: LevelEnum,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    units = (await session.scalars(
        select(CurriculumUnit).where(
            CurriculumUnit.level == level,
            CurriculumUnit.is_published == True,
        ).order_by(CurriculumUnit.order_index)
    )).all()

    result = []
    for unit in units:
        total_exercises = await session.scalar(
            select(func.count()).where(
                Exercise.unit_id == unit.id,
                Exercise.is_published == True,
                Exercise.type != ExerciseTypeEnum.FLASHCARD,
            )
        ) or 0

        progress = await session.scalar(
            select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.unit_id == unit.id,
            )
        )
        result.append(UnitSummary(
            id=unit.id,
            title=unit.title,
            order_index=unit.order_index,
            exercises_total=total_exercises,
            exercises_completed=progress.exercises_completed if progress else 0,
            mini_test_passed=progress.mini_test_passed if progress else False,
            unit_completed=progress.unit_completed if progress else False,
        ))

    return UnitsResponse(units=result)


@router.get("/units/{unit_id}", response_model=UnitDetailResponse)
async def get_unit_detail(
    unit_id: int,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    unit = await session.get(CurriculumUnit, unit_id)
    if not unit or not unit.is_published:
        raise HTTPException(status_code=404, detail="Unit not found")

    exercises_rows = (await session.scalars(
        select(Exercise).where(
            Exercise.unit_id == unit_id,
            Exercise.is_published == True,
        ).order_by(Exercise.order_index)
    )).all()

    progress = await session.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user.id,
            UserProgress.unit_id == unit_id,
        )
    )
    # completed_exercise_ids is stored as Text in SQLite — handle both list and str
    completed_ids_raw = progress.completed_exercise_ids if progress else []
    if isinstance(completed_ids_raw, str):
        try:
            completed_ids = json.loads(completed_ids_raw) if completed_ids_raw else []
        except json.JSONDecodeError:
            completed_ids = []
    else:
        completed_ids = completed_ids_raw or []

    exercises = [
        ExerciseMeta(
            id=ex.id,
            type=ex.type,
            order_index=ex.order_index,
            audio_paths=ex.audio_paths or [],
            completed=ex.id in completed_ids,
        )
        for ex in exercises_rows
    ]

    vocab_rows = (await session.scalars(
        select(VocabularyCard).where(
            VocabularyCard.unit_id == unit_id,
        ).order_by(VocabularyCard.order_index)
    )).all()

    vocab = [
        VocabCardMeta(
            id=card.id,
            word_gr=card.word_gr,
            word_ru=card.word_ru,
            audio_path=card.audio_path,
        )
        for card in vocab_rows
    ]

    return UnitDetailResponse(
        id=unit.id,
        title=unit.title,
        level=unit.level,
        exercises=exercises,
        vocabulary_cards=vocab,
    )
