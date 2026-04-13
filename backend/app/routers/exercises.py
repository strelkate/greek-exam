import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.enums import ExerciseTypeEnum
from app.models.exercise import Exercise
from app.models.progress import UserProgress
from app.models.user import User
from app.schemas.exercises import (
    CompleteExerciseRequest, CompleteExerciseResponse,
    ExerciseResponse, UnitProgressInline,
)
from app.services.streak_service import calculate_streak
from app.services.xp_service import XP_EXERCISE, XP_STREAK_BONUS, award_xp

router = APIRouter(prefix="/api/v1/exercises", tags=["exercises"])


def _parse_ids(raw) -> list[int]:
    """Parse completed_exercise_ids — handles list or JSON string (SQLite compat)."""
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            return json.loads(raw) if raw else []
        except json.JSONDecodeError:
            return []
    return list(raw)


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: int,
    _: tuple = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    ex = await session.get(Exercise, exercise_id)
    if not ex or not ex.is_published:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # audio_paths are strings, not ints — but _parse_ids works for any JSON array
    if ex.audio_paths and isinstance(ex.audio_paths, list):
        audio_paths = ex.audio_paths
    elif ex.audio_paths and isinstance(ex.audio_paths, str):
        try:
            audio_paths = json.loads(ex.audio_paths)
        except json.JSONDecodeError:
            audio_paths = []
    else:
        audio_paths = []

    return ExerciseResponse(
        id=ex.id,
        unit_id=ex.unit_id,
        type=ex.type,
        content=ex.content if isinstance(ex.content, dict) else json.loads(ex.content),
        audio_paths=audio_paths,
    )


@router.post("/{exercise_id}/complete", response_model=CompleteExerciseResponse)
async def complete_exercise(
    exercise_id: int,
    body: CompleteExerciseRequest,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    ex = await session.get(Exercise, exercise_id)
    if not ex or not ex.is_published:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # score and total are accepted for future analytics/statistics; not currently stored
    if body.total > 0 and body.score > body.total:
        raise HTTPException(status_code=422, detail="score cannot exceed total")

    # Load or create progress
    # NOTE: concurrent requests for the same exercise can bypass the idempotency check below
    # because there is no SELECT FOR UPDATE (SQLite incompatible). A proper fix requires
    # a separate UserExerciseCompletion table with UNIQUE(user_id, exercise_id) constraint.
    progress = await session.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user.id,
            UserProgress.unit_id == ex.unit_id,
        )
    )

    # Idempotency check
    completed_ids = _parse_ids(progress.completed_exercise_ids if progress else None)
    if exercise_id in completed_ids:
        raise HTTPException(status_code=409, detail="Exercise already completed")

    if not progress:
        progress = UserProgress(user_id=user.id, unit_id=ex.unit_id, completed_exercise_ids=[])
        session.add(progress)
        await session.flush()  # get progress.id

    # Update completed list (stores all exercise IDs including flashcards)
    completed_ids.append(exercise_id)
    progress.completed_exercise_ids = completed_ids

    # Streak
    streak_result = calculate_streak(
        last_active_date=user.last_active_date,
        current_streak=user.streak_days,
        today=date.today(),
    )
    xp_breakdown: dict[str, int] = {"exercise_complete": XP_EXERCISE}
    xp_total = XP_EXERCISE

    # Always update last_active_date when completing an exercise
    user.last_active_date = date.today()

    if streak_result["updated"]:
        user.streak_days = streak_result["streak_days"]
        if streak_result["streak_days"] > 1:
            xp_breakdown["streak_bonus"] = XP_STREAK_BONUS
            xp_total += XP_STREAK_BONUS

    await award_xp(session, user, xp_total, "exercise_complete", ref_id=exercise_id)

    # Fetch all non-flashcard published exercise IDs for this unit
    non_flashcard_ids_result = await session.scalars(
        select(Exercise.id).where(
            Exercise.unit_id == ex.unit_id,
            Exercise.is_published == True,
            Exercise.type != ExerciseTypeEnum.FLASHCARD,
        )
    )
    non_flashcard_ids = set(non_flashcard_ids_result.all())
    total_in_unit = len(non_flashcard_ids)
    completed_non_flashcard = len(set(completed_ids) & non_flashcard_ids)
    mini_test_unlocked = completed_non_flashcard >= total_in_unit
    # exercises_completed counts only non-flashcard completions (consistent with exercises_total)
    progress.exercises_completed = completed_non_flashcard

    await session.commit()

    return CompleteExerciseResponse(
        xp_earned=xp_total,
        xp_breakdown=xp_breakdown,
        streak_days=user.streak_days,
        streak_updated=streak_result["updated"],
        unit_progress=UnitProgressInline(
            exercises_completed=completed_non_flashcard,
            exercises_total=total_in_unit,
            mini_test_unlocked=mini_test_unlocked,
        ),
    )
