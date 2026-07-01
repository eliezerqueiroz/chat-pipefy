"""
Upload router.

Handles file upload, triggers ingestion pipeline, and returns chunk metadata.
File parsing and embedding runs as a FastAPI background task for non-blocking response.
"""

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from app.models.document import UploadResponse
from app.services.embeddings import embed_texts
from app.services.ingestion import ingest_document
from app.services.vector_store import store_chunks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def _validate_file(file: UploadFile) -> str:
    """
    Validate file extension and return the extension string.

    Args:
        file: The uploaded file object.

    Returns:
        Lowercase file extension string.

    Raises:
        HTTPException 400 if the file type is not supported.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name.")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return ext


async def _process_file(filename: str, file_bytes: bytes, file_id: str) -> int:
    """
    Full ingestion pipeline: parse → chunk → embed → store.

    Args:
        filename: Original file name.
        file_bytes: Raw file content.
        file_id: Pre-generated UUID for this document.

    Returns:
        Number of chunks indexed.
    """
    logger.info("Starting ingestion for %s (file_id=%s)", filename, file_id)

    # Parse and chunk
    chunks = ingest_document(filename, file_bytes, file_id)

    # Embed all chunk texts in a single batch call
    texts = [chunk.content for chunk in chunks]
    embeddings = embed_texts(texts)

    # Store in Redis
    count = store_chunks(chunks, embeddings)
    logger.info("Indexed %d chunks for %s", count, filename)
    return count


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile) -> UploadResponse:
    """
    Upload a document and trigger the RAG ingestion pipeline.

    Supported formats: PDF, TXT, DOCX (max 20 MB each).

    Returns:
        { file_id, name, chunks_indexed, status }
    """
    _validate_file(file)

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.",
        )

    file_id = str(uuid.uuid4())

    try:
        chunks_indexed = await _process_file(file.filename, file_bytes, file_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Ingestion failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}")

    return UploadResponse(
        file_id=file_id,
        name=file.filename,
        chunks_indexed=chunks_indexed,
        status="indexed",
    )
