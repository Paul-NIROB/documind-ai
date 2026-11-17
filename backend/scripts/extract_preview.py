"""Dev helper: extract a local PDF and print page statistics."""

import sys
from pathlib import Path

from app.services.pdf_extractor import ExtractionError, extract_pages


def main() -> None:
    """Print page count, text volume and a preview of the fullest page."""
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.extract_preview <path-to-pdf>")
        sys.exit(1)

    try:
        pages = extract_pages(Path(sys.argv[1]).read_bytes())
    except ExtractionError as error:
        print(f"Extraction failed: {error}")
        sys.exit(1)

    total_chars = sum(len(page.text) for page in pages)
    empty_pages = [page.page_number for page in pages if len(page.text) < 50]
    fullest = max(pages, key=lambda page: len(page.text))
    print(f"Pages: {len(pages)}")
    print(f"Total characters: {total_chars}")
    print(f"Pages with almost no text: {len(empty_pages)} {empty_pages[:10]}")
    print(f"Fullest page: {fullest.page_number} ({len(fullest.text)} chars)")
    print("Preview of page 1:", repr(pages[0].text[:300]))


if __name__ == "__main__":
    main()