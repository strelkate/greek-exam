from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.enums import CardStatusEnum
from app.models.user import User
from app.models.vocabulary import UserCardState, VocabularyCard
from app.schemas.vocabulary import (
    CardDue, DueCardsResponse, ReviewRequest, ReviewResponse, VocabStatsResponse,
)
from app.services.sm2_service import calculate_sm2
from app.services.xp_service import XP_CARD_KNOWN, award_xp

router = APIRouter(prefix="/api/v1/vocabulary", tags=["vocabulary"])


def _to_date(val) -> date:
    """Convert date or ISO string to date object (SQLite compat)."""
    if isinstance(val, date):
        return val
    return date.fromisoformat(str(val))


@router.get("/due", response_model=DueCardsResponse)
async def get_due_cards(
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    today = date.today()

    states = (await session.scalars(
        select(UserCardState).where(
            UserCardState.user_id == user.id,
            UserCardState.next_review_at <= today,
            UserCardState.status != CardStatusEnum.NEW,
        )
    )).all()

    cards = []
    for state in states:
        card = await session.get(VocabularyCard, state.card_id)
        if card:
            cards.append(CardDue(
                id=card.id,
                word_gr=card.word_gr,
                word_ru=card.word_ru,
                audio_path=card.audio_path,
                status=state.status,
                next_review_at=_to_date(state.next_review_at),
            ))

    return DueCardsResponse(due_count=len(cards), cards=cards)


@router.post("/cards/{card_id}/review", response_model=ReviewResponse)
async def review_card(
    card_id: int,
    body: ReviewRequest,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag

    state = await session.scalar(
        select(UserCardState).where(
            UserCardState.user_id == user.id,
            UserCardState.card_id == card_id,
        )
    )
    if not state:
        raise HTTPException(status_code=404, detail="Card not in user's vocabulary")

    sm2 = calculate_sm2(
        known=body.known,
        interval_days=state.interval_days,
        easiness_factor=state.easiness_factor,
        repetitions=state.repetitions,
    )

    state.interval_days = sm2["interval_days"]
    state.easiness_factor = sm2["easiness_factor"]
    state.repetitions = sm2["repetitions"]
    state.next_review_at = date.today() + timedelta(days=int(sm2["interval_days"]))
    state.last_reviewed_at = datetime.now()

    # Update status based on repetitions
    if sm2["repetitions"] >= 3:
        state.status = CardStatusEnum.LEARNED
    else:
        state.status = CardStatusEnum.LEARNING

    xp = XP_CARD_KNOWN if body.known else 0
    if xp > 0:
        await award_xp(session, user, xp, "card_known", ref_id=card_id)

    await session.commit()

    return ReviewResponse(
        card_id=card_id,
        new_status=state.status,
        next_review_at=_to_date(state.next_review_at),
        interval_days=state.interval_days,
        xp_earned=xp,
    )


@router.get("/stats", response_model=VocabStatsResponse)
async def get_vocab_stats(
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    today = date.today()

    total = await session.scalar(
        select(func.count(UserCardState.id)).where(UserCardState.user_id == user.id)
    ) or 0
    learned = await session.scalar(
        select(func.count(UserCardState.id)).where(
            UserCardState.user_id == user.id,
            UserCardState.status == CardStatusEnum.LEARNED,
        )
    ) or 0
    due = await session.scalar(
        select(func.count(UserCardState.id)).where(
            UserCardState.user_id == user.id,
            UserCardState.next_review_at <= today,
            UserCardState.status != CardStatusEnum.NEW,
        )
    ) or 0
    new = await session.scalar(
        select(func.count(UserCardState.id)).where(
            UserCardState.user_id == user.id,
            UserCardState.status == CardStatusEnum.NEW,
        )
    ) or 0

    return VocabStatsResponse(total_cards=total, learned_count=learned, due_today=due, new_count=new)
