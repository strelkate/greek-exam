from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, SmallInteger, String, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.enums import ExerciseTypeEnum


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("curriculum_units.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[ExerciseTypeEnum] = mapped_column(
        SAEnum(ExerciseTypeEnum, name="exercise_type_enum", native_enum=False),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    audio_paths: Mapped[list[str]] = mapped_column(
        ARRAY(item_type=String), nullable=False, default=list
    )
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
    generation_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("generation_runs.id", ondelete="SET NULL"), nullable=True
    )
