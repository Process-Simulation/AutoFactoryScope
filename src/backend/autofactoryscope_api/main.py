import base64
import io
import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

from autofactoryscope_api.config import settings
from autofactoryscope_api.inference import load_model, run_inference
from autofactoryscope_api.postprocess import apply_nms, merge_detections
from autofactoryscope_api.tiling import split_into_tiles
from autofactoryscope_api.visualize import annotate_image

app = FastAPI(title="AutoFactoryScope API")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_model_session = None
_label_map = None


class Detection(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    score: float
    class_id: int
    label: Optional[str] = None


class DetectResponse(BaseModel):
    robot_count: int
    detections: List[Detection]
    annotated_image_base64: str
    image_width: int
    image_height: int


class PreviewResponse(BaseModel):
    image_base64: str
    image_width: int
    image_height: int


def _load_pdf_page(pdf_bytes: bytes, dpi: int) -> Image.Image:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="PDF support requires PyMuPDF (pymupdf). Install backend requirements.",
        ) from exc

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid PDF file.") from exc

    if doc.page_count < 1:
        raise HTTPException(status_code=400, detail="PDF contains no pages.")

    page = doc.load_page(0)
    zoom = dpi / 72.0
    max_pixels = settings.PDF_MAX_PIXELS
    if max_pixels is None or max_pixels <= 0:
        max_pixels = Image.MAX_IMAGE_PIXELS or 0
    elif Image.MAX_IMAGE_PIXELS:
        max_pixels = min(max_pixels, Image.MAX_IMAGE_PIXELS)

    if max_pixels:
        for _ in range(2):
            est_width = int(page.rect.width * zoom)
            est_height = int(page.rect.height * zoom)
            est_pixels = est_width * est_height
            if est_pixels <= max_pixels:
                break
            scale = (max_pixels / est_pixels) ** 0.5
            zoom *= scale * 0.98
        if est_pixels > max_pixels:
            logger.warning(
                "PDF render scaled down to avoid oversized image (requested dpi=%s).",
                dpi,
            )

    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    return image


def _content_mask(image: Image.Image, white_threshold: int) -> Image.Image:
    threshold = max(0, min(255, white_threshold))
    gray = image.convert("L")
    return gray.point(lambda p: 255 if p < threshold else 0)


def _warn_if_low_pdf_content(image: Image.Image, mask: Optional[Image.Image] = None) -> None:
    if settings.PDF_MIN_CONTENT_RATIO <= 0:
        return

    if mask is None:
        mask = _content_mask(image, settings.PDF_CROP_WHITE_THRESHOLD)
    total_pixels = image.width * image.height
    if not total_pixels:
        return

    content_pixels = mask.histogram()[255]
    content_ratio = content_pixels / total_pixels
    if content_ratio < settings.PDF_MIN_CONTENT_RATIO:
        logger.warning(
            "PDF content ratio %.4f below threshold %.4f.",
            content_ratio,
            settings.PDF_MIN_CONTENT_RATIO,
        )


def _crop_pdf_to_content(image: Image.Image) -> Image.Image:
    mask = _content_mask(image, settings.PDF_CROP_WHITE_THRESHOLD)
    bbox = mask.getbbox()
    if not bbox:
        logger.warning("PDF content crop skipped; no non-white content detected.")
        return image

    _warn_if_low_pdf_content(image, mask=mask)

    padding = max(0, settings.PDF_CROP_PADDING_PX)
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    return image.crop((left, top, right, bottom))


def _maybe_save_pdf_render(image: Image.Image, original_name: str) -> None:
    debug_dir = settings.PDF_DEBUG_SAVE_DIR
    if not debug_dir:
        return

    output_dir = Path(debug_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(original_name).stem or "pdf_page"
    stem = re.sub(r"[^A-Za-z0-9_-]", "_", stem)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    token = uuid.uuid4().hex[:8]
    output_path = output_dir / f"{stem}_p0_{timestamp}_{token}.png"
    image.save(output_path, format="PNG")


def _parse_crop_payload(crop_payload: Optional[str]) -> Optional[dict]:
    if not crop_payload:
        return None

    try:
        data = json.loads(crop_payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Crop must be valid JSON.") from exc

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="Crop must be an object with x, y, width, height.",
        )

    required = ("x", "y", "width", "height")
    missing = [key for key in required if key not in data]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Crop missing fields: {', '.join(missing)}.",
        )

    try:
        crop = {key: float(data[key]) for key in required}
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Crop values must be numbers.") from exc

    return crop


def _apply_user_crop(image: Image.Image, crop: dict) -> Image.Image:
    x = crop["x"]
    y = crop["y"]
    width = crop["width"]
    height = crop["height"]

    epsilon = 1e-6
    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail="Crop width and height must be positive.")
    if x < 0 or y < 0:
        raise HTTPException(status_code=400, detail="Crop x and y must be non-negative.")
    if x + width > 1 + epsilon or y + height > 1 + epsilon:
        raise HTTPException(status_code=400, detail="Crop must be within image bounds.")

    x = max(0.0, min(x, 1.0))
    y = max(0.0, min(y, 1.0))
    width = min(width, 1.0 - x)
    height = min(height, 1.0 - y)

    left = int(round(x * image.width))
    top = int(round(y * image.height))
    right = int(round((x + width) * image.width))
    bottom = int(round((y + height) * image.height))

    if right <= left or bottom <= top:
        raise HTTPException(status_code=400, detail="Crop area is too small.")

    min_size = max(1, settings.CROP_MIN_SIZE_PX)
    if (right - left) < min_size or (bottom - top) < min_size:
        raise HTTPException(
            status_code=400,
            detail=f"Crop area must be at least {min_size}px on each side.",
        )

    return image.crop((left, top, right, bottom))


@app.on_event("startup")
def load_model_on_startup():
    global _model_session, _label_map
    _model_session, _label_map = load_model(settings.MODEL_PATH)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app_name": settings.APP_NAME}


@app.get("/config")
async def get_config():
    return {
        "model_path": settings.MODEL_PATH,
        "tile_size": settings.TILE_SIZE,
        "tile_overlap": settings.TILE_OVERLAP,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "iou_threshold": settings.IOU_THRESHOLD,
        "pdf_dpi": settings.PDF_DPI,
        "pdf_max_pixels": settings.PDF_MAX_PIXELS,
        "pdf_auto_crop": settings.PDF_AUTO_CROP,
        "pdf_crop_white_threshold": settings.PDF_CROP_WHITE_THRESHOLD,
        "pdf_crop_padding_px": settings.PDF_CROP_PADDING_PX,
        "pdf_min_content_ratio": settings.PDF_MIN_CONTENT_RATIO,
        "pdf_debug_save_dir": settings.PDF_DEBUG_SAVE_DIR,
        "crop_min_size_px": settings.CROP_MIN_SIZE_PX,
    }


@app.post("/preview", response_model=PreviewResponse)
async def preview_layout(file: UploadFile = File(...)):
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Missing content type.")

    content = await file.read()
    if file.content_type.startswith("image/"):
        try:
            image = Image.open(io.BytesIO(content)).convert("RGB")
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid image file.") from exc
    elif file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
        image = _load_pdf_page(content, settings.PDF_DPI)
        _warn_if_low_pdf_content(image)
    else:
        raise HTTPException(status_code=400, detail="Only image or PDF uploads are supported.")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    return PreviewResponse(
        image_base64=encoded,
        image_width=image.width,
        image_height=image.height,
    )


@app.post("/detect", response_model=DetectResponse)
async def detect_robots(
    file: UploadFile = File(...),
    crop: Optional[str] = Form(None),
    confidence_threshold: float = Query(None, ge=0.0, le=1.0),
    iou_threshold: float = Query(None, ge=0.0, le=1.0),
    tile_overlap: float = Query(None, ge=0.0, le=0.9),
):
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Missing content type.")

    crop_spec = _parse_crop_payload(crop)
    content = await file.read()
    pdf_source = False
    if file.content_type.startswith("image/"):
        try:
            image = Image.open(io.BytesIO(content)).convert("RGB")
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid image file.") from exc
    elif file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
        pdf_source = True
        image = _load_pdf_page(content, settings.PDF_DPI)
        if crop_spec is None and settings.PDF_AUTO_CROP:
            image = _crop_pdf_to_content(image)
        else:
            _warn_if_low_pdf_content(image)
    else:
        raise HTTPException(status_code=400, detail="Only image or PDF uploads are supported.")

    if crop_spec is not None:
        image = _apply_user_crop(image, crop_spec)
    if pdf_source:
        _maybe_save_pdf_render(image, file.filename or "upload.pdf")

    if _model_session is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")

    conf = confidence_threshold if confidence_threshold is not None else settings.CONFIDENCE_THRESHOLD
    iou = iou_threshold if iou_threshold is not None else settings.IOU_THRESHOLD
    overlap = tile_overlap if tile_overlap is not None else settings.TILE_OVERLAP

    tiles = split_into_tiles(image, tile_size=settings.TILE_SIZE, overlap=overlap)
    all_detections = []
    for tile in tiles:
        tile_dets = run_inference(_model_session, tile["image"], score_threshold=conf, label_map=_label_map)
        for det in tile_dets:
            det["tile_x"] = tile["x"]
            det["tile_y"] = tile["y"]
        all_detections.extend(tile_dets)

    merged = merge_detections(all_detections)
    final_detections = apply_nms(merged, iou_threshold=iou)

    annotated = annotate_image(image.copy(), final_detections)
    buffer = io.BytesIO()
    annotated.save(buffer, format="PNG")
    annotated_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")

    response_detections = [
        Detection(
            x1=det["bbox"][0],
            y1=det["bbox"][1],
            x2=det["bbox"][2],
            y2=det["bbox"][3],
            score=det["score"],
            class_id=det.get("class_id", 0),
            label=det.get("label"),
        )
        for det in final_detections
    ]

    return DetectResponse(
        robot_count=len(final_detections),
        detections=response_detections,
        annotated_image_base64=annotated_b64,
        image_width=image.width,
        image_height=image.height,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
