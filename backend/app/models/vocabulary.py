from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, Float, ForeignKey, Integer, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.enums import CardStatusEnum


class VocabularyCard(Base):
    __tablename__ = "vocabulary_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("curriculum_units.id", ondelete="CASCADE"), nullable=False
    )
    word_gr: Mapped[str] = mapped_column(String(256), nullable=False)
    word_ru: Mapped[str] = mapped_column(String(256), nullable=False)
    example_gr: Mapped[Optional[str]] = mapped_column(Text)
    audio_path: Mapped[Optional[str]] = mapped_column(String(512))
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )


class UserCardState(Base):
    __tablename__ = "user_card_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vocabulary_cards.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[CardStatusEnum] = mapped_column(
        nullable=False, default=CardStatusEnum.NEW
    )
    interval_days: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    easiness_factor: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_review_at: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
