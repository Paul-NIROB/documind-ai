"""Verifies Supabase access tokens and exposes the logged-in user to routes."""

from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from pydantic import BaseModel

from app.core.config import get_settings

# auto_error=False lets us return our own clean 401 instead of FastAPI's default
bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """The verified identity attached to a request."""

    id: str
    email: str | None = None


@lru_cache
def get_jwks_client() -> PyJWKClient:
    """Create one client that downloads and caches Supabase's public signing keys."""
    settings = get_settings()
    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def _unauthorized() -> HTTPException:
    """Build one generic 401 so error messages never reveal why a token failed."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """Verify the Bearer token and return the user; raise 401 if anything is wrong."""
    if credentials is None:
        raise _unauthorized()

    token = credentials.credentials
    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],  # whitelist: the token cannot choose its own algorithm
            audience="authenticated",  # only tokens issued for logged-in users
        )
    except jwt.PyJWTError:
        raise _unauthorized() from None

    return CurrentUser(id=claims["sub"], email=claims.get("email"))