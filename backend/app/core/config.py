"""Central application settings, loaded once from the root .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] is the repository root
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Typed view of the environment variables the backend needs."""

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    frontend_url: str = "http://localhost:3000"

    # env_file points at the root .env no matter where uvicorn is started from
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return one cached Settings instance so .env is read only once."""
    return Settings()