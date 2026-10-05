from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    discord_token: str = Field(default="", validation_alias="DISCORD_TOKEN")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./zenkai.db",
        validation_alias="DATABASE_URL",
    )
    redis_url: str | None = Field(default=None, validation_alias="REDIS_URL")
    ai_provider: str = Field(default="none", validation_alias="AI_PROVIDER")
    ai_api_key: str = Field(default="", validation_alias="AI_API_KEY")
    ai_model: str = Field(default="", validation_alias="AI_MODEL")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    environment: Literal["development", "test", "production"] = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )
    guild_id: str | None = Field(default=None, validation_alias="GUILD_ID")

    @property
    def guild_id_int(self) -> int | None:
        if not self.guild_id:
            return None
        return int(self.guild_id)

    @property
    def redis_connection_url(self) -> str | None:
        return self.redis_url or None

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def require_discord_token(self) -> str:
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN is required to start the Discord runtime")
        return self.discord_token


@lru_cache
def get_settings() -> Settings:
    return Settings()
