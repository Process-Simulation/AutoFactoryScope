"""
Middleware for production features.

Includes request ID injection, rate limiting, and error handling.
"""

import time
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings
from .logging_config import bind_request_id, clear_request_context, get_logger
from .schemas import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def create_limiter() -> Limiter:
    """Create and configure the rate limiter."""
    return Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        storage_uri="memory://",
    )


# Global limiter instance
limiter = create_limiter()


def get_rate_limit_string() -> str:
    """Get rate limit string from settings."""
    settings = get_settings()
    return f"{settings.rate_limit_requests}/{settings.rate_limit_window_seconds}second"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to inject request IDs into all requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state
        request.state.request_id = request_id

        # Bind to logging context
        bind_request_id(request_id)

        # Record start time
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log request completion
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        finally:
            clear_request_context()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error response formatting."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

            logger.exception(
                "unhandled_exception",
                error_type=type(e).__name__,
                error_message=str(e),
            )

            error_response = ErrorResponse(
                request_id=request_id,
                error=ErrorDetail(
                    code="INTERNAL_ERROR",
                    message="An unexpected error occurred",
                ),
                timestamp=datetime.utcnow(),
            )

            return JSONResponse(
                status_code=500,
                content=error_response.model_dump(mode="json"),
            )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    logger.warning(
        "rate_limit_exceeded",
        client_ip=get_remote_address(request),
        limit=str(exc.detail),
    )

    error_response = ErrorResponse(
        request_id=request_id,
        error=ErrorDetail(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded: {exc.detail}",
        ),
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=429,
        content=error_response.model_dump(mode="json"),
        headers={"Retry-After": "60"},
    )


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    settings = get_settings()

    # Add middlewares (order matters - last added is executed first)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Configure rate limiting
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    logger.info(
        "middleware_configured",
        rate_limiting=settings.rate_limit_enabled,
    )
