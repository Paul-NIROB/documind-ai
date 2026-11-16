"""Health check route used by humans, Docker and the deployment platform."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Report that the API is up and which settings are present (never their values)."""
    settings = get_settings()
    return {
        "status": "ok",
        "supabase_url_set": bool(settings.supabase_url),
        "supabase_secret_key_set": bool(settings.supabase_service_role_key),
    }