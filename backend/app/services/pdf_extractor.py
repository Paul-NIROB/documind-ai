"""Turns PDF bytes into a list of pages, each keeping its page number for citations."""

import pymupdf
from pydantic import BaseModel

# Below this average, a PDF is almost certainly scanned images with no real text layer
MIN_AVG_CHARS_PER_PAGE = 50


class ExtractionError(Exception):
    """Raised when a PDF cannot be turned into usable text; the message is safe to show users."""


class PageText(BaseModel):
    """The text of one page. page_number is 1-based, matching what a PDF viewer shows."""

    page_number: int
    text: str


def extract_pages(pdf_bytes: bytes) -> list[PageText]:
    """Return the text of every page, or raise ExtractionError with a clear reason."""
    try:
        document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:  # PyMuPDF raises several different error types for broken files
        raise ExtractionError("The PDF could not be read") from exc

    with document:
        if document.needs_pass:
            raise ExtractionError("The PDF is password protected")
        pages = [
            PageText(page_number=index + 1, text=page.get_text("text").strip())
            for index, page in enumerate(document)
        ]

    if not pages:
        raise ExtractionError("The PDF has no pages")

    average_chars = sum(len(page.text) for page in pages) / len(pages)
    if average_chars < MIN_AVG_CHARS_PER_PAGE:
        raise ExtractionError("The PDF looks scanned (no text layer); OCR is not supported yet")

    return pages