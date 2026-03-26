"""Application configuration and settings."""

from typing import Optional

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    log_level: str = Field(default="info")
    frontend_url: str = Field(default="http://localhost:3000")

    # LLM Configuration - MiniMax (OpenAI-compatible)
    openai_base_url: str = Field(default="https://api.minimax.io/v1")
    openai_api_key: str = Field(default="")
    minimax_api_key: Optional[str] = Field(default=None)  # Alias for openai_api_key

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Use minimax_api_key as fallback for openai_api_key
        if not self.openai_api_key and self.minimax_api_key:
            self.openai_api_key = self.minimax_api_key


def load_settings() -> Settings:
    """Load settings from environment."""
    return Settings()
