# 🏭 AutoFactoryScope

**Intelligent Factory Layout Robot Detection System**\
**TypeScript/React Web Frontend + Python ONNX Runtime Backend + YOLOv8**

------------------------------------------------------------------------

## 🎯 Project Purpose

**AutoFactoryScope** is a machine‑learning powered tool that
automatically detects industrial robots in large‑scale factory layout
drawings.\
It is designed for manufacturing engineering, robotics planning, and
digital factory teams who work with CAD-based 2D layout drawings
(Body‑in‑White, Trim, Chassis, etc.)

The system brings together:

-   🧠 **YOLOv8 object detection**
-   ⚡ **Optimized ONNX inference pipeline**
-   🐍 **Python backend (FastAPI)**
-   🌐 **TypeScript/React web frontend**
-   🔁 **Scalable, frontend-agnostic architecture**

This README documents the full architecture, setup, and development
workflow.

------------------------------------------------------------------------

# 🚀 System Architecture

## High-Level Architecture Diagram 

    ┌─────────────────────────┐
    │   Web Frontend (React)  │
    │   TypeScript + Vite     │
    │  - Image Upload         │
    │  - Sends to API         │
    │  - Shows annotated image│
    │  - Interactive results  │
    └───────────────┬─────────┘
                    │ HTTP POST (multipart/form-data)
                    ▼
    ┌──────────────────────────────────────────┐
    │        Python Inference Backend          │
    │        FastAPI / ONNX Runtime            │
    │------------------------------------------│
    │ 1. Receive layout image                  │
    │ 2. Preprocess + Tile into 640×640        │
    │ 3. YOLOv8 ONNX Inference                 │
    │ 4. Merge tile detections                 │
    │ 5. Non-max suppression                   │
    │ 6. Draw bounding boxes                   │
    │ 7. Return JSON + Annotated image         │
    └───────────────────┬──────────────────────┘
                        │
                        ▼
    ┌──────────────────────────────────────────┐
    │          Output to User (Web)            │
    │  - Robot count                           │
    │  - Bounding box overlays                 │
    │  - Exported annotated layout             │
    └──────────────────────────────────────────┘

------------------------------------------------------------------------

# 🏛️ Repository Structure 

    AutoFactoryScope/
    ├─ README.md
    ├─ LICENSE
    ├─ .gitignore
    ├─ .gitattributes
    ├─ .editorconfig
    │
    ├─ .github/
    │  ├─ workflows/
    │  │  ├─ backend-ci.yml
    │  │  └─ frontend-ci.yml
    │  └─ ISSUE_TEMPLATE/
    │     ├─ bug_report.md
    │     └─ feature_request.md
    │
    ├─ models/
    │  ├─ robot_detector.onnx
    │  └─ label_map.json
    │
    ├─ notebooks/
    │  ├─ 01_eda.ipynb
    │  ├─ 02_training_experiments.ipynb
    │  └─ 03_inference_tests.ipynb
    │
    ├─ data/
    │  ├─ samples/
    │  │  ├─ layout_example_1.png
    │  │  └─ layout_example_2.png
    │  └─ README.md
    │
    ├─ src/
    │  ├─ backend/
    │  │  └─ autofactoryscope_api/
    │  │     ├─ main.py
    │  │     ├─ inference.py
    │  │     ├─ tiling.py
    │  │     ├─ postprocess.py
    │  │     ├─ visualize.py
    │  │     ├─ config.py
    │  │     └─ requirements.txt
    │  │
    │  └─ frontend/
    │     └─ autofactoryscope-web/
    │        ├─ src/
    │        ├─ public/
    │        ├─ package.json
    │        ├─ tsconfig.json
    │        ├─ vite.config.ts
    │        └─ index.html
    │
    └─ scripts/
       ├─ run_backend_dev.sh
       ├─ run_backend_dev.bat
       └─ export_model_notes.md

------------------------------------------------------------------------

# 🧠 ML Pipeline Summary

### Dataset

-   High‑resolution factory layouts\
-   Split into overlapping 512×512 tiles\
-   Annotated in Roboflow\
-   Custom deterministic splitter for consistent train/val/test sets

### Model

-   YOLOv8\
-   Tuned using `model.tune()`\
-   Exported to ONNX for inference speed

### Inference

-   Tiled prediction\
-   Post-merge of detections to global coordinates\
-   Final annotated image produced

------------------------------------------------------------------------

# 🐍 Backend Setup (Python / FastAPI)

### Prerequisites

- **Python 3.11** (recommended)
- Virtual environment support (venv)

### Install dependencies

``` bash
cd src/backend

# Create virtual environment if needed
python -m venv autofactoryscope_api/.venv

# Activate virtual environment
# Windows:
autofactoryscope_api\.venv\Scripts\activate
# Linux/macOS:
source autofactoryscope_api/.venv/bin/activate

# Install dependencies
pip install -r autofactoryscope_api/requirements.txt
```

### Model file

The ONNX model must be located at `models/robot_detector.onnx` (relative to repository root). The backend will load this model at startup. To upgrade the model, replace this file after retraining and exporting from your notebooks.

### Run API

``` bash
# Run from src/backend to support absolute imports
uvicorn autofactoryscope_api.main:app --reload --host 0.0.0.0 --port 8000
```

Open API docs at:\
http://localhost:8000/docs

------------------------------------------------------------------------

# 🌐 Frontend Setup (TypeScript/React)

### Prerequisites

- **Node.js 18+** and **npm** (or **yarn**/ **pnpm**)
- Modern web browser

### Install dependencies

``` bash
cd src/frontend/autofactoryscope-web

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Development server

``` bash
# Start development server
npm run dev
# or
yarn dev
# or
pnpm dev
```

The frontend will be available at `http://localhost:5173` (or the next available port).

### Build for production

``` bash
# Build for production
npm run build
# or
yarn build
# or
pnpm build
```

### Backend URL configuration

The frontend is configured to connect to the backend API at `http://localhost:8000` by default. Update the `VITE_API_URL` environment variable or configuration file if your backend runs on a different host or port.

### Technology Stack

- **React 18+** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Modern ES6+** - JavaScript features


### Supported Formats

- **Images**: PNG, JPEG, TIFF (standard formats supported by PIL)
- **Documents**: PDF (via PyMuPDF integration)

This ensures **AutoFactoryScope is future-proof and flexible**.

------------------------------------------------------------------------

# 🔁 Branching Strategy

    main       – production-ready
    develop    – integration branch
    feature/*  – per-task development
    hotfix/*   – urgent fixes into main

### Rules

-   **No direct commits to `main`**
-   All work flows through PRs → `develop` → `main`
-   Squash merges recommended
-   Feature branches named as:
    -   `feature/tiling-optimization`
    -   `feature/wpf-ui-upload`
    -   `feature/backend-nms`

------------------------------------------------------------------------

# 🔒 Security & DevOps Notes

### Recommended GitHub configuration

-   Protect `main`
-   Require PR review
-   Require CI checks once implemented
-   Restrict deletions & force pushes

### CI (planned)

-   Backend unit tests (pytest)
-   ONNX inference smoke test
-   Frontend build validation

------------------------------------------------------------------------

# 🗺️ Roadmap

### Phase 1 (Current)

-   Full ONNX inference backend\
-   TypeScript/React web frontend\
-   Initial CI

### Phase 2

-   Enhanced web dashboard features\
-   Multi-layout analysis\
-   Automatic report generation

### Phase 3

-   Robot type classification\
-   Symbol clustering\
-   Scalability for enterprise datasets

------------------------------------------------------------------------

# 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

------------------------------------------------------------------------
