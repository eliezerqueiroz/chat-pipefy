"""
RAG (Retrieval-Augmented Generation) service.

Implements the full RAG pipeline using LangChain LCEL:
  embed query → KNN search Redis → build prompt → stream LLM response

Supports multiple LLM backends (selected via LLM_PROVIDER env var):
  - "ollama": Ollama local server (no API key required, needs ~5 GB RAM)
  - "openai": OpenAI GPT-4o
  - "gemini": Gemini API (embeddings + LLM both cloud)
  - "gemini-hybrid": Local embeddings + Gemini LLM (recommended for low-RAM machines)
"""

import json
import logging
from typing import AsyncGenerator

import redis as redis_lib
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.config import settings
from app.models.chat import Source
from app.services.embeddings import embed_query
from app.services.vector_store import get_redis_client, search_similar_chunks

logger = logging.getLogger(__name__)

# Session history Redis key prefix
HISTORY_PREFIX = "history:"

# Prompt template used for grounded RAG answers
RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided document context.

Rules:
- Answer only based on the context below.
- If the context does not contain enough information, say so clearly.
- Be concise and accurate.
- Do not fabricate information.

Context from documents:
{context}"""


def get_llm(streaming: bool = True):
    """
    Instantiate and return the configured LLM client.

    Args:
        streaming: Whether to enable token streaming.

    Returns:
        A LangChain-compatible chat model.
    """
    if settings.llm_provider == "ollama":
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            streaming=streaming,
            temperature=0.2,
        )
    elif settings.llm_provider == "groq-hybrid":
        from langchain_groq import ChatGroq

        return ChatGroq(
            api_key=settings.groq_api_key,
            model="llama-3.3-70b-versatile",
            streaming=streaming,
            temperature=0.2,
        )
    elif settings.llm_provider in ("gemini", "gemini-hybrid"):
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            google_api_key=settings.gemini_api_key,
            model="gemini-2.0-flash-lite",
            streaming=streaming,
            temperature=0.2,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.llm_model,
        streaming=streaming,
        temperature=0.2,
    )


def build_prompt() -> ChatPromptTemplate:
    """Build the RAG chat prompt template with context and history."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )


def load_session_history(session_id: str) -> list:
    """
    Load conversation history for a session from Redis.

    Args:
        session_id: Unique session identifier.

    Returns:
        List of LangChain message objects (HumanMessage / AIMessage).
    """
    client = get_redis_client()
    key = f"{HISTORY_PREFIX}{session_id}"
    raw = client.get(key)

    if not raw:
        return []

    try:
        messages_data = json.loads(raw)
        messages = []
        for msg in messages_data[-settings.max_history_messages :]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        return messages
    except (json.JSONDecodeError, KeyError):
        return []


def save_message_to_history(session_id: str, role: str, content: str) -> None:
    """
    Append a message to the session's conversation history in Redis.

    Args:
        session_id: Unique session identifier.
        role: "user" or "assistant".
        content: Message text.
    """
    client = get_redis_client()
    key = f"{HISTORY_PREFIX}{session_id}"
    raw = client.get(key)

    try:
        messages = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        messages = []

    messages.append({"role": role, "content": content})

    # Keep only the last N messages to bound memory usage
    messages = messages[-settings.max_history_messages :]
    client.set(key, json.dumps(messages), ex=86400)  # TTL: 24h


def retrieve_context(question: str) -> tuple[list[dict], str]:
    """
    Embed the question and retrieve the most relevant chunks from Redis.

    Args:
        question: User's question text.

    Returns:
        Tuple of (raw results list, formatted context string).
    """
    query_vector = embed_query(question)
    results = search_similar_chunks(query_vector, top_k=settings.top_k_results)

    if not results:
        return [], "No relevant documents found."

    context_parts = [
        f"[Source: {r['source']}, Chunk #{r['chunk_index']}]\n{r['content']}"
        for r in results
    ]
    return results, "\n\n---\n\n".join(context_parts)


async def stream_rag_response(
    session_id: str, question: str
) -> AsyncGenerator[str, None]:
    """
    Execute the full RAG pipeline and stream the LLM response as SSE tokens.

    Yields JSON-encoded SSE events:
      - {"type": "token", "content": "..."}  — individual tokens
      - {"type": "sources", "data": [...]}    — source metadata (end of stream)
      - {"type": "done"}                       — stream termination signal

    Args:
        session_id: Chat session identifier.
        question: User's question.

    Yields:
        SSE-formatted strings.
    """
    # Step 1: Retrieve relevant context
    raw_results, context = retrieve_context(question)

    # Step 2: Load conversation history
    history = load_session_history(session_id)

    # Step 3: Save user message to history
    save_message_to_history(session_id, "user", question)

    # Step 4: Build the LCEL chain
    prompt = build_prompt()
    llm = get_llm(streaming=True)
    chain = prompt | llm | StrOutputParser()

    # Step 5: Stream tokens
    full_response = ""
    async for token in chain.astream(
        {"context": context, "history": history, "question": question}
    ):
        full_response += token
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    # Step 6: Save assistant response to history
    save_message_to_history(session_id, "assistant", full_response)

    # Step 7: Emit sources
    sources = [
        Source(
            content=r["content"],
            source=r["source"],
            chunk_index=r["chunk_index"],
        )
        for r in raw_results
    ]
    yield f"data: {json.dumps({'type': 'sources', 'data': [s.model_dump() for s in sources]})}\n\n"

    # Step 8: Signal stream end
    yield "data: {\"type\": \"done\"}\n\n"
