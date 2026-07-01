# Discovery

## Problem

Companies need a way to query their internal documents (PDFs, text files) using natural language. Reading and searching documents manually is time-consuming and error-prone.

## Objective

Build a full-stack conversational application (RAG) that allows users to upload documents and ask questions about them, receiving grounded, source-cited answers.

## Stakeholders

- **Primary user**: Business professional who needs to query document knowledge bases via chat.
- **Evaluator**: Pipefy Data & AI Team (assessing technical breadth across backend, AI, frontend, and infrastructure).

## Context

- Pipefy operates in 150+ countries with 4,000+ enterprise customers.
- The Data & AI team is expanding AI capabilities.
- This case simulates real day-to-day work: ingestion pipelines, reliable APIs, LLM integration, and end-to-end delivery.

## Constraints

- Delivery: 5 business days.
- Must run locally with a single `docker-compose up --build` command.
- No proprietary secrets committed to the repository.
- Must use: FastAPI, React, Redis Stack, LangChain, Docker Compose.

## Risks

| Risk | Mitigation |
|------|-----------|
| OpenAI API costs | Support open-source alternative (Sentence Transformers + Ollama) via env var |
| Redis index corruption | Health check + auto-recreate index on startup |
| Large file uploads blocking the API | Async ingestion with background tasks |
| LLM hallucination | RAG grounds answers; sources always cited |

## Definition of Success

- User can upload PDF, TXT, and DOCX files.
- User can ask questions and receive streamed, source-cited answers.
- All 5 API endpoints function correctly.
- Backend test coverage ≥ 60%.
- Project starts with a single command.
