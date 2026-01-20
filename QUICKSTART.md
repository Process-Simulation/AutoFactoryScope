# 🚀 AutoFactoryScope: Quick Start Guide

**Get from zero to trained model in 2 hours.**

---

## Prerequisites

- **Windows 10/11** (development machine)
- **Python 3.11** ([download](https://www.python.org/downloads/))
- **Node.js 20+** ([download](https://nodejs.org/))
- **Google Account** (for free Colab training)

---

## 🏃 FAST TRACK (Copy-Paste Ready)

### Step 1: Environment Setup (5 minutes)

```powershell
# Clone repo (if not already)
cd c:\Users\georgem\source\repos\AutoFactoryScope

# Run automated setup
.\scripts\setup_env.ps1

# Verify backend
cd src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
python -c "import onnxruntime; print('ONNX Runtime:', onnxruntime.__version__)"
```

**Expected Output:**
```
ONNX Runtime: 1.15.0 (or higher)
```

---

### Step 2: Dataset Backup (3 minutes)

```powershell
# Return to repo root
cd c:\Users\georgem\source\repos\AutoFactoryScope

# Backup datasets (3-2-1 rule)
.\scripts\backup_dataset.ps1

# Verify datasets exist
ls datasets\
```

**Expected Output:**
```
v1_roboflow_export/  (102 images)
v2_roboflow_export/  (138 images)
DATA_README.md
```

---

### Step 3: Compress Dataset for Colab (2 minutes)

```powershell
# Create ZIP for Google Colab upload
Compress-Archive -Path datasets\v2_roboflow_export -DestinationPath v2_dataset.zip

# Verify size (should be ~10-50 MB)
(Get-Item v2_dataset.zip).Length / 1MB
```

---

### Step 4: Upload to Google Drive (5 minutes)

1. Open [Google Drive](https://drive.google.com)
2. Create folder: **AutoFactoryScope**
3. Upload `v2_dataset.zip`
4. Create subfolder: **AutoFactoryScope/models** (for saving trained model)

---

### Step 5: Train Model in Colab (60 minutes)

1. **Open Colab Notebook:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Upload `notebooks/01_train_yolo11.ipynb`
   - **OR** directly: File → Upload Notebook → Browse

2. **Set Runtime to GPU:**
   - Runtime → Change runtime type → T4 GPU → Save

3. **Run All Cells:**
   - Runtime → Run all (Ctrl+F9)
   - **Approve Drive mount** when prompted
   - **Wait ~45-60 minutes** for 50 epochs

4. **Monitor Training:**
   - Watch loss curves in notebook outputs
   - Final mAP50 should be > 0.80

5. **Download Model:**
   - Model auto-saves to Drive: `AutoFactoryScope/models/best.pt`
   - **OR** download directly from Colab (last cell)

---

### Step 6: Export to ONNX (10 minutes)

**Option A: Local Export (if you have GPU)**

```powershell
cd c:\Users\georgem\source\repos\AutoFactoryScope

# Activate venv
src\backend\autofactoryscope_api\.venv\Scripts\Activate.ps1

# Install ultralytics
pip install ultralytics

# Run export notebook
jupyter notebook notebooks\02_export_onnx.ipynb

# Run all cells → robot_detector.onnx created in models/
```

**Option B: Colab Export (if no GPU)**

1. Upload `notebooks/02_export_onnx.ipynb` to Colab
2. Run all cells
3. Download `robot_detector.onnx` to `c:\Users\georgem\source\repos\AutoFactoryScope\models\`

---

### Step 7: Test Backend (5 minutes)

```powershell
# Start API server
cd c:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Model loaded. Input: images, Outputs: ['output0']
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test API:**

1. Open browser: [http://localhost:8000/docs](http://localhost:8000/docs)
2. Try `GET /health` → Should return `{"status": "healthy", "model_loaded": true}`
3. Try `POST /detect`:
   - Upload image: `datasets/v2_roboflow_export/test/images/<any_image>.jpg`
   - Click **Execute**
   - See detections in response!

---

### Step 8: Test Frontend (5 minutes)

**New Terminal:**

```powershell
cd c:\Users\georgem\source\repos\AutoFactoryScope\src\frontend\autofactoryscope-web
npm run dev
```

**Expected Output:**
```
VITE v6.x ready in 500 ms
➜  Local:   http://localhost:5173/
```

**Test UI:**

1. Open [http://localhost:5173](http://localhost:5173)
2. Upload factory layout image
3. See bounding boxes overlaid on image
4. View count summary

---

## 🎉 SUCCESS!

You now have:

- ✅ Trained YOLO11 model (robot detection)
- ✅ ONNX production model
- ✅ Running FastAPI backend
- ✅ React frontend
- ✅ End-to-end inference pipeline

---

## 🔜 NEXT STEPS

### Immediate (This Week)

1. **Improve Model:**
   - Add more training images (target: 500+)
   - Add more classes: `weld_gun`, `fixture`, `conveyor`, `gate`
   - See [docs/ANNOTATION_TOOLS.md](docs/ANNOTATION_TOOLS.md) for Label Studio setup

2. **Add OCR:**
   - Install PaddleOCR: `pip install paddleocr paddlepaddle`
   - Test [src/backend/autofactoryscope_api/ocr.py](src/backend/autofactoryscope_api/ocr.py)
   - Extract legend text from layouts

3. **Deploy as Service:**
   - See [docs/RUNBOOK.md](docs/RUNBOOK.md) for NSSM setup
   - Run API 24/7 on Windows

---

### Long-term (Next Month)

1. **Active Learning Loop:**
   - Run model on new layouts
   - Correct predictions in Label Studio
   - Retrain with expanded dataset
   - See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) Phase 6

2. **Performance Optimization:**
   - INT8 quantization (2x faster inference)
   - Parallel tile processing (4x faster on 4-core CPU)
   - See [docs/RUNBOOK.md](docs/RUNBOOK.md) Performance section

3. **Advanced Features:**
   - Context validation with Florence-2 VLM
   - Symbol-to-meaning mapping
   - Automatic legend parsing

---

## 🆘 TROUBLESHOOTING

### "Model not found" error

```powershell
# Check model path
ls c:\Users\georgem\source\repos\AutoFactoryScope\models\robot_detector.onnx

# If missing, re-run Step 6 (ONNX export)
```

### Training fails in Colab

- **Out of memory:** Reduce `batch=16` to `batch=8` in training cell
- **Drive not mounted:** Re-run Drive mount cell and approve
- **Slow training:** Verify GPU is enabled (Runtime → Change runtime type)

### API returns empty detections

- **Low confidence:** Model needs more training data
- **Wrong image format:** Ensure RGB (not RGBA or grayscale)
- **Tile size mismatch:** Check `AFS_TILE_SIZE=512` matches training `imgsz=512`

---

## 📚 DOCUMENTATION INDEX

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview |
| **[QUICKSTART.md](QUICKSTART.md)** | **This file** |
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Full roadmap |
| [docs/LICENSING.md](docs/LICENSING.md) | Model license decision |
| [docs/ANNOTATION_TOOLS.md](docs/ANNOTATION_TOOLS.md) | Label Studio setup |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Production deployment |
| [datasets/DATA_README.md](datasets/DATA_README.md) | Dataset policy |

---

**Total Setup Time:** ~90 minutes (excluding training wait time)

**Questions?** Check [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) support section.
