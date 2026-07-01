# ADR-0003

## Title

Redis Stack as Vector Store

## Status

Approved

## Context

Need a vector database to store and search document embeddings with low latency and support for metadata filtering.

## Options Considered

- Chroma (embedded)
- Pinecone (managed cloud)
- Weaviate (self-hosted)
- Redis Stack with RedisSearch (self-hosted)
- pgvector (PostgreSQL extension)

## Decision

Use Redis Stack (`redis/redis-stack:latest`) with RedisSearch module.

## Justification

- Case requirement explicitly mandates Redis Stack.
- RedisSearch HNSW index provides sub-millisecond KNN search.
- COSINE similarity metric aligns with text embedding space.
- Stores both vectors (BLOB) and metadata (TEXT/NUMERIC fields) in the same HASH.
- Single Docker image bundles Redis + RedisSearch + RedisJSON.
- redis-py client has native vector search support.

## Consequences

- Redis must persist to a Docker volume to survive container restarts.
- Index must be recreated on cold start if not already present.
- FLOAT32 vectors require explicit byte packing when storing.
