import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.database import Base, get_session

TEST_BOT_TOKEN = "test_token"
# Use SQLite in-memory for tests (no Postgres required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# We need a shared engine for the session scope
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # single connection — required for in-memory SQLite
)
TestSessionFactory = async_sessionmaker(test_engine, expire_on_commit=False)


def make_fake_init_data(user_id: int = 123456789, first_name: str = "Test") -> str:
    """Constructs a valid Telegram initData string signed with TEST_BOT_TOKEN."""
    user_json = json.dumps(
        {"id": user_id, "first_name": first_name}, separators=(",", ":")
    )
    auth_date = str(int(time.time()))
    params = {"auth_date": auth_date, "user": user_json}
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )
    secret_key = hmac.new(
        b"WebAppData", TEST_BOT_TOKEN.encode(), hashlib.sha256
    ).digest()
    hash_val = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    params["hash"] = hash_val
    return urlencode(params)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once per test session."""
    # Patch PostgreSQL-specific types for SQLite compatibility
    import json as _json
    from sqlalchemy import JSON, Text
    from sqlalchemy.types import TypeDecorator

    class JSONList(TypeDecorator):
        """Stores a Python list as a JSON string in SQLite Text column."""
        impl = Text
        cache_ok = True

        def process_bind_param(self, value, dialect):
            if value is None:
                return "[]"
            if isinstance(value, list):
                return _json.dumps(value)
            return value  # already a string

        def process_result_value(self, value, dialect):
            if value is None:
                return []
            if isinstance(value, str):
                return _json.loads(value)
            return value

    from sqlalchemy import text as sa_text
    from sqlalchemy.sql.schema import DefaultClause

    for table in Base.metadata.tables.values():
        for col in table.columns:
            if col.type.__class__.__name__ == "JSONB":
                col.type = JSON()
            if col.type.__class__.__name__ == "ARRAY":
                col.type = JSONList()
            # SQLite doesn't have NOW() — replace with CURRENT_TIMESTAMP
            if getattr(col, "server_default", None) is not None:
                sd = col.server_default
                if hasattr(sd, "arg") and hasattr(sd.arg, "text") and "NOW()" in sd.arg.text.upper():
                    col.server_default = DefaultClause(sa_text("CURRENT_TIMESTAMP"))

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clean_tables():
    """Delete all rows between tests."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
def init_data() -> str:
    return make_fake_init_data()


async def override_get_session():
    async with TestSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client(monkeypatch):
    """Async HTTP client wired to the FastAPI app with test DB and test bot token."""
    monkeypatch.setattr("app.config.settings.bot_token", TEST_BOT_TOKEN)
    monkeypatch.setattr("app.config.settings.debug", False)  # always verify auth in tests

    from app.main import app
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
