"""
Document ingestion service.

Responsibilities:
- Parse PDF, TXT, and DOCX files.
- Split text into overlapping chunks using RecursiveCharacterTextSplitter.
- Return structured chunk objects ready for embedding and storage.
"""

import io
import logging
from datetime import datetime, timezone
from dataclasses import dataclass

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a single text chunk with its metadata."""

    content: str
    source: str
    file_id: str
    chunk_index: int
    uploaded_at: str


def parse_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file."""
    text_parts: list[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def parse_txt(file_bytes: bytes) -> str:
    """Decode a plain text file."""
    return file_bytes.decode("utf-8", errors="replace")


def parse_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file."""
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())


def parse_document(filename: str, file_bytes: bytes) -> str:
    """
    Dispatch to the appropriate parser based on file extension.

    Args:
        filename: Original filename with extension.
        file_bytes: Raw file bytes.

    Returns:
        Extracted plain text.

    Raises:
        ValueError: If the file format is not supported.
    """
    ext = filename.rsplit(".", 1)[-1].lower()
    parsers = {
        "pdf": parse_pdf,
        "txt": parse_txt,
        "docx": parse_docx,
    }
    if ext not in parsers:
        raise ValueError(f"Unsupported file format: .{ext}. Supported: pdf, txt, docx")

    logger.info("Parsing file %s (format: %s)", filename, ext)
    return parsers[ext](file_bytes)


def chunk_document(
    text: str,
    filename: str,
    file_id: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> list[DocumentChunk]:
    """
    Split a document's text into overlapping chunks.

    Args:
        text: Full document text.
        filename: Original filename (used as `source` metadata).
        file_id: Unique document identifier.
        chunk_size: Token size per chunk (defaults to settings value).
        chunk_overlap: Overlap between chunks (defaults to settings value).

    Returns:
        List of DocumentChunk objects.
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(text)
    uploaded_at = datetime.now(timezone.utc).isoformat()

    chunks = [
        DocumentChunk(
            content=chunk,
            source=filename,
            file_id=file_id,
            chunk_index=i,
            uploaded_at=uploaded_at,
        )
        for i, chunk in enumerate(raw_chunks)
    ]

    logger.info("Chunked '%s' into %d chunks (size=%d, overlap=%d)", filename, len(chunks), chunk_size, chunk_overlap)
    return chunks


def ingest_document(filename: str, file_bytes: bytes, file_id: str) -> list[DocumentChunk]:
    """
    Full ingestion pipeline: parse → chunk.

    Args:
        filename: Original file name.
        file_bytes: Raw file bytes.
        file_id: Pre-generated unique ID for this document.

    Returns:
        List of DocumentChunk objects ready for embedding and storage.
    """
    text = parse_document(filename, file_bytes)
    if not text.strip():
        raise ValueError(f"Document '{filename}' produced no extractable text.")
    return chunk_document(text, filename, file_id)
