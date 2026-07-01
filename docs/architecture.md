# Architecture

## Overview

Three-tier containerized application:

```
User Browser
     │
     ▼
┌─────────────┐         ┌──────────────────┐         ┌──────────────┐
│  Frontend   │──HTTP──▶│     Backend      │──Redis──▶│ Redis Stack  │
│ React+Vite  │         │    FastAPI       │         │ (Vector DB)  │
│ Nginx:80    │         │ Uvicorn:8000     │         │ Port: 6379   │
└─────────────┘         └────────┬─────────┘         └──────────────┘
                                  │
                                  │──OpenAI API (external)──▶ Embeddings + LLM
```

## Components

### Frontend (React + Vite + Tailwind)
- **SPA** served by Nginx inside Docker.
- **Zustand** stores: `chatStore` (sessions, messages), `documentStore` (files).
- **Axios** API client with base URL from env.
- **EventSource** for SSE streaming.

### Backend (FastAPI)
- **Routers**: `health`, `upload`, `documents`, `chat`
- **Services**: `ingestion`, `embeddings`, `vector_store`, `rag`
- **Models**: Pydantic schemas for request/response validation
- **Background tasks**: File ingestion runs async (non-blocking upload endpoint)
- **CORS**: Configured for frontend origin

### Redis Stack
- Module: **RedisSearch** (RediSearch)
- Index name: `docs`
- Key pattern: `doc:{file_id}:chunk:{n}` (HASH type)
- Index type: HNSW, COSINE, FLOAT32, DIM=1536
- Separate hash `file:{file_id}` stores document metadata

## Data Model

### Redis HASH — `doc:{file_id}:chunk:{n}`
```
content       TEXT    Chunk text
embedding     BLOB    FLOAT32 vector (1536 dims)
source        TEXT    Original filename
file_id       TEXT    UUID of the file
chunk_index   NUM     Chunk sequence number
uploaded_at   TEXT    ISO 8601 timestamp
```

### Redis HASH — `file:{file_id}`
```
name          TEXT    Original filename
uploaded_at   TEXT    ISO 8601 timestamp
chunks        NUM     Total chunk count
```

## Data Flow

### Ingestion
```
File Upload → Parse (PyMuPDF/python-docx) → Split Chunks
  → Embed (OpenAI) → Store HASH in Redis → Update metadata
```

### RAG Chat
```
User Query → Embed query → KNN search Redis (top-5 chunks)
  → Build prompt [system + context + history + query]
  → Stream GPT-4o response via SSE → Return answer + sources
```

## APIs

See `spec.md` FR-01 through FR-05 for full contract.

## Integrations

| Service | Purpose | Auth |
|---------|---------|------|
| OpenAI | Embeddings + LLM | API Key (env var) |
| Redis Stack | Vector storage | Host + Port (env) |

## Diagrams

### Ingestion Sequence
```
Client      API         IngestionService    EmbeddingService    Redis
  │          │                │                    │              │
  │─POST /upload──────────────│                    │              │
  │          │─parse_file()──▶│                    │              │
  │          │                │─chunk_text()       │              │
  │          │                │─embed_chunks()────▶│              │
  │          │                │                    │─embed()──────│
  │          │                │◀───────────────────│              │
  │          │                │─store_vectors()──────────────────▶│
  │◀─200─────│                │                    │              │
```

### Chat RAG Sequence
```
Client    API        RAGService    EmbeddingService    Redis    OpenAI
  │        │              │               │              │         │
  │─POST /chat────────────│               │              │         │
  │        │─embed_query()│               │              │         │
  │        │              │─embed()──────▶│              │         │
  │        │              │◀──────────────│              │         │
  │        │              │─knn_search()────────────────▶│         │
  │        │              │◀────────────────────────────│         │
  │        │              │─stream_chat()─────────────────────────▶│
  │◀─SSE───│◀─────────────│◀──────────────────────────────────────│
```
