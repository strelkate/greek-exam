from pydantic import BaseModel, ConfigDict
from app.models.enums import ExerciseTypeEnum, LevelEnum


class LevelProgress(BaseModel):
    level: LevelEnum
    total_units: int
    completed_units: int
    progress_percent: int


class LevelsResponse(BaseModel):
    levels: list[LevelProgress]


class UnitSummary(BaseModel):
    id: int
    title: str
    order_index: int
    exercises_total: int
    exercises_completed: int
    mini_test_passed: bool
    unit_completed: bool


class UnitsResponse(BaseModel):
    units: list[UnitSummary]


class ExerciseMeta(BaseModel):
    id: int
    type: ExerciseTypeEnum
    order_index: int
    audio_paths: list[str]
    completed: bool


class VocabCardMeta(BaseModel):
    id: int
    word_gr: str
    word_ru: str
    audio_path: str | None = None


class UnitDetailResponse(BaseModel):
    id: int
    title: str
    level: LevelEnum
    mini_test_passed: bool
    unit_completed: bool
    exercises: list[ExerciseMeta]
    vocabulary_cards: list[VocabCardMeta]
