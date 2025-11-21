🏭 AutoFactoryScope

Machine-Learning–Powered Factory Layout Robot Detection System
C# WPF Frontend + Python ONNX Inference Backend

📌 Overview

AutoFactoryScope is an end-to-end system designed to automatically detect industrial robots on large-scale 2D factory layout images.

It combines:

YOLOv8-based object detection

ONNX-optimized inference backend (Python)

C# WPF desktop frontend

512×512 tile-based processing pipeline for large factory drawings

Automatic robot counting + bounding box rendering

This project enables engineers to rapidly analyze factory layouts, count robot instances, and visualize ML-detected results.

✨ Key Features
🔹 1. ML Detection Pipeline

Trained YOLO model (exported to ONNX)

512×512 tiling with overlap for high-resolution layouts

Detection stitching & post-processing

Non-maximum suppression (NMS)

One-step inference pipeline via /infer endpoint

🔹 2. Python Backend

REST API (FastAPI or Flask)

ONNX Runtime for high-performance inference

Preprocessing, tiling, merging, visualization

JSON and image output

🔹 3. C# WPF Frontend

Clean UI for selecting an image

Sends image to backend via HTTP

Displays annotated output image

Shows metadata and robot counts

🔹 4. Modular Project Structure

models/ for ONNX weights

notebooks/ for EDA, training artifacts

backend/ for API + inference

frontend/ for WPF application

scripts/ for dev tools

🧠 System Architecture
+------------------+
|    WPF Frontend  |
| (C#, .NET 8 WPF) |
+--------+---------+
         |
         | HTTP (POST multipart/form-data)
         v
+--------------------------+
|  Python Inference API    |
|  (FastAPI / Flask)       |
|    - Preprocess          |
|    - Tile (512x512)      |
|    - ONNX Inference      |
|    - Merge Detections    |
|    - Draw Boxes          |
+------------+-------------+
             |
             | PNG + JSON
             v
+--------------------------+
|  WPF Renders Result      |
+--------------------------+

🗂 Repository Structure
AutoFactoryScope/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .gitattributes
├─ .editorconfig
│
├─ .github/
│  ├─ workflows/            # Continuous Integration (C# backend, Python backend)
│  └─ ISSUE_TEMPLATE/
│     ├─ bug_report.md
│     └─ feature_request.md
│
├─ models/
│  ├─ robot_detector.onnx   # Exported YOLO model
│  └─ label_map.json
│
├─ notebooks/
│  ├─ 01_eda.ipynb
│  ├─ 02_training_experiments.ipynb
│  └─ 03_inference_tests.ipynb
│
├─ data/
│  ├─ samples/              # Example layout images
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

🚀 Getting Started
🔧 1. Install Backend (Python)

Python 3.10+ recommended

cd src/backend/autofactoryscope_api
pip install -r requirements.txt


Run the server:

uvicorn autofactoryscope_api.main:app --reload --host 0.0.0.0 --port 8000


The API is now available at:

http://localhost:8000/docs

🖥️ 2. Run the WPF Frontend

Open:

src/frontend/AutoFactoryScope.Desktop/AutoFactoryScope.Desktop.sln


Build and run.

Default API endpoint:

http://localhost:8000/infer/image

📤 Inference API
POST /infer

Returns detection metadata (JSON)

POST /infer/image

Returns annotated PNG/JPEG with bounding boxes.

Request:

Content-Type: multipart/form-data
Field: image (file)


Response:

Annotated image

Detection metadata (robot count, bounding boxes)

🧪 Machine Learning Notes
✔ Model

YOLOv8

Small architecture tuned for symbol-level detection

Trained via Google Colab

Hyperparameter tuning performed (model.tune())

✔ Dataset

Entire factory layout PNGs

Preprocessing into 512×512 tiles

Annotated using Roboflow

Custom deterministic train/val/test splitter

✔ ONNX Export

Used for optimized CPU inference in production.

🛠 Development Workflow
🔥 Branching Strategy
main      – protected, production-ready
develop   – staging branch for stable work
feature/* – individual contributor branches

💬 Pull Request Requirements

Code builds successfully

Linting passes

At least 1 approval

No direct commits to main

(If GitHub Team is not enabled, use the “Develop branch only” workflow.)

🔒 Security Practices

No force pushes to protected branches

Sensitive data (layout images from real factories) excluded

Notebook outputs sanitized before commit

ONNX model weights licensed internally

📅 Roadmap
Phase 1 (Current)

Backend inference pipeline

WPF integration

Core YOLO model

Phase 2

Add batch inference

Add robot-type classification

Add heatmap overlay mode (density map)

Phase 3

Multi-layout comparison

Integrate into enterprise workflow tools

Auto-report generation (PDF/Excel)

🤝 Contributing

Guidelines:

Feature branches only (feature/xyz)

PR required for all merges

Clean commit history (squash recommended)

Add tests for backend changes

Keep frontend code MVVM-aligned

📄 License

MIT License (or your chosen license)
