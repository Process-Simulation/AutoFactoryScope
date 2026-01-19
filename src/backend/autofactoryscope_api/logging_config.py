"""
Structured logging configuration using structlog.

Provides JSON-formatted logs for production and readable console output for development.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from .config import get_settings


def add_app_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add application context to all log entries."""
    settings = get_settings()
    event_dict["app"] = settings.app_name
    event_dict["version"] = settings.app_version
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Shared processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        add_app_context,
    ]

    if settings.log_format == "json":
        # JSON format for production
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console format for development
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Set third-party loggers to WARNING
    for logger_name in ["uvicorn", "uvicorn.access", "httpx", "httpcore"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance with the given name."""
    return structlog.get_logger(name)


# Request ID context variable
_request_id_var: structlog.contextvars = structlog.contextvars


def bind_request_id(request_id: str) -> None:
    """Bind request ID to the current context."""
    structlog.contextvars.bind_contextvars(request_id=request_id)


def clear_request_context() -> None:
    """Clear request-specific context."""
    structlog.contextvars.clear_contextvars()
