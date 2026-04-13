# backend/app/routers/placement_test.py
import json
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.enums import ExerciseTypeEnum, PlacementStatusEnum
from app.models.exercise import PlacementTestQuestion
from app.models.user import User

router = APIRouter(prefix="/api/v1/placement-test", tags=["placement-test"])

PASS_THRESHOLD = 0.8
QUESTION_COUNT = (15, 20)


class PlacementQuestion(BaseModel):
    id: int
    type: ExerciseTypeEnum
    content: dict


class PlacementQuestionsResponse(BaseModel):
    questions: list[PlacementQuestion]


class PlacementCompleteRequest(BaseModel):
    score: int
    total: int
    skipped: bool = False


class PlacementCompleteResponse(BaseModel):
    placement_status: PlacementStatusEnum
    a1_skipped: bool
    message: str


@router.get("/questions", response_model=PlacementQuestionsResponse)
async def get_placement_questions(
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    if user.placement_status != PlacementStatusEnum.PENDING:
        raise HTTPException(status_code=403, detail="Placement test already completed")

    all_q = (await session.scalars(
        select(PlacementTestQuestion).where(PlacementTestQuestion.is_active == True)
    )).all()

    count = min(QUESTION_COUNT[1], max(QUESTION_COUNT[0], len(all_q)))
    selected = random.sample(list(all_q), min(count, len(all_q)))

    questions = []
    for q in selected:
        content = q.content
        if isinstance(content, str):
            content = json.loads(content)
        questions.append(PlacementQuestion(id=q.id, type=q.type, content=content))

    return PlacementQuestionsResponse(questions=questions)


@router.post("/complete", response_model=PlacementCompleteResponse)
async def complete_placement_test(
    body: PlacementCompleteRequest,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    if user.placement_status != PlacementStatusEnum.PENDING:
        raise HTTPException(status_code=409, detail="Placement test already completed")

    if not body.skipped and body.total <= 0:
        raise HTTPException(status_code=422, detail="total must be > 0 when not skipping")

    if body.skipped:
        user.placement_status = PlacementStatusEnum.SKIPPED
        user.a1_skipped = False
        msg = "Начинаете с A1."
    elif body.score / body.total >= PASS_THRESHOLD:
        user.placement_status = PlacementStatusEnum.PASSED
        user.a1_skipped = True
        msg = "Поздравляем! A1 пропущен, начинаете с A2."
    else:
        user.placement_status = PlacementStatusEnum.FAILED
        user.a1_skipped = False
        msg = "Начинаете с A1."

    await session.commit()
    return PlacementCompleteResponse(
        placement_status=user.placement_status,
        a1_skipped=user.a1_skipped,
        message=msg,
    )
