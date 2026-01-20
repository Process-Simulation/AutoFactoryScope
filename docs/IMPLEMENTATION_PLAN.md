# AutoFactoryScope: ML Production Pipeline Implementation Plan

**Status**: MVP Phase → Production Ready
**Last Updated**: 2026-01-20

---

## ✅ CURRENT STATE

### Infrastructure (Complete)
- [x] FastAPI backend with ONNX Runtime
- [x] Tiling pipeline (512x512, 10% overlap)
- [x] Global NMS for detection merging
- [x] TypeScript/React frontend
- [x] Prometheus metrics + structlog
- [x] 80% test coverage (pytest)

### Gaps Identified
- [ ] No trained model (`models/robot_detector.onnx` missing)
- [ ] No training pipeline
- [ ] No OCR integration
- [ ] No annotation workflow
- [ ] No dataset versioning
- [ ] No production deployment guide

---

## 🎯 IMPLEMENTATION PHASES

### PHASE 1: DATA SECURITY & TRAINING (TODAY - 2 hours) ✅

**Status**: IN PROGRESS

#### Completed
1. ✅ Add datasets/ to .gitignore
2. ✅ Extract v1 & v2 Roboflow datasets
3. ✅ Create DATA_README.md with backup policy
4. ✅ Create backup_dataset.ps1 script
5. ✅ Document licensing decision (YOLO11 AGPL-3.0)

#### In Progress
- [ ] Run backup script (`scripts\backup_dataset.ps1`)
- [ ] Upload dataset to Google Colab
- [ ] Train YOLO11 (50 epochs, ~1 hour)
- [ ] Download best.pt model

**Commands:**

```powershell
# 1. Backup dataset
.\scripts\backup_dataset.ps1

# 2. Compress for Colab upload
Compress-Archive -Path datasets\v2_roboflow_export -DestinationPath v2_dataset.zip

# 3. Upload to Google Drive manually

# 4. Open notebooks/01_train_yolo11.ipynb in Colab
# 5. Run all cells
# 6. Download best.pt to models/
```

---

### PHASE 2: MODEL DEPLOYMENT (THIS WEEK - 3 hours)

**Goal**: Get ONNX model running in production backend.

#### Tasks
1. [ ] Export ONNX (notebook: `02_export_onnx.ipynb`)
   - Input: `models/best.pt`
   - Output: `models/robot_detector.onnx`
2. [ ] Validate ONNX parity (<2% mAP difference)
3. [ ] Test inference with backend API
4. [ ] Create MODEL_CARD.md with metrics
5. [ ] Update frontend to display detections

**Commands:**

```powershell
# 1. Export ONNX (run notebook locally)
cd C:\Users\georgem\source\repos\AutoFactoryScope
jupyter notebook notebooks\02_export_onnx.ipynb

# 2. Test API with real model
cd src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --reload

# 3. Upload test image via Swagger UI
# http://localhost:8000/docs
# POST /detect
```

**Success Criteria:**
- ONNX model loads without errors
- Detections returned for test images
- Inference <100ms per 512x512 tile (CPU)

---

### PHASE 3: ANNOTATION WORKFLOW (THIS WEEK - 2 hours)

**Goal**: Set up Label Studio for active learning.

#### Tasks
1. [ ] Install Label Studio (no Docker)
2. [ ] Import v2 dataset
3. [ ] Configure labeling interface (5 classes)
4. [ ] Test annotation workflow
5. [ ] Document export process

**Commands:**

```powershell
# 1. Install Label Studio
python -m venv .labelstudio_env
.labelstudio_env\Scripts\Activate.ps1
pip install label-studio

# 2. Start server
label-studio start --port 8080

# 3. Browser: http://localhost:8080
# - Create project: "AutoFactoryScope Annotations"
# - Import images from datasets/v2_roboflow_export/train/images
# - Configure labels: robot, weld_gun, fixture, conveyor, gate
```

**Reference**: [docs/ANNOTATION_TOOLS.md](./ANNOTATION_TOOLS.md)

---

### PHASE 4: OCR INTEGRATION (NEXT WEEK - 4 hours)

**Goal**: Extract text from legends and title blocks.

#### Tasks
1. [ ] Add PaddleOCR to requirements.txt
2. [ ] Test ocr.py module
3. [ ] Add POST /detect/with_ocr endpoint
4. [ ] Extract legend regions (manual crop coords for now)
5. [ ] Return text annotations in response

**Example Usage:**

```python
# Backend endpoint (to implement)
from autofactoryscope_api.ocr import load_text_extractor

@app.post("/detect/with_ocr")
async def detect_with_ocr(file: UploadFile):
    # 1. Run object detection
    detections = model.predict(image)

    # 2. Extract text from legend (bottom-right 300x200px)
    ocr_engine = load_text_extractor()
    h, w = image.shape[:2]
    legend_crop = (w - 300, h - 200, w, h)
    text_results = ocr_engine.extract_from_crop(image, legend_crop)

    # 3. Return combined results
    return {
        "detections": detections,
        "legend_text": [r.text for r in text_results]
    }
```

**Dependencies:**

```txt
paddleocr>=2.7.0
paddlepaddle>=2.5.0  # CPU version
```

---

### PHASE 5: PRODUCTION DEPLOYMENT (NEXT WEEK - 2 hours)

**Goal**: Run API as Windows service.

#### Tasks
1. [ ] Download NSSM
2. [ ] Install AutoFactoryScope service
3. [ ] Configure logging to `C:\Logs\AutoFactoryScope\`
4. [ ] Test auto-restart on failure
5. [ ] Set up firewall rules (if exposing on LAN)

**Commands:**

```powershell
# See docs/RUNBOOK.md for full instructions

# Quick start:
nssm install AutoFactoryScope `
    "C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api\.venv\Scripts\python.exe" `
    "-m uvicorn autofactoryscope_api.main:app --host 0.0.0.0 --port 8000"

nssm start AutoFactoryScope
```

---

### PHASE 6: ACTIVE LEARNING (NEXT MONTH - Ongoing)

**Goal**: Improve model with production data.

#### Workflow
1. Deploy model to production
2. Collect factory layouts from real projects
3. Run inference → save predictions as pre-labels
4. Import to Label Studio
5. Human corrects detections (faster than labeling from scratch)
6. Export corrected labels to `datasets/v3_active_learning/`
7. Retrain model with expanded dataset
8. Re-export ONNX
9. Redeploy

**Script** (to create):

```python
# scripts/prelabel_with_model.py
# Run model on new images, export YOLO format for Label Studio import
```

---

## 📊 DECISION MATRIX SUMMARY

### Model Choice: YOLO11 (AGPL-3.0)

**Rationale:**
- Best accuracy/speed/size trade-off
- OBB support for rotated symbols
- Easiest training workflow (Ultralytics)
- Internal use only (AGPL OK)

**Risk Mitigation:**
- If commercializing → retrain RT-DETR (Apache 2.0)
- Inference code already model-agnostic (ONNX)

**Reference**: [docs/LICENSING.md](./LICENSING.md)

---

### Annotation Tool: Label Studio

**Rationale:**
- No Docker required (pip install)
- Modern web UI
- YOLO export built-in
- Pre-labeling support

**Reference**: [docs/ANNOTATION_TOOLS.md](./ANNOTATION_TOOLS.md)

---

### OCR Engine: PaddleOCR

**Rationale:**
- Free & open source (Apache 2.0)
- Works offline (no API calls)
- Good accuracy on technical drawings
- CPU-friendly

**Alternative**: docTR (if PaddleOCR too slow)

---

## 🚀 QUICK START GUIDE

### For New Developers

```powershell
# 1. Clone repo
git clone <your-repo-url>
cd AutoFactoryScope

# 2. Run setup script
.\scripts\setup_env.ps1

# 3. Download pre-trained model (once available)
# Place in models/robot_detector.onnx

# 4. Start backend
cd src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --reload

# 5. Start frontend (new terminal)
cd src\frontend\autofactoryscope-web
npm run dev

# 6. Open browser
# http://localhost:5173
```

---

## 📈 SUCCESS METRICS

### Training Phase
- [ ] mAP50 > 0.85 (target for single-class robot detection)
- [ ] Inference speed < 100ms per tile (512x512, CPU)
- [ ] Model size < 10 MB (ONNX)

### Production Phase
- [ ] API uptime > 99% (monitored via /health)
- [ ] Average detection latency < 2s for 5000x5000px layouts
- [ ] Zero data leaks (no uploads to public services)

### Active Learning Phase
- [ ] Annotation speed: 2x faster with pre-labels vs from scratch
- [ ] mAP improvement: +5% with each iteration

---

## 🔗 REFERENCE LINKS

### Documentation
- [README.md](../README.md) - Project overview
- [LICENSING.md](./LICENSING.md) - Model license decision
- [ANNOTATION_TOOLS.md](./ANNOTATION_TOOLS.md) - Label Studio setup
- [RUNBOOK.md](./RUNBOOK.md) - Production deployment
- [DATA_README.md](../datasets/DATA_README.md) - Dataset policy

### Notebooks
- [01_train_yolo11.ipynb](../notebooks/01_train_yolo11.ipynb) - Training pipeline
- [02_export_onnx.ipynb](../notebooks/02_export_onnx.ipynb) - ONNX export

### Scripts
- [setup_env.ps1](../scripts/setup_env.ps1) - Environment setup
- [backup_dataset.ps1](../scripts/backup_dataset.ps1) - Dataset backup

### External
- [Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/)
- [Label Studio Docs](https://labelstud.io/guide/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

---

## 🆘 SUPPORT

### Troubleshooting
1. Check [docs/RUNBOOK.md](./RUNBOOK.md) troubleshooting section
2. Review logs: `C:\Logs\AutoFactoryScope\`
3. Validate dataset with `data.yaml`
4. Test ONNX model parity (notebook 02)

### Getting Help
- GitHub Issues: [autofactoryscope/issues](https://github.com/your-org/AutoFactoryScope/issues)
- Internal Wiki: (add link if available)

---

**Next Immediate Action**: Run `.\scripts\backup_dataset.ps1` and start Colab training!
