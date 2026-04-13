from typing import TypedDict


class SM2Result(TypedDict):
    interval_days: float
    easiness_factor: float
    repetitions: int


def calculate_sm2(
    known: bool,
    interval_days: float,
    easiness_factor: float,
    repetitions: int,
) -> SM2Result:
    """
    Simplified SM-2 spaced repetition algorithm.
    known=True  → quality score 5 (perfect recall)
    known=False → quality score 1 (blackout)
    """
    q = 5 if known else 1

    if q < 3:
        # Failed: reset repetitions and interval
        new_repetitions = 0
        new_interval = 1.0
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1.0
        elif new_repetitions == 2:
            new_interval = 6.0
        else:
            new_interval = interval_days * easiness_factor

    # Update easiness factor (SM-2 formula)
    new_ef = easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(1.3, new_ef)  # EF floor

    return SM2Result(
        interval_days=round(new_interval, 2),
        easiness_factor=round(new_ef, 4),
        repetitions=new_repetitions,
    )
