"""
Pydantic schemas for API request/response models.

Provides consistent, validated data structures for the API.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DetectionItem(BaseModel):
    """A single detection in the response."""

    bbox: tuple[float, float, float, float] = Field(
        ...,
        description="Bounding box as (x1, y1, x2, y2)",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence score",
    )
    class_name: str = Field(
        default="robot",
        description="Detected object class",
        alias="class",
    )

    model_config = ConfigDict(populate_by_name=True)


class DetectionResponse(BaseModel):
    """Response from the /detect endpoint."""

    request_id: str = Field(
        ...,
        description="Unique request identifier for tracing",
    )
    robot_count: int = Field(
        ...,
        ge=0,
        description="Total number of robots detected",
    )
    detections: list[DetectionItem] = Field(
        default_factory=list,
        description="List of individual detections",
    )
    annotated_image: str | None = Field(
        default=None,
        description="Base64-encoded annotated image (if requested)",
    )
    processing_time_ms: int = Field(
        ...,
        ge=0,
        description="Processing time in milliseconds",
    )
    image_size: tuple[int, int] = Field(
        ...,
        description="Original image dimensions (width, height)",
    )
    model_version: str = Field(
        default="0.1.0",
        description="Model version used for inference",
    )


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(
        ...,
        description="Error code for programmatic handling",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
    field: str | None = Field(
        default=None,
        description="Field that caused the error (if applicable)",
    )


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    request_id: str = Field(
        ...,
        description="Unique request identifier for tracing",
    )
    error: ErrorDetail = Field(
        ...,
        description="Error details",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp",
    )


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""

    status: str = Field(
        default="healthy",
        description="Overall health status",
    )
    version: str = Field(
        ...,
        description="API version",
    )
    model_loaded: bool = Field(
        ...,
        description="Whether the ML model is loaded",
    )
    uptime_seconds: float = Field(
        ...,
        ge=0,
        description="Server uptime in seconds",
    )
    checks: dict[str, bool] = Field(
        default_factory=dict,
        description="Individual health checks",
    )


class DetectionRunRecord(BaseModel):
    """Database record for a detection run."""

    id: UUID
    created_at: datetime
    image_filename: str
    image_width: int
    image_height: int
    model_version: str
    processing_time_ms: int
    robot_count: int
    artifact_path: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
