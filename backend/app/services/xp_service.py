from sqlalchemy.ext.asyncio import AsyncSession

from app.models.xp_log import XpLog
from app.models.user import User

# XP constants
XP_EXERCISE = 10
XP_MINI_TEST = 25
XP_CARD_KNOWN = 2
XP_STREAK_BONUS = 5


async def award_xp(
    session: AsyncSession,
    user: User,
    amount: int,
    reason: str,
    ref_id: int | None = None,
) -> None:
    """
    Awards XP to user and logs it in xp_log.
    Does NOT commit — caller is responsible for committing the session.
    """
    if amount <= 0:
        raise ValueError(f"award_xp: amount must be positive, got {amount}")
    user.total_xp += amount
    log_entry = XpLog(
        user_id=user.id,
        amount=amount,
        reason=reason,
        ref_id=ref_id,
    )
    session.add(log_entry)
