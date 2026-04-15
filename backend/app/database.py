import json as _json
from sqlalchemy import JSON, Text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator

from app.config import settings


class _JSONList(TypeDecorator):
    """Stores a Python list as a JSON string — SQLite fallback for ARRAY."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return _json.dumps(value) if isinstance(value, list) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return _json.loads(value) if isinstance(value, str) else value


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _make_engine(url: str):
    if _is_sqlite(url):
        return create_async_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_async_engine(url, echo=settings.debug)


engine = _make_engine(settings.database_url)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def patch_sqlite_types(base) -> None:
    """Replace PostgreSQL-specific column types with SQLite-compatible ones."""
    from sqlalchemy.sql.schema import DefaultClause
    from sqlalchemy import text as sa_text

    for table in base.metadata.tables.values():
        for col in table.columns:
            type_name = col.type.__class__.__name__
            if type_name == "JSONB":
                col.type = JSON()
            elif type_name == "ARRAY":
                col.type = _JSONList()
            sd = getattr(col, "server_default", None)
            if sd is not None and hasattr(sd, "arg") and hasattr(sd.arg, "text"):
                if "NOW()" in sd.arg.text.upper():
                    col.server_default = DefaultClause(sa_text("CURRENT_TIMESTAMP"))


async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
