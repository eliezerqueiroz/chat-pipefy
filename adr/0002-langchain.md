# ADR-0002

## Title

LangChain LCEL for RAG Orchestration

## Status

Approved

## Context

Need to orchestrate the RAG pipeline: query embedding → vector retrieval → prompt construction → LLM call → response streaming.

## Options Considered

- Manual pipeline (raw OpenAI + redis-py)
- LangChain (classic chains)
- LangChain LCEL (LangChain Expression Language)
- LlamaIndex

## Decision

Use LangChain LCEL with composable Runnables.

## Justification

- LCEL is the modern LangChain approach (replaces deprecated `RetrievalQA`).
- Composable, readable pipeline syntax with `|` operator.
- Native streaming support via `.astream()`.
- Well-maintained, case requirement explicitly mentions LangChain.
- `ConversationBufferWindowMemory` handles session history.

## Consequences

- LangChain is a heavy dependency; pin to a specific version.
- LCEL syntax learning curve for future maintainers.
