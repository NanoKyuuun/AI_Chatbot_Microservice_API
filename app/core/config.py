from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "AI Chatbot Microservice API"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None

    # LLM
    OPENROUTER_API_KEY: str
    DEFAULT_CHAT_MODEL: str = "openai/gpt-4o-mini"

    # Storage
    STORAGE_DRIVER: str = "local"
    LOCAL_STORAGE_PATH: str = "/app/storage"

settings = Settings()
