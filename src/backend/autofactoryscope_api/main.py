"""
FastAPI application entry point.

Defines HTTP endpoints for robot detection API.
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

import numpy as np
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from . import __version__
from .config import get_settings
from .inference import get_model, load_model
from .logging_config import get_logger, setup_logging
from .middleware import limiter, setup_middleware
from .postprocess import nms
from .schemas import DetectionItem, DetectionResponse, ErrorDetail, ErrorResponse, HealthResponse
from .tiling import tile_image
from .visualize import create_annotated_image

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "afs_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "afs_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
)
DETECTIONS_COUNT = Counter(
    "afs_detections_total",
    "Total number of robots detected",
)

# Track startup time for uptime calculation
_startup_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _startup_time
    _startup_time = time.time()

    settings = get_settings()
    logger.info(
        "application_starting",
        version=__version__,
        debug=settings.debug,
    )

    # Pre-load model if it exists
    try:
        model_path = settings.get_model_path()
        if model_path.exists():
            load_model(model_path)
            logger.info("model_loaded", path=str(model_path))
        else:
            logger.warning("model_not_found", path=str(model_path))
    except Exception as e:
        logger.error("model_load_failed", error=str(e))

    yield

    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title="AutoFactoryScope API",
    description="Intelligent Factory Layout Robot Detection System",
    version=__version__,
    lifespan=lifespan,
)

# Setup CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current health status of the API including
    model loading status and uptime.
    """
    model = get_model()

    checks = {
        "model_loaded": model.is_loaded,
        "config_valid": True,
    }

    # Check if model file exists even if not loaded
    try:
        model_path = settings.get_model_path()
        checks["model_file_exists"] = model_path.exists()
    except Exception:
        checks["model_file_exists"] = False

    return HealthResponse(
        status="healthy" if all(checks.values()) else "degraded",
        version=__version__,
        model_loaded=model.is_loaded,
        uptime_seconds=round(time.time() - _startup_time, 2),
        checks=checks,
    )


@app.get("/metrics", tags=["System"])
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.
    """
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.post(
    "/detect",
    response_model=DetectionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal error"},
    },
    tags=["Detection"],
)
@limiter.limit("30/minute")
async def detect_robots(
    request: Request,
    file: Annotated[UploadFile, File(description="Factory layout image")],
    include_annotated: bool = True,
) -> DetectionResponse:
    """
    Detect robots in a factory layout image.

    Processes the uploaded image through the YOLOv8 detection pipeline:
    1. Tiles the image into overlapping 512x512 regions
    2. Runs inference on each tile
    3. Merges detections and applies NMS
    4. Returns detection results and optionally an annotated image

    Args:
        file: The factory layout image (PNG, JPEG, etc.)
        include_annotated: Whether to include base64-encoded annotated image

    Returns:
        Detection results including robot count and bounding boxes
    """
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = time.perf_counter()

    # Track request
    REQUEST_COUNT.labels(method="POST", endpoint="/detect", status="started").inc()

    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    request_id=request_id,
                    error=ErrorDetail(
                        code="INVALID_FILE_TYPE",
                        message=f"Expected image file, got {file.content_type}",
                        field="file",
                    ),
                ).model_dump(mode="json"),
            )

        # Read and decode image
        contents = await file.read()
        if len(contents) == 0:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    request_id=request_id,
                    error=ErrorDetail(
                        code="EMPTY_FILE",
                        message="Uploaded file is empty",
                        field="file",
                    ),
                ).model_dump(mode="json"),
            )

        try:
            from io import BytesIO

            image = Image.open(BytesIO(contents))
            image_array = np.array(image)
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    request_id=request_id,
                    error=ErrorDetail(
                        code="INVALID_IMAGE",
                        message=f"Could not decode image: {e}",
                        field="file",
                    ),
                ).model_dump(mode="json"),
            )

        logger.info(
            "processing_image",
            filename=file.filename,
            size=len(contents),
            dimensions=f"{image.width}x{image.height}",
        )

        # Get model
        model = get_model()
        if not model.is_loaded:
            try:
                model.load()
            except FileNotFoundError:
                return JSONResponse(
                    status_code=500,
                    content=ErrorResponse(
                        request_id=request_id,
                        error=ErrorDetail(
                            code="MODEL_NOT_FOUND",
                            message="Detection model not available",
                        ),
                    ).model_dump(mode="json"),
                )

        # Tile the image
        settings = get_settings()
        tiling_result = tile_image(
            image_array,
            tile_size=settings.tile_size,
            overlap=settings.tile_overlap,
        )

        logger.info(
            "image_tiled",
            tile_count=len(tiling_result.tiles),
            tile_size=settings.tile_size,
        )

        # Run inference on tiles
        all_detections = model.predict_tiles(tiling_result)

        # Apply NMS
        final_detections = nms(all_detections, iou_threshold=settings.nms_iou_threshold)

        # Track detections
        DETECTIONS_COUNT.inc(len(final_detections))

        logger.info(
            "detection_complete",
            raw_detections=len(all_detections),
            final_detections=len(final_detections),
        )

        # Create annotated image if requested
        annotated_b64: str | None = None
        if include_annotated and final_detections:
            _, annotated_b64 = create_annotated_image(image, final_detections)

        # Calculate processing time
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Track latency
        REQUEST_LATENCY.labels(method="POST", endpoint="/detect").observe(
            processing_time_ms / 1000
        )
        REQUEST_COUNT.labels(method="POST", endpoint="/detect", status="success").inc()

        return DetectionResponse(
            request_id=request_id,
            robot_count=len(final_detections),
            detections=[
                DetectionItem(
                    bbox=d.bbox,
                    confidence=d.confidence,
                    class_name=d.class_name,
                )
                for d in final_detections
            ],
            annotated_image=annotated_b64,
            processing_time_ms=processing_time_ms,
            image_size=(image.width, image.height),
            model_version=__version__,
        )

    except Exception as e:
        REQUEST_COUNT.labels(method="POST", endpoint="/detect", status="error").inc()
        logger.exception("detection_failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                request_id=request_id,
                error=ErrorDetail(
                    code="DETECTION_FAILED",
                    message="Detection processing failed",
                ),
            ).model_dump(mode="json"),
        )


@app.get("/", tags=["System"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "AutoFactoryScope API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
