# backend/app/routers/mini_test.py
import json
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.enums import CardStatusEnum, ExerciseTypeEnum
from app.models.exercise import Exercise
from app.models.progress import UserProgress
from app.models.user import User
from app.models.vocabulary import UserCardState, VocabularyCard
from app.services.xp_service import XP_MINI_TEST, award_xp

router = APIRouter(prefix="/api/v1/units", tags=["mini-test"])

MINI_TEST_TYPES = {ExerciseTypeEnum.TRUE_FALSE, ExerciseTypeEnum.MULTIPLE_CHOICE, ExerciseTypeEnum.FILL_BLANK}
MINI_TEST_QUESTION_COUNT = 5


class MiniTestQuestion(BaseModel):
    id: int
    type: ExerciseTypeEnum
    content: dict


class MiniTestQuestionsResponse(BaseModel):
    questions: list[MiniTestQuestion]


class MiniTestCompleteRequest(BaseModel):
    score: int
    total: int


class MiniTestCompleteResponse(BaseModel):
    unit_completed: bool
    xp_earned: int
    cards_added_to_vocab: int


async def _check_all_exercises_done(user_id: int, unit_id: int, session: AsyncSession) -> bool:
    total = await session.scalar(
        select(func.count(Exercise.id)).where(
            Exercise.unit_id == unit_id,
            Exercise.is_published == True,
            Exercise.type != ExerciseTypeEnum.FLASHCARD,
        )
    ) or 0
    if total == 0:
        return True
    progress = await session.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user_id, UserProgress.unit_id == unit_id
        )
    )
    completed_ids = progress.completed_exercise_ids or [] if progress else []
    # completed_exercise_ids may be stored as JSON string in SQLite
    if isinstance(completed_ids, str):
        completed_ids = json.loads(completed_ids)
    completed = len(completed_ids)
    return completed >= total


@router.get("/{unit_id}/mini-test", response_model=MiniTestQuestionsResponse)
async def get_mini_test(
    unit_id: int,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    if not await _check_all_exercises_done(user.id, unit_id, session):
        raise HTTPException(status_code=403, detail="Complete all exercises first")

    exercises = (await session.scalars(
        select(Exercise).where(
            Exercise.unit_id == unit_id,
            Exercise.is_published == True,
            Exercise.type.in_(MINI_TEST_TYPES),
        )
    )).all()

    selected = random.sample(list(exercises), min(MINI_TEST_QUESTION_COUNT, len(exercises)))

    questions = []
    for ex in selected:
        content = ex.content
        if isinstance(content, str):
            content = json.loads(content)
        questions.append(MiniTestQuestion(id=ex.id, type=ex.type, content=content))

    return MiniTestQuestionsResponse(questions=questions)


@router.post("/{unit_id}/mini-test/complete", response_model=MiniTestCompleteResponse)
async def complete_mini_test(
    unit_id: int,
    body: MiniTestCompleteRequest,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    if not await _check_all_exercises_done(user.id, unit_id, session):
        raise HTTPException(status_code=403, detail="Complete all exercises first")

    progress = await session.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user.id, UserProgress.unit_id == unit_id
        )
    )
    if progress and progress.mini_test_passed:
        raise HTTPException(status_code=409, detail="Mini-test already passed")

    if not progress:
        progress = UserProgress(user_id=user.id, unit_id=unit_id)
        session.add(progress)

    progress.mini_test_passed = True
    progress.mini_test_score = body.score
    progress.unit_completed = True

    # Add vocabulary cards to user's queue (status LEARNING)
    cards_added = 0
    if not progress.cards_added_to_vocab:
        vocab_cards = (await session.scalars(
            select(VocabularyCard).where(VocabularyCard.unit_id == unit_id)
        )).all()
        for card in vocab_cards:
            existing = await session.scalar(
                select(UserCardState).where(
                    UserCardState.user_id == user.id, UserCardState.card_id == card.id
                )
            )
            if not existing:
                state = UserCardState(
                    user_id=user.id, card_id=card.id, status=CardStatusEnum.LEARNING
                )
                session.add(state)
                cards_added += 1
        progress.cards_added_to_vocab = True

    await award_xp(session, user, XP_MINI_TEST, "mini_test", ref_id=unit_id)
    await session.commit()

    return MiniTestCompleteResponse(
        unit_completed=True,
        xp_earned=XP_MINI_TEST,
        cards_added_to_vocab=cards_added,
    )
