# 🏭 AutoFactoryScope

**Intelligent Factory Layout Robot Detection System**
**TypeScript/React (Vite) + Python (FastAPI/ONNX)**

------------------------------------------------------------------------

## 🎯 Project Purpose

**AutoFactoryScope** applies computer vision to detect industrial robots in large-scale factory layout drawings.
It uses a tiled inference approach to handle high-resolution CAD exports (50k+ pixels wide).

## 🚀 Quick Start

### Backend (Python 3.11+)

```bash
cd src/backend/autofactoryscope_api

# Install dependencies
pip install -r requirements.txt

# Run server (logs to console in dev mode)
uvicorn autofactoryscope_api.main:app --reload
```

- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Health: http://localhost:8000/health

### Frontend (Node.js 20+)

```bash
cd src/frontend/autofactoryscope-web

# Install dependencies (updated to React 19 + Vite 6)
npm install

# Run dev server
npm run dev
```

- App: http://localhost:5173

------------------------------------------------------------------------

## 🧪 Testing

### Backend Tests

We use `pytest` with 80% coverage enforcement.

```bash
cd src/backend/autofactoryscope_api
pytest --cov=autofactoryscope_api --cov-report=term-missing
```

### Frontend Tests

We use `vitest` + `testing-library`.

```bash
cd src/frontend/autofactoryscope-web
npm run test           # Watch mode
npm run test:coverage  # Coverage report
```

------------------------------------------------------------------------

## 🏗️ Architecture

### Backend (Production Ready)
- **Framework**: FastAPI
- **Inference**: ONNX Runtime (YOLOv8)
- **Tiling**: Custom sliding window with 50% overlap support
- **Post-processing**: Global coordinate merge + NMS
- **Observability**: Structlog (JSON), Prometheus metrics, Request IDs
- **Resilience**: Rate limiting (slowapi), Global error handling

### Frontend (Modernized)
- **Core**: React 19, TypeScript 5.9
- **Build**: Vite 6
- **Styling**: TailwindCSS 3.4
- **State**: Zustand
- **Testing**: Vitest

------------------------------------------------------------------------

## 🔌 API Summary

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/detect` | Upload image, returns robot count + annotations |
| `GET` | `/health` | System health, model status, uptime |
| `GET` | `/metrics` | Prometheus metrics scrape target |

---
*Created by GeorgeM*
