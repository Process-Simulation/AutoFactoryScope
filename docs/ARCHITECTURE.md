# Architecture Overview

This document provides a deeper technical overview of the AutoFactoryScope system architecture, data flow, and component interactions.

## System Components

### Backend (Python / FastAPI)

The backend is the core inference engine that processes factory layout images and returns robot detections.

**Key Modules:**

- **`main.py`**: FastAPI application entry point, defines HTTP endpoints
- **`config.py`**: Configuration management (model paths, tile size, NMS parameters)
- **`tiling.py`**: Image tiling logic - splits large layouts into 512×512 overlapping tiles
- **`inference.py`**: ONNX Runtime integration, loads YOLOv8 model, runs inference on tiles
- **`postprocess.py`**: Merges tile detections to global coordinates, applies Non-Maximum Suppression (NMS)
- **`visualize.py`**: Draws bounding boxes on original image, generates annotated output

### Frontend (TypeScript/React)

The React web application provides:

- Image upload interface with drag-and-drop support
- HTTP client (fetch/axios) to communicate with backend API
- Interactive display of detection results (counts, bounding boxes, annotated image)
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

### 1. Image Upload

The frontend sends a POST request to `/detect` (or similar endpoint) with:
- `multipart/form-data` containing the layout image file
- Optional parameters (confidence threshold, NMS IoU threshold)

### 2. Preprocessing & Tiling

The backend:
- Loads the image into memory
- Validates image format and dimensions
- Tiles the image into 512×512 regions with configurable overlap
- Maintains tile-to-global coordinate mapping

### 3. ONNX Inference

For each tile:
- Preprocesses tile to model input format (normalization, resizing if needed)
- Runs YOLOv8 ONNX inference
- Extracts bounding boxes, confidence scores, and class predictions

### 4. Post-Processing

- Merges detections from all tiles back to global layout coordinates
- Applies Non-Maximum Suppression (NMS) to remove duplicate detections
- Filters by confidence threshold
- Counts total robots detected

### 5. Visualization

- Draws bounding boxes on the original image
- Optionally labels boxes with confidence scores
- Generates annotated image (PNG/JPEG)

### 6. Response

Returns JSON response containing:
- `robot_count`: Total number of robots detected
- `detections`: Array of bounding boxes with coordinates, confidence, class
- `annotated_image`: Base64-encoded annotated image (or URL if stored)

## Data Flow Diagram

```
┌─────────────┐
│ Layout Image│
│  (PNG/JPEG) │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  FastAPI Endpoint   │
│  /detect            │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Tiling Module     │
│  Split into 512×512 │
│  tiles (overlapping)│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  ONNX Inference     │
│  YOLOv8 per tile    │
│  → detections       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Post-Processing    │
│  Merge coordinates  │
│  Apply NMS          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Visualization      │
│  Draw bboxes        │
│  Generate overlay   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  JSON Response      │
│  + Annotated Image  │
└─────────────────────┘
```

## Frontend Integration

The React frontend communicates with the backend via standard HTTP:

1. **Upload**: `fetch()` or `axios.post()` with `FormData` containing the image file
2. **Receive**: Parse JSON response, decode base64 image if needed, handle errors
3. **Display**: Render annotated image in `<img>` or canvas element, show statistics in React components
4. **State Management**: React hooks (useState, useEffect) or state management library for application state

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
- NMS IoU threshold: `NMS_IOU_THRESHOLD` (default: 0.5)
- Confidence threshold: `CONFIDENCE_THRESHOLD` (default: 0.25)
- Logging level: `LOG_LEVEL` (default: INFO)

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

