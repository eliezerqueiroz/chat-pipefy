# ADR-0005

## Title

React + Vite + Tailwind CSS for Frontend

## Status

Approved

## Context

Need a frontend SPA for document upload, management, and RAG chat interface.

## Options Considered

- React CRA + CSS Modules
- React + Vite + Tailwind CSS
- Vue 3 + Vite
- Next.js (SSR)

## Decision

Use React 18 + Vite + Tailwind CSS v3 + Zustand.

## Justification

- **Vite**: Faster HMR than CRA, minimal config.
- **Tailwind CSS**: Utility-first styling enables rapid UI without fighting CSS specificity. Explicitly listed as option in case spec.
- **Zustand**: Minimal boilerplate for global state (sessions, documents); no Redux overhead needed.
- **TypeScript**: Type safety, better developer experience, aligns with engineering best practices.
- **EventSource API**: Browser-native SSE client for streaming responses.

## Consequences

- Nginx serves the static build inside the Docker container.
- Tailwind requires PostCSS configuration.
- Zustand must persist session list to localStorage for UX continuity.
