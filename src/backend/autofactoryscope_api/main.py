import base64
import io
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

from autofactoryscope_api.config import settings
from autofactoryscope_api.inference import load_model, run_inference
from autofactoryscope_api.postprocess import apply_nms, merge_detections
from autofactoryscope_api.tiling import split_into_tiles
from autofactoryscope_api.visualize import annotate_image

app = FastAPI(title="AutoFactoryScope API")

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
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    return image


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
    }


@app.post("/detect", response_model=DetectResponse)
async def detect_robots(
    file: UploadFile = File(...),
    confidence_threshold: float = Query(None, ge=0.0, le=1.0),
    iou_threshold: float = Query(None, ge=0.0, le=1.0),
    tile_overlap: float = Query(None, ge=0.0, le=0.9),
):
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
    else:
        raise HTTPException(status_code=400, detail="Only image or PDF uploads are supported.")

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
