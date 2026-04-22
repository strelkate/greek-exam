from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    telegram_id: int
    streak_days: int
    total_xp: int
    show_instruction_translation: bool
    is_new_user: bool
