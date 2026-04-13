from datetime import date
from typing import TypedDict


class StreakResult(TypedDict):
    streak_days: int
    updated: bool


def calculate_streak(
    last_active_date: date | None,
    current_streak: int,
) -> StreakResult:
    """
    Returns updated streak based on last_active_date vs today.
    - Same day: no change
    - Next day: increment
    - Gap > 1 day: reset to 1
    - Never active: start at 1
    """
    today = date.today()

    if last_active_date is None:
        return StreakResult(streak_days=1, updated=True)

    delta = (today - last_active_date).days

    if delta == 0:
        return StreakResult(streak_days=current_streak, updated=False)
    elif delta == 1:
        return StreakResult(streak_days=current_streak + 1, updated=True)
    else:
        return StreakResult(streak_days=1, updated=True)
