"""Pydantic schema describing a document in API responses."""

from pydantic import BaseModel


class DocumentOut(BaseModel):
    """What the API returns about a document; storage_path is deliberately not exposed."""

    id: str
    filename: str
    status: str
    page_count: int | None = None
    created_at: str