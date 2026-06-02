"""
Configuration management for the AI Chatbot backend.
Loads settings from environment variables.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env file from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider (nvidia or anthropic)
    llm_provider: str = Field(default="nvidia", env="LLM_PROVIDER")

    # NVIDIA Configuration
    nvidia_api_key: str = Field(default="", env="NVIDIA_API_KEY")
    nvidia_model: str = Field(default="meta/llama-3.1-8b-instruct", env="NVIDIA_MODEL")
    nvidia_api_base: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        env="NVIDIA_API_BASE"
    )

    # Anthropic Configuration (alternative)
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")

    # Server Configuration
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")

    # CORS Configuration
    frontend_url: str = Field(default="http://localhost:5173", env="FRONTEND_URL")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    # Timeouts
    request_timeout_seconds: int = Field(default=30, env="REQUEST_TIMEOUT_SECONDS")
    tool_timeout_seconds: int = Field(default=15, env="TOOL_TIMEOUT_SECONDS")

    # Tool Configuration
    duckduckgo_max_results: int = Field(default=5, env="DUCKDUCKGO_MAX_RESULTS")
    weather_api_base: str = Field(default="https://api.open-meteo.com/v1", env="WEATHER_API_BASE")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create a default instance
settings = get_settings()
