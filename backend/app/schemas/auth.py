from pydantic import BaseModel, ConfigDict
from app.models.enums import PlacementStatusEnum


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    telegram_id: int
    streak_days: int
    total_xp: int
    placement_status: PlacementStatusEnum
    a1_skipped: bool
    show_instruction_translation: bool
    is_new_user: bool
