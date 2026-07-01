# Specification

## Context

RAG chat application for document Q&A. Users upload documents that are chunked, embedded, and stored in Redis. A chat interface lets users ask questions answered by a LangChain RAG pipeline.

## Objective

Deliver a containerized, full-stack RAG application with a functional chat UI, reliable API, and proper test coverage.

## Functional Requirements

### FR-01 — Document Upload
- Accepts PDF, TXT, DOCX files (max 20MB each).
- Chunks text into ~500 tokens with 50-token overlap.
- Generates embeddings and stores in Redis with metadata.
- Returns `{ file_id, chunks_indexed, status }`.

### FR-02 — Document Listing
- Lists all indexed documents with name, upload date, and chunk count.

### FR-03 — Document Deletion
- Removes a document and ALL its vector chunks from Redis.
- Returns `{ deleted: true }`.

### FR-04 — RAG Chat
- Embeds the user query.
- Performs KNN vector search (top-5) in Redis.
- Builds a grounded prompt and calls GPT-4o.
- Streams response via Server-Sent Events (SSE).
- Returns sources (chunk text + document name) with the answer.
- Maintains per-session conversation history (last 10 messages).

### FR-05 — Health Check
- Returns `{ status: "ok", redis: "connected" }`.

### FR-06 — Upload UI
- Drag-and-drop or file-selector interface.
- Upload progress bar.
- Status feedback (success / error).

### FR-07 — Document Manager UI
- Lists indexed documents.
- Delete button per document.

### FR-08 — Chat UI
- Message history (user + assistant bubbles).
- Streaming display (token-by-token).
- Sources drawer per assistant message.
- Multiple named chat sessions.
- Enter key to send.

## Non-Functional Requirements

- **NFR-01 Performance**: Chat first-token latency < 3s on local hardware.
- **NFR-02 Reliability**: API returns 4xx/5xx with structured error body.
- **NFR-03 Security**: No secrets in source code or Docker images. `.env` only.
- **NFR-04 Testability**: Backend test coverage ≥ 60% via pytest.
- **NFR-05 Portability**: Runs on any OS with Docker installed.

## Constraints

- Must use FastAPI, LangChain, Redis Stack, React, Docker Compose.
- Python 3.11+, Node 18+.
- No SSR (SPA only).

## Acceptance Criteria

1. `docker-compose up --build` starts all services successfully.
2. `POST /upload` with a PDF returns indexed chunk count.
3. `POST /chat` with a question returns a streamed, source-cited answer.
4. `DELETE /documents/{id}` removes all document vectors.
5. `GET /health` returns `{ status: "ok", redis: "connected" }`.
6. `make test` runs all tests with ≥ 60% coverage.

## Out of Scope

- User authentication / authorization.
- Multi-tenancy.
- Production deployment (infrastructure as code).
- Real-time collaboration.
