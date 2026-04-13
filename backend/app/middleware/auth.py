import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.user import User


def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """
    Verifies Telegram WebApp initData HMAC-SHA256 signature.
    Returns parsed user dict or raises ValueError.
    """
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise ValueError("Missing hash")

    auth_date = int(params.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        raise ValueError("initData expired")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()
    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Invalid hash")

    return json.loads(params.get("user", "{}"))


async def get_current_user_data(
    x_telegram_init_data: str = Header(...),
) -> dict:
    """FastAPI dependency: parses and verifies initData header."""
    try:
        user_data = verify_telegram_init_data(x_telegram_init_data, settings.bot_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    if not user_data.get("id"):
        raise HTTPException(status_code=401, detail="No user in initData")
    return user_data


async def get_or_create_user(
    user_data: dict = Depends(get_current_user_data),
    session: AsyncSession = Depends(get_session),
) -> tuple[User, bool]:
    """Returns (user, is_new_user). Creates user if not exists."""
    telegram_id = user_data["id"]
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        return user, False

    user = User(
        telegram_id=telegram_id,
        telegram_username=user_data.get("username"),
        telegram_first_name=user_data.get("first_name"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True
