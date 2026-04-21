from datetime import date
from pydantic import BaseModel
from app.models.enums import CardStatusEnum


class CardDue(BaseModel):
    id: int
    word_gr: str
    word_ru: str
    audio_path: str | None = None
    status: CardStatusEnum
    next_review_at: date


class DueCardsResponse(BaseModel):
    due_count: int
    cards: list[CardDue]


class ReviewRequest(BaseModel):
    known: bool


class ReviewResponse(BaseModel):
    card_id: int
    new_status: CardStatusEnum
    next_review_at: date
    interval_days: float
    xp_earned: int


class VocabStatsResponse(BaseModel):
    total_cards: int
    learning_count: int
    learned_count: int
    due_today: int
    new_count: int
