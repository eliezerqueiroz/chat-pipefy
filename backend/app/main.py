"""
FastAPI application factory.

Initializes the app, configures CORS, registers all routers,
and ensures the Redis vector index exists on startup.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, documents, health, upload
from app.services.vector_store import ensure_index_exists, get_redis_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Chat-Pipefy API",
        description="RAG-powered document chat API using Redis vector search and LangChain.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — allow frontend and local development origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(documents.router)
    app.include_router(chat.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        """Ensure Redis vector index exists on application startup."""
        logger.info("Starting Chat-Pipefy API (provider=%s, dim=%d)", settings.llm_provider, settings.embedding_dim)
        try:
            ensure_index_exists(get_redis_client())
            logger.info("Redis index ready.")
        except Exception as exc:
            logger.warning("Could not initialize Redis index on startup: %s", exc)

    return app


app = create_app()
