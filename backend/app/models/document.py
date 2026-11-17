"""Pydantic schemas describing documents in API responses."""

from pydantic import BaseModel


class DocumentOut(BaseModel):
    """What the API returns about a document; storage_path is deliberately not exposed."""

    id: str
    filename: str
    status: str
    page_count: int | None = None
    created_at: str


class ProcessResult(BaseModel):
    """Summary returned after a document's text has been extracted."""

    page_count: int
    total_chars: int
    empty_pages: int