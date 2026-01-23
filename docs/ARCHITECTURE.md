# Architecture Overview

This document provides a deeper technical overview of the AutoFactoryScope system architecture, data flow, and component interactions.

## System Components

### Backend (Python / FastAPI)

The backend is the core inference engine that processes factory layout images and returns robot detections.

**Key Modules:**

- **`main.py`**: FastAPI application entry point, defines HTTP endpoints (including `/preview` and `/detect`)
- **`config.py`**: Configuration management (model paths, tile size, PDF/crop settings, NMS parameters)
- **`tiling.py`**: Image tiling logic - splits large layouts into configurable overlapping tiles (e.g., 512x512)
- **`inference.py`**: ONNX Runtime integration, loads YOLOv8 model, runs inference on tiles
- **`postprocess.py`**: Merges tile detections to global coordinates, applies Non-Maximum Suppression (NMS)
- **`visualize.py`**: Draws bounding boxes on original image, generates annotated output

### Frontend (TypeScript/React)

The React web application provides:

- Image/PDF upload interface
- Preview rendering and manual crop selection (single rectangle)
- HTTP client (fetch/axios) to communicate with backend API
- Interactive display of detection results (counts, bounding boxes, annotated image)
- Download of annotated image results as PNG
- Real-time progress indicators
- Responsive design for various screen sizes

**Architecture Note:** The frontend is intentionally decoupled from the backend. The backend exposes a standard REST API that any HTTP client can consume. This allows the web frontend to be extended, replaced, or integrated into existing tools without backend changes.

### ML Pipeline

Model training and export happens in Jupyter notebooks:

- **`01_eda.ipynb`**: Exploratory data analysis
- **`02_training_experiments.ipynb`**: YOLOv8 training and hyperparameter tuning
- **`03_inference_tests.ipynb`**: Model validation and ONNX export

The trained model is exported to `models/robot_detector.onnx` for production inference.

## Request Flow

### 1. Preview + Crop Selection

The frontend sends a POST request to `/preview` with:
- `multipart/form-data` containing the layout image or PDF file

The backend returns a rendered preview (`image_base64`, `image_width`, `image_height`).
The user draws a single rectangular crop; the UI stores normalized coordinates
(`x`, `y`, `width`, `height` in 0-1 space).

### 2. Detection Request

The frontend sends a POST request to `/detect` with:
- `multipart/form-data` containing the layout file
- `crop` JSON string with normalized coordinates
- Optional parameters (confidence threshold, NMS IoU threshold)
The web UI requires a crop selection; API clients may omit it if they handle cropping elsewhere.

### 3. PDF Conversion (if applicable)

If the uploaded file is a PDF (during `/detect`):
- Validate PDF format and file size
- Extract first page
- Render page to PIL Image at configured DPI (default: 600)
- Scale down render if estimated pixels exceed `PDF_MAX_PIXELS` (or Pillow safety limit)
- If a crop is provided, skip PDF auto-crop; otherwise optional auto-crop may run

If the uploaded file is an image:
- Load image directly to PIL Image

### 4. Crop Application (manual)

- Convert normalized crop to pixel coordinates
- Validate bounds and minimum size (`CROP_MIN_SIZE_PX`)
- Crop the image, then proceed to tiling

### 5. Preprocessing & Tiling

The backend:
- Loads the image into memory
- Validates image format and dimensions
- Tiles the image into regions (default 512x512) with configurable overlap
- Maintains tile-to-global coordinate mapping

### 6. ONNX Inference

For each tile:
- Preprocesses tile to model input format (normalization, resizing if needed)
- Runs YOLOv8 ONNX inference
- Extracts bounding boxes, confidence scores, and class predictions

### 7. Post-Processing

- Merges detections from all tiles back to global layout coordinates
- Applies Non-Maximum Suppression (NMS) to remove duplicate detections
- Filters by confidence threshold
- Counts total robots detected

### 8. Visualization

- Draws bounding boxes on the original image
- Optionally labels boxes with confidence scores
- Generates annotated image (PNG/JPEG)

### 9. Response

Returns JSON response containing:
- `robot_count`: Total number of robots detected
- `detections`: Array of bounding boxes with coordinates, confidence, class
- `annotated_image_base64`: Base64-encoded annotated image
- `image_width`, `image_height`: Final image dimensions after crop

## Data Flow Diagram

```
+---------------------------+
| Layout File (PNG/JPEG/PDF)|
+-------------+-------------+
              |
              v
+---------------------------+
| FastAPI /preview          |
| Render PDF page 1 if PDF  |
+-------------+-------------+
              |
              v
+---------------------------+
| User Crop Selection (UI)  |
| Normalized x,y,w,h        |
+-------------+-------------+
              |
              v
+---------------------------+
| FastAPI /detect           |
| file + crop JSON          |
+-------------+-------------+
              |
              v
+---------------------------+
| Render PDF (if needed)    |
| Apply manual crop         |
+-------------+-------------+
              |
              v
+---------------------------+
| Tiling Module (512x512)   |
+-------------+-------------+
              |
              v
+---------------------------+
| ONNX Inference (YOLOv8)   |
+-------------+-------------+
              |
              v
+---------------------------+
| Post-Processing (merge +  |
| NMS)                      |
+-------------+-------------+
              |
              v
+---------------------------+
| Visualization             |
+-------------+-------------+
              |
              v
+---------------------------+
| JSON Response + Annotated |
| Image (base64)            |
+---------------------------+
```

## Frontend Integration

The React frontend communicates with the backend via standard HTTP:

1. **Preview**: `fetch()` or `axios.post()` to `/preview` with `FormData` containing the file
2. **Crop**: User draws a rectangle; frontend stores normalized crop coordinates
3. **Detect**: POST `/detect` with `FormData` containing the file + `crop` JSON string
4. **Display**: Render annotated image in `<img>` or canvas element, show statistics in React components
5. **State Management**: React hooks (useState, useEffect) or state management library for application state

**Technology Stack:**
- React 18+ for UI components
- TypeScript for type safety
- Vite for build tooling and dev server
- Modern fetch API or axios for HTTP requests

The backend API is stateless and frontend-agnostic. Any client (web, mobile, desktop) can use the same endpoints.

## Model Management

- **Location**: `models/robot_detector.onnx` (relative to repository root)
- **Loading**: Backend loads model at startup via ONNX Runtime
- **Upgrade**: Replace model file and restart backend (no code changes needed)
- **Versioning**: Model version can be tracked via git tags or metadata files

## Configuration

Backend configuration (via `config.py` or environment variables):

- Model path: `MODEL_PATH` (default: `models/robot_detector.onnx`)
- Tile size: `TILE_SIZE` (default: 512)
- Tile overlap: `TILE_OVERLAP` (default: 0.1)
- IoU threshold: `IOU_THRESHOLD` (default: 0.45)
- Confidence threshold: `CONFIDENCE_THRESHOLD` (default: 0.5)
- PDF DPI: `PDF_DPI` (default: 600)
- PDF max pixels: `PDF_MAX_PIXELS` (default: None, capped by Pillow MAX_IMAGE_PIXELS)
- PDF auto-crop: `PDF_AUTO_CROP` (default: true)
- PDF crop threshold: `PDF_CROP_WHITE_THRESHOLD` (default: 245)
- PDF crop padding: `PDF_CROP_PADDING_PX` (default: 12)
- PDF min content ratio: `PDF_MIN_CONTENT_RATIO` (default: 0.02)
- Crop min size: `CROP_MIN_SIZE_PX` (default: 48)

## Scalability Considerations

- **Stateless backend**: Can be horizontally scaled behind a load balancer
- **Model caching**: ONNX Runtime loads model once per process
- **Async processing**: FastAPI supports async endpoints for concurrent requests
- **Future**: Batch processing endpoint for multiple layouts

## Future Architecture Evolution

The current web frontend can be extended with:

- **Enhanced UI/UX**: More interactive visualizations, zoom/pan for large images
- **Real-time Updates**: WebSocket support for long-running inference tasks
- **Authentication**: User authentication and authorization
- **Result Storage**: Caching and persistence layer for detection results
- **Batch Processing UI**: Interface for processing multiple layouts
- **Advanced Analytics**: Charts, statistics, and reporting features

The backend remains unchanged (REST API), allowing frontend evolution without backend modifications.


