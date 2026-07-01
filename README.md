# Chat-Pipefy

> AI-powered document chat using RAG (Retrieval-Augmented Generation), Redis vector search, and LangChain — built as a technical case for Pipefy's Data & AI team.

## What it does

Upload PDF, TXT, or DOCX documents and ask questions about their content in natural language. Answers are grounded in the actual documents and include source citations, streamed token by token.

---

## Architecture

```
┌──────────────┐    HTTP    ┌──────────────┐    Redis    ┌──────────────┐
│   Frontend   │──────────▶│   Backend    │────────────▶│ Redis Stack  │
│ React + Vite │           │   FastAPI    │             │  (Vectors)   │
│   Port: 80   │           │  Port: 8000  │             │  Port: 6379  │
└──────────────┘           └──────┬───────┘             └──────────────┘
                                  │
                           ┌──────▼───────┐
                           │    Ollama    │
                           │  (llama3 +   │
                           │  embeddings) │
                           │ Port: 11434  │
                           └──────────────┘
```

**Stack:**
| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS + Zustand |
| Backend | Python 3.11 + FastAPI + LangChain LCEL |
| Vector store | Redis Stack (RedisSearch, HNSW, COSINE) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local) |
| LLM | Ollama + llama3 (local, no API key needed) |
| Infra | Docker Compose |
| CI | GitHub Actions |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/install/)
- At least **8 GB of RAM** (Ollama + llama3 requires ~5 GB)
- (Optional) OpenAI API key if you prefer cloud models

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/your-username/chat-pipefy.git
cd chat-pipefy

# Copy environment template
cp .env.example .env

# The defaults use Ollama (no API key needed)
# To use OpenAI instead, set LLM_PROVIDER=openai and add your OPENAI_API_KEY
```

### 2. Start all services

```bash
docker-compose up --build
```

This will:
- Start **Redis Stack** (vector database)
- Start **Ollama** and download the `llama3` model (~4 GB, first run only)
- Start the **FastAPI backend**
- Build and serve the **React frontend**

### 3. Pull the LLM model (first run)

After the containers are up, pull the Ollama model:

```bash
docker exec chat-pipefy-ollama ollama pull llama3
```

### 4. Open the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API docs (Swagger) | http://localhost:8000/docs |
| RedisInsight | http://localhost:8001 |

---

## Using OpenAI instead of Ollama

Edit your `.env` file:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-real-key
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o
EMBEDDING_DIM=1536
```

> **Note**: If you switch providers after indexing documents, recreate the Redis index (dimensions differ: 1536 vs 384). Run `docker-compose down -v` to reset volumes.

---

## Running Tests

```bash
# Install backend dependencies locally (or run inside Docker)
cd backend
pip install -r requirements.txt

# Run all tests with coverage
make test

# Generate HTML coverage report
make coverage
```

Coverage target: **≥ 60%** (enforced in CI).

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | API + Redis health check |
| `POST` | `/upload` | Upload and index a document |
| `GET` | `/documents` | List indexed documents |
| `DELETE` | `/documents/{id}` | Remove document and its vectors |
| `POST` | `/chat` | RAG chat with SSE streaming |

Full interactive documentation: http://localhost:8000/docs

---

## Project Structure

```
chat-pipefy/
├── .ai/                     # SDD Playbook reference
├── adr/                     # Architecture Decision Records (5 ADRs)
├── docs/                    # SDD artifacts: discovery, spec, planning, architecture
├── backend/
│   ├── app/
│   │   ├── config.py        # Pydantic Settings (all config from env)
│   │   ├── main.py          # FastAPI app factory
│   │   ├── routers/         # upload, documents, chat, health
│   │   ├── services/        # ingestion, embeddings, vector_store, rag
│   │   └── models/          # Pydantic request/response schemas
│   └── tests/               # pytest suite (≥60% coverage)
├── frontend/
│   └── src/
│       ├── components/      # ChatPanel, DocumentPanel, Layout
│       ├── store/           # Zustand: chatStore, documentStore
│       ├── api/             # Typed API client (Axios + fetch SSE)
│       └── types/           # Shared TypeScript interfaces
├── .github/workflows/ci.yml # GitHub Actions CI (pytest on push)
├── docker-compose.yml
├── .env.example
└── Makefile
```

---

## Differentiator Features

- **Streaming responses** — token-by-token SSE from the LLM
- **Multiple named sessions** — persistent chat sessions with localStorage
- **DOCX support** — PDF, TXT, and DOCX (python-docx)
- **Source citations** — every answer shows the exact document chunks used
- **Redis vector cleanup** — deleting a document removes all its embeddings
- **GitHub Actions CI** — automated pytest on every push

---

## Development

```bash
# Format + lint backend
make format
make lint

# Run backend in hot-reload mode (requires local Python env)
cd backend && uvicorn app.main:app --reload

# Run frontend in dev mode
cd frontend && npm install && npm run dev
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | `openai` or `ollama` |
| `OPENAI_API_KEY` | _(empty)_ | Required if `LLM_PROVIDER=openai` |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |
| `EMBEDDING_DIM` | `384` | Must match the embedding model output |
| `REDIS_URL` | `redis://redis:6379` | Redis connection string |
| `CHUNK_SIZE` | `500` | Characters per text chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Number of chunks retrieved per query |
| `MAX_HISTORY_MESSAGES` | `10` | Conversation turns kept in context |

See [`.env.example`](.env.example) for the full list.