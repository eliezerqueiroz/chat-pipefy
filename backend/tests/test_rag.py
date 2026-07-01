"""
Unit tests for the RAG service.

Tests cover session history management, context retrieval, and the full
streaming pipeline — all with mocked LLM and Redis dependencies.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSessionHistory:
    def test_load_empty_history(self):
        """Loading history for a new session returns an empty list."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None

        with patch("app.services.rag.get_redis_client", return_value=mock_redis):
            from app.services.rag import load_session_history
            result = load_session_history("new-session")

        assert result == []

    def test_load_existing_history(self):
        """Existing history is deserialized correctly."""
        history_data = json.dumps([
            {"role": "user", "content": "What is RAG?"},
            {"role": "assistant", "content": "RAG stands for Retrieval-Augmented Generation."},
        ])
        mock_redis = MagicMock()
        mock_redis.get.return_value = history_data.encode()

        with patch("app.services.rag.get_redis_client", return_value=mock_redis):
            from app.services.rag import load_session_history
            result = load_session_history("existing-session")

        assert len(result) == 2

    def test_save_message_to_history(self):
        """Messages are saved and TTL is set."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None

        with patch("app.services.rag.get_redis_client", return_value=mock_redis):
            from app.services.rag import save_message_to_history
            save_message_to_history("sess-001", "user", "Hello!")

        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        # Verify TTL is set (ex parameter)
        assert call_args.kwargs.get("ex") == 86400


class TestRetrieveContext:
    def test_returns_formatted_context(self):
        mock_results = [
            {"content": "Doc chunk 1", "source": "file.pdf", "chunk_index": 0},
            {"content": "Doc chunk 2", "source": "file.pdf", "chunk_index": 1},
        ]

        with patch("app.services.rag.embed_query", return_value=[0.1] * 384), \
             patch("app.services.rag.search_similar_chunks", return_value=mock_results):
            from app.services.rag import retrieve_context
            results, context = retrieve_context("What is in the document?")

        assert len(results) == 2
        assert "Doc chunk 1" in context
        assert "Doc chunk 2" in context

    def test_returns_no_results_message(self):
        with patch("app.services.rag.embed_query", return_value=[0.1] * 384), \
             patch("app.services.rag.search_similar_chunks", return_value=[]):
            from app.services.rag import retrieve_context
            results, context = retrieve_context("Unknown question")

        assert results == []
        assert "No relevant documents" in context


class TestStreamRagResponse:
    @pytest.mark.asyncio
    async def test_streams_tokens_and_sources(self):
        """Full streaming pipeline emits token, sources, and done events."""
        mock_results = [
            {"content": "Relevant chunk.", "source": "doc.txt", "chunk_index": 0},
        ]

        async def fake_astream(*args, **kwargs):
            for token in ["Hello", " ", "world"]:
                yield token

        mock_chain = MagicMock()
        mock_chain.astream = fake_astream

        mock_llm = MagicMock()
        mock_prompt = MagicMock()
        mock_parser = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=MagicMock(
            __or__=MagicMock(return_value=mock_chain)
        ))

        with patch("app.services.rag.embed_query", return_value=[0.1] * 384), \
             patch("app.services.rag.search_similar_chunks", return_value=mock_results), \
             patch("app.services.rag.get_redis_client", return_value=MagicMock(get=MagicMock(return_value=None), set=MagicMock())), \
             patch("app.services.rag.build_prompt", return_value=mock_prompt), \
             patch("app.services.rag.get_llm", return_value=mock_llm), \
             patch("app.services.rag.StrOutputParser", return_value=mock_parser):

            from app.services.rag import stream_rag_response

            events = []
            async for event in stream_rag_response("sess-test", "Test question"):
                events.append(event)

        # Should have: token events + sources event + done event
        assert any('"type": "sources"' in e for e in events)
        assert any('"type": "done"' in e for e in events)
