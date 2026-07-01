"""
Integration tests for all FastAPI routers.

Uses httpx TestClient with mocked Redis, embeddings, and LLM services
to avoid any real network or infrastructure calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestHealthRouter:
    def test_health_ok(self, app_client):
        with patch("app.routers.health.check_redis_connection", return_value=True):
            response = app_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["redis"] == "connected"

    def test_health_degraded_when_redis_down(self, app_client):
        with patch("app.routers.health.check_redis_connection", return_value=False):
            response = app_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["redis"] == "disconnected"


class TestDocumentsRouter:
    def test_list_documents_empty(self, app_client):
        with patch("app.routers.documents.list_documents", return_value=[]):
            response = app_client.get("/documents")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_documents_returns_data(self, app_client):
        from app.models.document import DocumentInfo
        mock_docs = [
            DocumentInfo(file_id="abc", name="test.pdf", uploaded_at="2025-01-01T00:00:00Z", chunks=5)
        ]
        with patch("app.routers.documents.list_documents", return_value=mock_docs):
            response = app_client.get("/documents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["file_id"] == "abc"
        assert data[0]["name"] == "test.pdf"

    def test_delete_existing_document(self, app_client):
        with patch("app.routers.documents.delete_document", return_value=True):
            response = app_client.delete("/documents/file-001")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
        assert data["file_id"] == "file-001"

    def test_delete_nonexistent_document_returns_404(self, app_client):
        with patch("app.routers.documents.delete_document", return_value=False):
            response = app_client.delete("/documents/ghost-id")
        assert response.status_code == 404


class TestUploadRouter:
    def test_upload_txt_file(self, app_client):
        from app.services.ingestion import DocumentChunk

        mock_chunks = [
            DocumentChunk("text chunk", "test.txt", "file-001", 0, "2025-01-01T00:00:00Z")
        ]

        with patch("app.routers.upload.ingest_document", return_value=mock_chunks), \
             patch("app.routers.upload.embed_texts", return_value=[[0.1] * 384]), \
             patch("app.routers.upload.store_chunks", return_value=1):
            response = app_client.post(
                "/upload",
                files={"file": ("test.txt", b"Hello, this is a test document.", "text/plain")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["chunks_indexed"] == 1
        assert data["status"] == "indexed"
        assert data["name"] == "test.txt"
        assert "file_id" in data

    def test_upload_unsupported_format_returns_400(self, app_client):
        response = app_client.post(
            "/upload",
            files={"file": ("malware.exe", b"not a document", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_upload_no_filename_returns_400(self, app_client):
        response = app_client.post(
            "/upload",
            files={"file": ("", b"content", "text/plain")},
        )
        assert response.status_code == 400


class TestChatRouter:
    def test_chat_returns_sse_stream(self, app_client):
        async def mock_stream(session_id: str, question: str):
            yield 'data: {"type": "token", "content": "Hello"}\n\n'
            yield 'data: {"type": "sources", "data": []}\n\n'
            yield 'data: {"type": "done"}\n\n'

        with patch("app.routers.chat.stream_rag_response", side_effect=mock_stream):
            response = app_client.post(
                "/chat",
                json={"session_id": "sess-001", "question": "What is this document about?"},
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

    def test_chat_empty_question_returns_422(self, app_client):
        response = app_client.post(
            "/chat",
            json={"session_id": "sess-001", "question": ""},
        )
        assert response.status_code == 422
