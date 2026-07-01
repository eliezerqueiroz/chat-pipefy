"""
Pytest configuration and shared fixtures for all backend tests.

All external dependencies (Redis, OpenAI, Ollama) are mocked here
to ensure tests are fast, isolated, and free from network calls.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session")
def mock_redis():
    """Provide a mock Redis client for the entire test session."""
    mock = MagicMock()
    mock.ping.return_value = True
    mock.hset.return_value = 1
    mock.hgetall.return_value = {}
    mock.keys.return_value = []
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    mock.pipeline.return_value.__enter__ = lambda s: s
    mock.pipeline.return_value.__exit__ = MagicMock(return_value=False)
    mock.pipeline.return_value.execute.return_value = []
    mock.pipeline.return_value.hset = MagicMock()
    mock.pipeline.return_value.delete = MagicMock()

    # RedisSearch mock
    ft_mock = MagicMock()
    ft_mock.info.return_value = {"index_name": "docs"}
    ft_mock.create_index.return_value = True
    mock.ft.return_value = ft_mock

    return mock


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal valid PDF bytes for testing."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Hello World) Tj ET\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000274 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n369\n%%EOF"
    )


@pytest.fixture
def sample_txt_bytes() -> bytes:
    """Plain text file bytes for testing."""
    return b"This is a sample document.\nIt contains multiple lines.\nUsed for testing the ingestion pipeline."


@pytest.fixture
def mock_embeddings():
    """Mock embedding service returning fixed 384-dim vectors."""
    vector = [0.1] * 384
    with patch("app.services.embeddings.get_embedding_model") as mock_model:
        st_mock = MagicMock()
        st_mock.encode.return_value = [vector]
        mock_model.return_value = st_mock
        yield vector


@pytest.fixture
def app_client(mock_redis):
    """FastAPI test client with Redis mocked out."""
    with patch("app.services.vector_store.get_redis_client", return_value=mock_redis):
        with patch("app.services.vector_store.ensure_index_exists"):
            from app.main import app
            with TestClient(app) as client:
                yield client
