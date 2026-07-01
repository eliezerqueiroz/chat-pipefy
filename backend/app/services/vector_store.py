"""
Vector store service (Redis Stack).

Responsibilities:
- Create and manage the Redis Search index (HNSW, COSINE).
- Store document chunks with their embeddings and metadata.
- Perform KNN vector similarity search.
- List and delete documents and their associated chunks.
"""

import json
import logging
import struct
from functools import lru_cache
from typing import Any

import redis
from redis.commands.search.field import NumericField, TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from app.config import settings
from app.models.document import DocumentInfo
from app.services.ingestion import DocumentChunk

logger = logging.getLogger(__name__)

INDEX_NAME = "docs"
DOC_PREFIX = "doc:"
FILE_PREFIX = "file:"


@lru_cache(maxsize=1)
def get_redis_client() -> redis.Redis:
    """Return a cached Redis client instance."""
    return redis.from_url(settings.redis_url, decode_responses=False)


def ensure_index_exists(client: redis.Redis) -> None:
    """
    Create the RedisSearch vector index if it does not already exist.

    Uses HNSW algorithm with COSINE distance metric.
    Index is created over keys prefixed with 'doc:'.
    """
    try:
        client.ft(INDEX_NAME).info()
        logger.debug("Redis index '%s' already exists.", INDEX_NAME)
    except redis.ResponseError:
        logger.info("Creating Redis index '%s'...", INDEX_NAME)
        schema = (
            TextField("content"),
            TextField("source"),
            TextField("file_id"),
            NumericField("chunk_index"),
            TextField("uploaded_at"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": settings.embedding_dim,
                    "DISTANCE_METRIC": "COSINE",
                    "INITIAL_CAP": 1000,
                },
            ),
        )
        client.ft(INDEX_NAME).create_index(
            schema,
            definition=IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH),
        )
        logger.info("Redis index '%s' created successfully.", INDEX_NAME)


def _floats_to_bytes(vector: list[float]) -> bytes:
    """Pack a list of floats into a FLOAT32 binary blob for Redis."""
    return struct.pack(f"{len(vector)}f", *vector)


def store_chunks(chunks: list[DocumentChunk], embeddings: list[list[float]]) -> int:
    """
    Store document chunks and their embeddings in Redis.

    Args:
        chunks: List of DocumentChunk objects.
        embeddings: Corresponding embedding vectors.

    Returns:
        Number of chunks stored.
    """
    client = get_redis_client()
    ensure_index_exists(client)

    pipe = client.pipeline(transaction=False)
    for chunk, embedding in zip(chunks, embeddings):
        key = f"{DOC_PREFIX}{chunk.file_id}:chunk:{chunk.chunk_index}"
        pipe.hset(
            key,
            mapping={
                "content": chunk.content.encode("utf-8"),
                "source": chunk.source.encode("utf-8"),
                "file_id": chunk.file_id.encode("utf-8"),
                "chunk_index": chunk.chunk_index,
                "uploaded_at": chunk.uploaded_at.encode("utf-8"),
                "embedding": _floats_to_bytes(embedding),
            },
        )

    # Store document-level metadata separately
    if chunks:
        file_key = f"{FILE_PREFIX}{chunks[0].file_id}"
        pipe.hset(
            file_key,
            mapping={
                "name": chunks[0].source.encode("utf-8"),
                "uploaded_at": chunks[0].uploaded_at.encode("utf-8"),
                "chunks": len(chunks),
                "file_id": chunks[0].file_id.encode("utf-8"),
            },
        )

    pipe.execute()
    logger.info("Stored %d chunks for file_id=%s", len(chunks), chunks[0].file_id if chunks else "N/A")
    return len(chunks)


def search_similar_chunks(query_embedding: list[float], top_k: int = None) -> list[dict[str, Any]]:
    """
    Perform KNN vector similarity search against the Redis index.

    Args:
        query_embedding: The embedded query vector.
        top_k: Number of results to return.

    Returns:
        List of dicts with 'content', 'source', and 'chunk_index' keys.
    """
    client = get_redis_client()
    top_k = top_k or settings.top_k_results
    query_bytes = _floats_to_bytes(query_embedding)

    knn_query = (
        Query(f"(*)=>[KNN {top_k} @embedding $vec AS vector_score]")
        .sort_by("vector_score")
        .return_fields("content", "source", "chunk_index", "vector_score")
        .dialect(2)
    )

    results = client.ft(INDEX_NAME).search(knn_query, query_params={"vec": query_bytes})

    return [
        {
            "content": doc.content.decode("utf-8") if isinstance(doc.content, bytes) else doc.content,
            "source": doc.source.decode("utf-8") if isinstance(doc.source, bytes) else doc.source,
            "chunk_index": int(doc.chunk_index),
        }
        for doc in results.docs
    ]


def list_documents() -> list[DocumentInfo]:
    """
    List all indexed documents from Redis metadata keys.

    Returns:
        List of DocumentInfo objects.
    """
    client = get_redis_client()
    pattern = f"{FILE_PREFIX}*"
    keys = client.keys(pattern)

    documents: list[DocumentInfo] = []
    for key in keys:
        data = client.hgetall(key)
        if not data:
            continue
        documents.append(
            DocumentInfo(
                file_id=_decode(data, b"file_id"),
                name=_decode(data, b"name"),
                uploaded_at=_decode(data, b"uploaded_at"),
                chunks=int(data.get(b"chunks", 0)),
            )
        )

    return sorted(documents, key=lambda d: d.uploaded_at, reverse=True)


def delete_document(file_id: str) -> bool:
    """
    Remove a document and all its vector chunks from Redis.

    Args:
        file_id: The document's unique identifier.

    Returns:
        True if the document existed and was deleted; False otherwise.
    """
    client = get_redis_client()

    # Find all chunk keys for this file
    chunk_pattern = f"{DOC_PREFIX}{file_id}:chunk:*"
    chunk_keys = client.keys(chunk_pattern)

    if not chunk_keys:
        logger.warning("No chunks found for file_id=%s", file_id)
        return False

    pipe = client.pipeline(transaction=False)
    for key in chunk_keys:
        pipe.delete(key)
    pipe.delete(f"{FILE_PREFIX}{file_id}")
    pipe.execute()

    logger.info("Deleted %d chunks for file_id=%s", len(chunk_keys), file_id)
    return True


def check_redis_connection() -> bool:
    """Ping Redis and return True if connected, False otherwise."""
    try:
        get_redis_client().ping()
        return True
    except Exception:
        return False


def _decode(data: dict, key: bytes) -> str:
    """Safely decode a bytes value from a Redis hash."""
    value = data.get(key, b"")
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)
