"""Health check router."""

from fastapi import APIRouter

from app.models.chat import HealthResponse
from app.services.vector_store import check_redis_connection

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Check API and Redis connectivity.

    Returns:
        { status: "ok", redis: "connected" } on success.
        { status: "degraded", redis: "disconnected" } if Redis is unreachable.
    """
    redis_ok = check_redis_connection()
    return HealthResponse(
        status="ok" if redis_ok else "degraded",
        redis="connected" if redis_ok else "disconnected",
    )
