# backend/app/routers/settings.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_or_create_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


class SettingsPatch(BaseModel):
    show_instruction_translation: bool | None = None


class SettingsResponse(BaseModel):
    show_instruction_translation: bool


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    body: SettingsPatch,
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    user, _ = user_and_flag
    if body.show_instruction_translation is not None:
        user.show_instruction_translation = body.show_instruction_translation
    await session.commit()
    return SettingsResponse(show_instruction_translation=user.show_instruction_translation)
