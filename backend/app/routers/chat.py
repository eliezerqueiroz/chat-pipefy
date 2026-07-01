"""
Chat router.

Implements the POST /chat endpoint with Server-Sent Events (SSE) streaming.
The RAG pipeline runs fully async:
  embed query → KNN search Redis → build prompt → stream LLM → emit sources
"""

import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.services.rag import stream_rag_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """
    Start a RAG-powered chat session with SSE streaming.

    Accepts a session_id and a question, streams the LLM response token by token,
    and emits a final "sources" event with the retrieved document chunks.

    SSE event types:
      - {"type": "token",   "content": "..."}   — streamed answer tokens
      - {"type": "sources", "data": [...]}        — source citations
      - {"type": "done"}                           — end of stream
    """
    logger.info("Chat request: session_id=%s, question=%r", request.session_id, request.question[:80])

    return StreamingResponse(
        stream_rag_response(request.session_id, request.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
