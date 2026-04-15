from typing import Optional
from sqlalchemy import String, Text, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
