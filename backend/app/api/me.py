"""Route that returns the currently logged-in user; used to test authentication."""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user

router = APIRouter(tags=["auth"])


@router.get("/me")
def read_me(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Return the verified user; a missing or bad token never reaches this body."""
    return user