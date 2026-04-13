from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Enum as SAEnum, Integer, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.enums import LevelEnum


class CurriculumUnit(Base):
    __tablename__ = "curriculum_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[LevelEnum] = mapped_column(
        SAEnum(LevelEnum, name="level_enum", native_enum=False),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
