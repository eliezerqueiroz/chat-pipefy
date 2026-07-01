# ADR-0004

## Title

OpenAI text-embedding-3-small for Embeddings and GPT-4o for LLM

## Status

Approved

## Context

Need embedding and generation models for the RAG pipeline. Must balance quality, cost, and latency.

## Options Considered

**Embeddings:**
- OpenAI text-embedding-ada-002 (legacy, 1536 dims)
- OpenAI text-embedding-3-small (1536 dims, cheaper, better)
- Sentence Transformers all-MiniLM-L6-v2 (384 dims, local, free)

**LLM:**
- OpenAI GPT-4o
- Anthropic Claude Sonnet 3.5
- Ollama + Llama3:8b (local, free)

## Decision

Default: `text-embedding-3-small` + `GPT-4o` via OpenAI API.

Fallback (open-source mode): `all-MiniLM-L6-v2` + `Ollama/llama3:8b` when `LLM_PROVIDER=ollama` env var is set.

## Justification

- `text-embedding-3-small` outperforms `ada-002` at lower cost.
- GPT-4o provides best answer quality with context adherence.
- Open-source fallback ensures zero-cost local operation for evaluation.
- `LLM_PROVIDER` env var makes switching seamless.

## Consequences

- Open-source mode requires Ollama running locally or in Docker.
- Embedding dimension differs between providers (1536 vs 384) — Redis index must be recreated when switching.
