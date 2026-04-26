"""
Nexus Social — Configuration
==============================
Pydantic settings loaded from environment variables.
In Cloud Run, GEMINI_API_KEY is injected from Secret Manager.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # GCP
    gcp_project_id: str = ""
    secret_name: str = "gemini-api-key"

    # App
    environment: str = "development"
    port: int = 8080
    log_level: str = "INFO"

    # AI tuning per feature
    caption_temperature: float = 0.9      # Creative — higher
    hashtag_temperature: float = 0.7
    moderation_temperature: float = 0.2   # Factual — lower
    sentiment_temperature: float = 0.4
    growth_temperature: float = 0.7
    predict_temperature: float = 0.5
    search_temperature: float = 0.6
    trending_temperature: float = 0.6
    max_output_tokens: int = 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
