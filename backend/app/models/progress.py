from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("curriculum_units.id", ondelete="CASCADE"), nullable=False
    )
    exercises_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_exercise_ids: Mapped[list] = mapped_column(
        ARRAY(item_type=Integer), nullable=False, default=list
    )
    mini_test_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mini_test_score: Mapped[Optional[int]] = mapped_column(SmallInteger)
    unit_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    unit_completed_at: Mapped[Optional[datetime]] = mapped_column()
    cards_added_to_vocab: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
