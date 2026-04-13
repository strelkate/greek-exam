from datetime import date as date_type
from typing import Optional, TypedDict


class StreakResult(TypedDict):
    streak_days: int
    updated: bool


def calculate_streak(
    last_active_date: date_type | None,
    current_streak: int,
    today: date_type | None = None,
) -> StreakResult:
    """
    Returns updated streak based on last_active_date vs today.
    - Same day: no change
    - Next day: increment
    - Gap > 1 day: reset to 1
    - Never active: start at 1
    """
    if today is None:
        today = date_type.today()

    if last_active_date is None:
        return StreakResult(streak_days=1, updated=True)

    delta = (today - last_active_date).days

    if delta == 0:
        return StreakResult(streak_days=current_streak, updated=False)
    elif delta == 1:
        return StreakResult(streak_days=current_streak + 1, updated=True)
    else:
        return StreakResult(streak_days=1, updated=True)
