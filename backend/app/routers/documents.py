"""Documents listing and deletion router."""

from fastapi import APIRouter, HTTPException

from app.models.document import DeleteResponse, DocumentInfo
from app.services.vector_store import delete_document, list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentInfo])
def get_documents() -> list[DocumentInfo]:
    """
    List all indexed documents with their metadata.

    Returns:
        List of documents sorted by upload date (newest first).
    """
    return list_documents()


@router.delete("/{file_id}", response_model=DeleteResponse)
def remove_document(file_id: str) -> DeleteResponse:
    """
    Remove a document and all its vector chunks from Redis.

    Args:
        file_id: The document's unique identifier.

    Returns:
        { deleted: true, file_id: "..." } on success.

    Raises:
        404 if the document is not found.
    """
    deleted = delete_document(file_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document '{file_id}' not found.")
    return DeleteResponse(deleted=True, file_id=file_id)
