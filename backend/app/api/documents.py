"""Routes to upload a PDF, list the current user's documents, and extract a document's text."""

import logging
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.auth import CurrentUser, get_current_user
from app.db.client import get_supabase
from app.models.document import DocumentOut, ProcessResult
from app.services.pdf_extractor import ExtractionError, extract_pages

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

BUCKET = "documents"
MAX_BYTES = 20 * 1024 * 1024  # 20 MB limit keeps memory use and abuse in check


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DocumentOut)
def upload_document(
    file: UploadFile, user: CurrentUser = Depends(get_current_user)
) -> dict:
    """Validate a PDF, store it privately, and record it in the documents table."""
    content = file.file.read(MAX_BYTES + 1)  # read one byte past the limit to detect oversize files
    if len(content) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File exceeds 20 MB")
    if not content.startswith(b"%PDF-"):  # real PDFs start with this signature, whatever the extension says
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is not a valid PDF")

    doc_id = str(uuid.uuid4())
    storage_path = f"{user.id}/{doc_id}.pdf"  # UUID path: no name collisions, no user-controlled path text
    display_name = os.path.basename(file.filename or "document.pdf")[:200]
    db = get_supabase()

    try:
        db.storage.from_(BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": "application/pdf"},
        )
    except Exception:
        logger.exception("Storage upload failed")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Could not store the file") from None

    try:
        result = (
            db.table("documents")
            .insert(
                {
                    "id": doc_id,
                    "user_id": user.id,  # always the verified ID from the token, never from the request body
                    "filename": display_name,
                    "storage_path": storage_path,
                }
            )
            .execute()
        )
    except Exception:
        logger.exception("Database insert failed")
        db.storage.from_(BUCKET).remove([storage_path])  # undo the upload so no orphan file is left behind
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not save the document") from None

    return result.data[0]


@router.get("", response_model=list[DocumentOut])
def list_documents(user: CurrentUser = Depends(get_current_user)) -> list[dict]:
    """Return only the current user's documents, newest first."""
    result = (
        get_supabase()
        .table("documents")
        .select("id, filename, status, page_count, created_at")
        .eq("user_id", user.id)  # this filter is the backend's isolation layer, because the secret key skips RLS
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.post("/{document_id}/process", response_model=ProcessResult)
def process_document(
    document_id: uuid.UUID, user: CurrentUser = Depends(get_current_user)
) -> dict:
    """Extract the document's text and record its page count (chunking and embedding come next)."""
    db = get_supabase()
    found = (
        db.table("documents")
        .select("id, storage_path")
        .eq("id", str(document_id))
        .eq("user_id", user.id)  # ownership check: someone else's id looks exactly like a missing one
        .execute()
    )
    if not found.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    try:
        pdf_bytes = db.storage.from_(BUCKET).download(found.data[0]["storage_path"])
    except Exception:
        logger.exception("Storage download failed")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Could not read the stored file") from None

    try:
        pages = extract_pages(pdf_bytes)
    except ExtractionError as error:
        db.table("documents").update({"status": "failed", "error_message": str(error)}).eq(
            "id", str(document_id)
        ).execute()  # the UI can show why a document failed instead of hanging forever
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from None

    db.table("documents").update({"page_count": len(pages)}).eq("id", str(document_id)).execute()
    return {
        "page_count": len(pages),
        "total_chars": sum(len(page.text) for page in pages),
        "empty_pages": sum(1 for page in pages if len(page.text) < 50),
    }