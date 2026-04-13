# backend/app/schemas/sync.py
from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class ExerciseCompleteEvent(BaseModel):
    type: Literal["exercise_complete"]
    exercise_id: int
    score: int
    total: int
    occurred_at: datetime


class CardReviewEvent(BaseModel):
    type: Literal["card_review"]
    card_id: int
    known: bool
    occurred_at: datetime


class MiniTestCompleteEvent(BaseModel):
    type: Literal["mini_test_complete"]
    unit_id: int
    score: int
    total: int
    occurred_at: datetime


SyncEvent = Annotated[
    Union[ExerciseCompleteEvent, CardReviewEvent, MiniTestCompleteEvent],
    Field(discriminator="type"),
]


class SyncRequest(BaseModel):
    events: list[SyncEvent]


class SyncResponse(BaseModel):
    processed: int
    skipped: int
    xp_total_earned: int
    conflicts: list[str]
