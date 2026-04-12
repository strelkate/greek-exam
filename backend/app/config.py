from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://greekapp:greekapp@localhost/greekapp"
    bot_token: str = "test_token"
    cors_origins: list[str] = ["*"]
    debug: bool = False


settings = Settings()
