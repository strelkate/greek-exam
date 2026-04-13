# backend/app/routers/sync.py
from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.enums import CardStatusEnum
from app.models.exercise import Exercise
from app.models.progress import UserProgress
from app.models.user import User
from app.models.vocabulary import UserCardState
from app.routers.exercises import _parse_ids
from app.schemas.sync import SyncRequest, SyncResponse
from app.services.sm2_service import calculate_sm2
from app.services.streak_service import calculate_streak
from app.services.xp_service import XP_CARD_KNOWN, XP_EXERCISE, XP_STREAK_BONUS, award_xp

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


@router.post("/progress", response_model=SyncResponse)
async def sync_progress(
    body: SyncRequest,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    processed = 0
    skipped = 0
    total_xp = 0
    conflicts: list[str] = []

    # Process events in chronological order
    events = sorted(body.events, key=lambda e: e.occurred_at)

    for event in events:
        if event.type == "exercise_complete":
            ex = await session.get(Exercise, event.exercise_id)
            if not ex or not ex.is_published:
                skipped += 1
                continue

            progress = await session.scalar(
                select(UserProgress).where(
                    UserProgress.user_id == user.id, UserProgress.unit_id == ex.unit_id
                )
            )
            completed_ids = _parse_ids(progress.completed_exercise_ids if progress else None)
            if event.exercise_id in completed_ids:
                skipped += 1
                continue

            if not progress:
                progress = UserProgress(user_id=user.id, unit_id=ex.unit_id)
                session.add(progress)

            completed_ids.append(event.exercise_id)
            progress.completed_exercise_ids = completed_ids
            progress.exercises_completed = len(completed_ids)

            streak = calculate_streak(user.last_active_date, user.streak_days,
                                      today=event.occurred_at.date())
            xp = XP_EXERCISE
            user.last_active_date = event.occurred_at.date()
            if streak["updated"]:
                user.streak_days = streak["streak_days"]
                if streak["streak_days"] > 1:
                    xp += XP_STREAK_BONUS

            await award_xp(session, user, xp, "exercise_complete", ref_id=event.exercise_id)
            total_xp += xp
            processed += 1

        elif event.type == "card_review":
            state = await session.scalar(
                select(UserCardState).where(
                    UserCardState.user_id == user.id, UserCardState.card_id == event.card_id
                )
            )
            if not state:
                skipped += 1
                continue

            sm2 = calculate_sm2(
                known=event.known,
                interval_days=state.interval_days,
                easiness_factor=state.easiness_factor,
                repetitions=state.repetitions,
            )
            state.interval_days = sm2["interval_days"]
            state.easiness_factor = sm2["easiness_factor"]
            state.repetitions = sm2["repetitions"]
            state.next_review_at = event.occurred_at.date() + timedelta(days=int(sm2["interval_days"]))

            if sm2["repetitions"] >= 3:
                state.status = CardStatusEnum.LEARNED
            else:
                state.status = CardStatusEnum.LEARNING

            xp = XP_CARD_KNOWN if event.known else 0
            if xp > 0:
                await award_xp(session, user, xp, "card_known", ref_id=event.card_id)
                total_xp += xp
            processed += 1

        elif event.type == "mini_test_complete":
            # Mini-test offline sync is not processed (complex vocab unlock requires online)
            skipped += 1

    await session.commit()
    return SyncResponse(processed=processed, skipped=skipped, xp_total_earned=total_xp, conflicts=conflicts)
