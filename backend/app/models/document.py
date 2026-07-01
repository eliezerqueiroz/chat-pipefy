"""
Pydantic schemas for document-related requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    file_id: str
    name: str
    chunks_indexed: int
    status: str


class DocumentInfo(BaseModel):
    file_id: str
    name: str
    uploaded_at: str
    chunks: int


class DeleteResponse(BaseModel):
    deleted: bool
    file_id: str
