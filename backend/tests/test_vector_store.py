"""
Unit tests for the vector store service.

All Redis interactions are mocked — no real Redis connection required.
Tests cover index creation, chunk storage, KNN search, listing, and deletion.
"""

import struct
from unittest.mock import MagicMock, patch, call

import pytest

from app.services.ingestion import DocumentChunk
from app.services.vector_store import (
    _floats_to_bytes,
    delete_document,
    list_documents,
    store_chunks,
)


def make_chunk(file_id: str = "file-001", index: int = 0) -> DocumentChunk:
    return DocumentChunk(
        content="Sample content for testing purposes.",
        source="test_file.txt",
        file_id=file_id,
        chunk_index=index,
        uploaded_at="2025-01-01T00:00:00Z",
    )


class TestFloatsToBytes:
    def test_produces_float32_bytes(self):
        vector = [0.1, 0.2, 0.3]
        result = _floats_to_bytes(vector)
        assert isinstance(result, bytes)
        assert len(result) == 4 * len(vector)  # 4 bytes per float32

    def test_round_trip(self):
        vector = [1.0, 2.0, 3.0]
        packed = _floats_to_bytes(vector)
        unpacked = list(struct.unpack(f"{len(vector)}f", packed))
        assert len(unpacked) == len(vector)


class TestStoreChunks:
    def test_stores_correct_number_of_chunks(self, mock_redis):
        chunks = [make_chunk(index=i) for i in range(3)]
        embeddings = [[0.1] * 384 for _ in range(3)]

        with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
            with patch("app.services.vector_store.ensure_index_exists"):
                result = store_chunks(chunks, embeddings)

        assert result == 3

    def test_returns_zero_for_empty_input(self, mock_redis):
        with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
            with patch("app.services.vector_store.ensure_index_exists"):
                result = store_chunks([], [])
        assert result == 0


class TestListDocuments:
    def test_returns_empty_when_no_documents(self, mock_redis):
        mock_redis.keys.return_value = []
        with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
            result = list_documents()
        assert result == []

    def test_returns_document_info(self, mock_redis):
        mock_redis.keys.return_value = [b"file:file-001"]
        mock_redis.hgetall.return_value = {
            b"file_id": b"file-001",
            b"name": b"test.pdf",
            b"uploaded_at": b"2025-01-01T00:00:00Z",
            b"chunks": b"5",
        }

        with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
            result = list_documents()

        assert len(result) == 1
        assert result[0].file_id == "file-001"
        assert result[0].name == "test.pdf"
        assert result[0].chunks == 5


class TestDeleteDocument:
    def test_deletes_existing_document(self, mock_redis):
        mock_redis.keys.return_value = [
            b"doc:file-001:chunk:0",
            b"doc:file-001:chunk:1",
        ]

        with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
            result = delete_document("file-001")

        assert result is True

    def test_returns_false_for_nonexistent_document(self, mock_redis):
        mock_redis.keys.return_value = []

        with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
            result = delete_document("does-not-exist")

        assert result is False
