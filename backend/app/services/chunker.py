"""Splits extracted pages into overlapping chunks that keep their page number for citations."""

from pydantic import BaseModel

from app.services.pdf_extractor import PageText

CHUNK_SIZE = 1000  # maximum characters per chunk
CHUNK_OVERLAP = 150  # characters repeated between neighbouring chunks


class Chunk(BaseModel):
    """One piece of text ready to be embedded; page_number is what a citation will show."""

    chunk_index: int  # position within the whole document, starting at 0
    page_number: int
    content: str

def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Cut one cleaned text into pieces of at most chunk_size characters with the given overlap."""
    ...  # your code goes here

def chunk_pages(
    pages: list[PageText],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Turn pages into chunks; layer 1 makes one chunk per page, with no cutting yet."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")  # otherwise the loop you add later never advances

    chunks: list[Chunk] = []
    for page in pages:
        cleaned = " ".join(page.text.split())  # collapses every run of spaces and newlines into a single space
        if not cleaned:
            continue  # near-empty pages produce no chunks
        chunks.append(
            Chunk(
                chunk_index=len(chunks),  # the next free index, so indexes stay unique and in order
                page_number=page.page_number,
                content=cleaned,
            )
        )
    return chunks