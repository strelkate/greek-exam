from datetime import date, datetime
from typing import Optional
from sqlalchemy import BigInteger, Boolean, Date, Enum as SAEnum, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.enums import PlacementStatusEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(64))
    telegram_first_name: Mapped[Optional[str]] = mapped_column(String(128))
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_active_date: Mapped[Optional[date]] = mapped_column(Date)
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    placement_status: Mapped[PlacementStatusEnum] = mapped_column(
        SAEnum(PlacementStatusEnum, name="placement_status_enum", native_enum=False),
        nullable=False,
        default=PlacementStatusEnum.PENDING,
    )
    a1_skipped: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    show_instruction_translation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"),
        onupdate=func.now(),
        nullable=False,
    )
