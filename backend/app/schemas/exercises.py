from pydantic import BaseModel
from app.models.enums import ExerciseTypeEnum


class ExerciseResponse(BaseModel):
    id: int
    unit_id: int
    type: ExerciseTypeEnum
    content: dict
    audio_paths: list[str]


class CompleteExerciseRequest(BaseModel):
    score: int
    total: int


class UnitProgressInline(BaseModel):
    exercises_completed: int
    exercises_total: int
    mini_test_unlocked: bool


class CompleteExerciseResponse(BaseModel):
    xp_earned: int
    xp_breakdown: dict[str, int]
    streak_days: int
    streak_updated: bool
    unit_progress: UnitProgressInline
