# 📍 File Locations Reference

**Quick reference for where everything is located.**

---

## 🗂️ YOUR DATASETS

### Google Drive (Ready for Colab)
```
G:\My Drive\AutoFactoryScope\
├── robot_detection_layouts.v1-auto-factory-scope-dataset-v1.yolov8/  (102 images)
└── robot_detection_layouts.v2i.yolov8 (1)/  ← USE THIS (138 images)
    ├── data.yaml
    ├── train/images/ + train/labels/
    ├── valid/images/ + valid/labels/
    └── test/images/ + test/labels/
```

### Local Repo (Git-Ignored Backup)
```
c:\Users\georgem\source\repos\AutoFactoryScope\datasets\
├── v1_roboflow_export/  (102 images)
└── v2_roboflow_export/  (138 images) ← Local backup
    └── data.yaml
```

---

## 📓 TRAINING NOTEBOOKS

### For Colab (Use This!)
```
Local:
c:\Users\georgem\source\repos\AutoFactoryScope\notebooks\01_train_yolo11_drive.ipynb

Copy to Drive:
G:\My Drive\AutoFactoryScope\01_train_yolo11_drive.ipynb

Then: Right-click → Open with → Google Colaboratory
```

### For ONNX Export (Local)
```
c:\Users\georgem\source\repos\AutoFactoryScope\notebooks\02_export_onnx.ipynb

Run with: jupyter notebook
```

---

## 🤖 MODELS

### After Training (Drive)
```
G:\My Drive\AutoFactoryScope\models\
├── best.pt   ← Trained PyTorch model
└── last.pt   ← Last checkpoint
```

### Copy to Local (For Production)
```
c:\Users\georgem\source\repos\AutoFactoryScope\models\
├── best.pt           ← Copy from Drive after training
└── robot_detector.onnx  ← Create with 02_export_onnx.ipynb
```

### Backend Expects (Check config.py)
```
c:\Users\georgem\source\repos\AutoFactoryScope\models\robot_detector.onnx
```

---

## 📚 DOCUMENTATION

```
c:\Users\georgem\source\repos\AutoFactoryScope\
├── QUICKSTART.md           ← General getting started
├── TRAIN_NOW.md           ← Use this! (Drive-specific)
├── FILE_LOCATIONS.md      ← This file
├── docs\
│   ├── IMPLEMENTATION_PLAN.md  ← Full roadmap
│   ├── LICENSING.md            ← Model license decision
│   ├── ANNOTATION_TOOLS.md     ← Label Studio guide
│   └── RUNBOOK.md              ← Production deployment
└── datasets\
    └── DATA_README.md          ← Dataset backup policy
```

---

## 🛠️ SCRIPTS

```
c:\Users\georgem\source\repos\AutoFactoryScope\scripts\
├── setup_env.ps1         ← Install dependencies (already ran ✅)
├── validate_setup.ps1    ← Health check (already ran ✅)
└── backup_dataset.ps1    ← 3-2-1 backup (run now!)
```

---

## 🖥️ BACKEND

### API Code
```
c:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api\
├── main.py           ← FastAPI entry point
├── inference.py      ← ONNX model wrapper
├── ocr.py           ← PaddleOCR integration (new!)
├── config.py        ← Settings (model path = models/robot_detector.onnx)
└── requirements.txt  ← Dependencies
```

### Start Backend
```powershell
cd c:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --reload
```

### API Endpoints
```
http://localhost:8000/docs       ← Swagger UI
http://localhost:8000/health     ← Health check
http://localhost:8000/detect     ← Upload & detect
http://localhost:8000/metrics    ← Prometheus
```

---

## 🎨 FRONTEND

### UI Code
```
c:\Users\georgem\source\repos\AutoFactoryScope\src\frontend\autofactoryscope-web\
├── src/
│   ├── App.tsx           ← Main React app
│   └── components/       ← UI components
└── package.json
```

### Start Frontend
```powershell
cd c:\Users\georgem\source\repos\AutoFactoryScope\src\frontend\autofactoryscope-web
npm run dev
```

### URL
```
http://localhost:5173
```

---

## 🔄 WORKFLOW PATHS

### Training Flow
```
1. Drive: G:\My Drive\AutoFactoryScope\robot_detection_layouts.v2i.yolov8 (1)/
   ↓ (Colab: 01_train_yolo11_drive.ipynb)
2. Drive: G:\My Drive\AutoFactoryScope\models\best.pt
   ↓ (Copy to local)
3. Local: c:\Users\georgem\source\repos\AutoFactoryScope\models\best.pt
   ↓ (Jupyter: 02_export_onnx.ipynb)
4. Local: c:\Users\georgem\source\repos\AutoFactoryScope\models\robot_detector.onnx
   ↓ (Backend loads automatically)
5. API: http://localhost:8000/detect
```

### Annotation Flow (Future)
```
1. New images → datasets/v3_unlabeled/
2. Label Studio → datasets/v3_labeled/
3. Retrain → models/best_v2.pt
4. Export → models/robot_detector_v2.onnx
5. Replace in backend
```

---

## 🎯 IMMEDIATE NEXT STEPS

### Command 1: Copy Notebook to Drive
```powershell
Copy-Item "c:\Users\georgem\source\repos\AutoFactoryScope\notebooks\01_train_yolo11_drive.ipynb" -Destination "G:\My Drive\AutoFactoryScope\"
```

### Command 2: Open in Colab
```
1. Go to: https://drive.google.com/drive/my-drive
2. Navigate to: AutoFactoryScope/
3. Right-click: 01_train_yolo11_drive.ipynb
4. Click: Open with → Google Colaboratory
```

### Command 3: Set GPU & Run
```
In Colab:
1. Runtime → Change runtime type → T4 GPU → Save
2. Runtime → Run all
3. Wait ~60 minutes
4. Model saves to: G:\My Drive\AutoFactoryScope\models\best.pt
```

---

## 📦 BACKUP LOCATIONS (3-2-1 Rule)

### Primary (Working Copy)
```
c:\Users\georgem\source\repos\AutoFactoryScope\datasets\
```

### Secondary (External Drive) - TO SET UP
```
E:\AutoFactoryScope_Backups\datasets\
(or your external drive letter)
```

### Tertiary (Cloud) - ALREADY HAVE IT!
```
G:\My Drive\AutoFactoryScope\  ← Your Google Drive is backup #3! ✅
```

---

## ✅ FILE CHECKLIST

```
Required for Training:
[✅] G:\My Drive\AutoFactoryScope\robot_detection_layouts.v2i.yolov8 (1)/
[✅] c:\Users\georgem\source\repos\AutoFactoryScope\notebooks\01_train_yolo11_drive.ipynb
[ ] G:\My Drive\AutoFactoryScope\01_train_yolo11_drive.ipynb  ← COPY NOW

Required for Production:
[ ] c:\Users\georgem\source\repos\AutoFactoryScope\models\best.pt  ← AFTER TRAINING
[ ] c:\Users\georgem\source\repos\AutoFactoryScope\models\robot_detector.onnx  ← AFTER EXPORT
[✅] c:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api\.venv\
[✅] c:\Users\georgem\source\repos\AutoFactoryScope\src\frontend\autofactoryscope-web\node_modules\
```

---

**Everything is ready!** Just copy the notebook to Drive and start training! 🚀
