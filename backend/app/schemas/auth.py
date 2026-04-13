from pydantic import BaseModel
from app.models.enums import PlacementStatusEnum


class SessionResponse(BaseModel):
    user_id: int
    telegram_id: int
    streak_days: int
    total_xp: int
    placement_status: PlacementStatusEnum
    a1_skipped: bool
    show_instruction_translation: bool
    is_new_user: bool
