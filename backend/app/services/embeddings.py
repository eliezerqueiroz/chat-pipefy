"""
Embedding service.

Supports two providers, selected via the LLM_PROVIDER environment variable:
- "openai": OpenAI text-embedding-3-small (or configured model)
- "ollama": sentence-transformers/all-MiniLM-L6-v2 (local, free)
"""

import logging
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Return a cached embedding model instance based on LLM_PROVIDER setting.
    Uses lru_cache to avoid re-initializing on every call.
    """
    if settings.llm_provider == "ollama":
        logger.info("Using local SentenceTransformer embeddings (all-MiniLM-L6-v2)")
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    elif settings.llm_provider == "gemini":
        logger.info("Using Gemini text-embedding-004 embeddings")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            google_api_key=settings.gemini_api_key,
            model="models/text-embedding-004"
        )

    logger.info("Using OpenAI embeddings: %s", settings.embedding_model)
    from openai import OpenAI
    return OpenAI(api_key=settings.openai_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of float vectors (one per input text).
    """
    if not texts:
        return []

    model = get_embedding_model()

    if settings.llm_provider == "ollama":
        # SentenceTransformer returns numpy arrays; convert to Python lists.
        embeddings = model.encode(texts, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]
    elif settings.llm_provider == "gemini":
        # LangChain wrapper returns a list of float lists
        return model.embed_documents(texts)

    # OpenAI client
    response = model.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def embed_query(query: str) -> list[float]:
    """
    Embed a single query string.

    Args:
        query: The search query text.

    Returns:
        A single float vector.
    """
    if settings.llm_provider == "gemini":
        model = get_embedding_model()
        return model.embed_query(query)
        
    return embed_texts([query])[0]
