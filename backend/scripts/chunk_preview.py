"""Dev helper: chunk a local PDF and print statistics."""

import sys
from pathlib import Path

from app.services.chunker import chunk_pages
from app.services.pdf_extractor import extract_pages


def main() -> None:
    """Print chunk counts and sizes, and check the basic rules."""
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.chunk_preview <path-to-pdf>")
        sys.exit(1)

    pages = extract_pages(Path(sys.argv[1]).read_bytes())
    chunks = chunk_pages(pages)
    sizes = [len(chunk.content) for chunk in chunks]
    valid_pages = {page.page_number for page in pages}

    print(f"Pages: {len(pages)}  Chunks: {len(chunks)}")
    print(f"Chunk length min/avg/max: {min(sizes)} / {sum(sizes) // len(sizes)} / {max(sizes)}")
    print(f"Any chunk over 1000 chars: {any(size > 1000 for size in sizes)}")
    print(f"All page numbers valid: {all(chunk.page_number in valid_pages for chunk in chunks)}")
    print(f"Indexes unique and in order: {[c.chunk_index for c in chunks] == list(range(len(chunks)))}")
    middle = chunks[len(chunks) // 2]
    print(f"Sample chunk (page {middle.page_number}):", repr(middle.content[:300]))


if __name__ == "__main__":
    main()