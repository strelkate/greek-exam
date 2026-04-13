from fastapi import APIRouter, Depends

from app.middleware.auth import get_or_create_user
from app.models.user import User
from app.schemas.auth import SessionResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/session", response_model=SessionResponse)
async def create_session(
    user_and_flag: tuple[User, bool] = Depends(get_or_create_user),
):
    user, is_new_user = user_and_flag
    return SessionResponse(
        user_id=user.id,
        telegram_id=user.telegram_id,
        streak_days=user.streak_days,
        total_xp=user.total_xp,
        placement_status=user.placement_status,
        a1_skipped=user.a1_skipped,
        show_instruction_translation=user.show_instruction_translation,
        is_new_user=is_new_user,
    )
