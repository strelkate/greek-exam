from datetime import date
import pytest
from app.services.sm2_service import calculate_sm2
from app.services.streak_service import calculate_streak


# --- SM-2 tests ---

def test_sm2_first_success():
    result = calculate_sm2(known=True, interval_days=1.0, easiness_factor=2.5, repetitions=0)
    assert result["interval_days"] == 1.0
    assert result["repetitions"] == 1
    # SM-2: EF increases on perfect recall (q=5): 2.5 + 0.1 = 2.6
    assert result["easiness_factor"] == pytest.approx(2.6, abs=0.01)


def test_sm2_second_success():
    result = calculate_sm2(known=True, interval_days=1.0, easiness_factor=2.5, repetitions=1)
    assert result["interval_days"] == 6.0
    assert result["repetitions"] == 2


def test_sm2_third_success():
    result = calculate_sm2(known=True, interval_days=6.0, easiness_factor=2.5, repetitions=2)
    assert result["interval_days"] == pytest.approx(15.0, abs=0.5)
    assert result["repetitions"] == 3


def test_sm2_failure_resets():
    result = calculate_sm2(known=False, interval_days=10.0, easiness_factor=2.5, repetitions=3)
    assert result["interval_days"] == 1.0
    assert result["repetitions"] == 0
    assert result["easiness_factor"] < 2.5
    assert result["easiness_factor"] >= 1.3  # never below minimum


def test_sm2_easiness_floor():
    # Repeated failures should not drop below 1.3
    ef = 2.5
    for _ in range(20):
        r = calculate_sm2(known=False, interval_days=1.0, easiness_factor=ef, repetitions=0)
        ef = r["easiness_factor"]
    assert ef == pytest.approx(1.3, abs=0.01)


# --- Streak tests ---

def test_streak_same_day():
    result = calculate_streak(last_active_date=date.today(), current_streak=5)
    assert result["streak_days"] == 5
    assert result["updated"] is False


def test_streak_next_day():
    from datetime import timedelta
    yesterday = date.today() - timedelta(days=1)
    result = calculate_streak(last_active_date=yesterday, current_streak=5)
    assert result["streak_days"] == 6
    assert result["updated"] is True


def test_streak_broken():
    from datetime import timedelta
    two_days_ago = date.today() - timedelta(days=2)
    result = calculate_streak(last_active_date=two_days_ago, current_streak=5)
    assert result["streak_days"] == 1
    assert result["updated"] is True


def test_streak_new_user():
    result = calculate_streak(last_active_date=None, current_streak=0)
    assert result["streak_days"] == 1
    assert result["updated"] is True
