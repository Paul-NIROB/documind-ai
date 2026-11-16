"""Creates the single Supabase client used by the backend."""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_supabase() -> Client:
    """Return one cached client that uses the secret key (bypasses RLS; filter by user in code)."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)