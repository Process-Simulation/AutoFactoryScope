# 🏭 AutoFactoryScope

**Intelligent Factory Layout Robot Detection System**\
**C# WPF (MVP) + Python ONNX Runtime Backend + YOLOv8**

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
-   🖥️ **C# WPF desktop client (MVP / temporary)**
-   🔁 **Scalable architecture that can migrate to a web frontend
    later**

This README documents the full architecture, setup, and development
workflow.

------------------------------------------------------------------------

# 🚀 System Architecture

## High-Level Architecture Diagram 

    ┌─────────────────────────┐
    │     Frontend (MVP)      │
    │    C# WPF Desktop App   │
    │  - Image Upload         │
    │  - Sends to API         │
    │  - Shows annotated image│
    └───────────────┬─────────┘
                    │ HTTP POST (multipart/form-data)
                    ▼
    ┌──────────────────────────────────────────┐
    │        Python Inference Backend          │
    │        FastAPI / ONNX Runtime            │
    │------------------------------------------│
    │ 1. Receive layout image                  │
    │ 2. Preprocess + Tile into 512×512        │
    │ 3. YOLOv8 ONNX Inference                 │
    │ 4. Merge tile detections                 │
    │ 5. Non-max suppression                   │
    │ 6. Draw bounding boxes                   │
    │ 7. Return JSON + Annotated image         │
    └───────────────────┬──────────────────────┘
                        │
                        ▼
    ┌──────────────────────────────────────────┐
    │          Output to User (WPF)            │
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
    │     └─ AutoFactoryScope.Desktop/
    │        ├─ App.xaml
    │        ├─ MainWindow.xaml
    │        ├─ ViewModels/
    │        ├─ Services/
    │        └─ Models/
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
cd src/backend/autofactoryscope_api

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Model file

The ONNX model must be located at `models/robot_detector.onnx` (relative to repository root). The backend will load this model at startup. To upgrade the model, replace this file after retraining and exporting from your notebooks.

### Run API

``` bash
# Ensure virtual environment is activated
uvicorn autofactoryscope_api.main:app --reload --host 0.0.0.0 --port 8000
```

Open API docs at:\
http://localhost:8000/docs

------------------------------------------------------------------------

# 🖥️ Frontend Setup (C# WPF MVP)

### Prerequisites

- **.NET 8 SDK** or later
- Visual Studio 2022 (recommended) or Visual Studio Code with C# extension
- Windows (WPF is Windows-only)

### Build and run

``` bash
cd src/frontend/AutoFactoryScope.Desktop

# Restore dependencies
dotnet restore

# Build (Debug)
dotnet build

# Run
dotnet run
```

### Backend URL configuration

The WPF client must be configured to connect to the backend API. By default, it expects the backend at `http://localhost:8000`. Update the backend URL in the application configuration or service settings if your backend runs on a different host or port.

### Why WPF?

-   Quickest path to a working MVP
-   Easier for local testing and debugging
-   Simple integration with backend via HttpClient

### Long-term note

> **WPF is a temporary MVP technology.**
>
> The architecture has been intentionally designed so the frontend can
> later be replaced with: - A web dashboard (React, Blazor, Vue) -
> Electron or MAUI - Integration into existing factory engineering tools

This ensures **AutoFactoryScope is future-proof**.

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
-   MVP WPF client\
-   Initial CI

### Phase 2

-   Web dashboard replacement for WPF\
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
