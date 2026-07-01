# ADR-0001

## Title

FastAPI as Backend Framework

## Status

Approved

## Context

Need a Python HTTP API framework that supports async I/O, type safety, and streaming responses (SSE) for RAG chat.

## Options Considered

- Flask
- Django REST Framework
- FastAPI

## Decision

Use FastAPI with Uvicorn.

## Justification

- Native async/await support for non-blocking file processing and LLM calls.
- Pydantic-based request/response validation out of the box.
- Native OpenAPI/Swagger documentation.
- StreamingResponse support required for SSE streaming.
- Best performance among Python web frameworks (Starlette under the hood).

## Consequences

- Team must be familiar with Pydantic v2 model syntax.
- Dependency injection via FastAPI `Depends()`.
