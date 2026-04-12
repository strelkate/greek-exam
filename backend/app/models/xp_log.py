from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Integer, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class XpLog(Base):
    __tablename__ = "xp_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    ref_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
