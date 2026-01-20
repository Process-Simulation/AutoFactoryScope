# 🚀 TRAIN NOW - Your Dataset is Ready!

Your datasets are already unzipped in Google Drive. **You can start training immediately.**

---

## ✅ WHAT YOU HAVE

```
G:\My Drive\AutoFactoryScope/
├── robot_detection_layouts.v1-auto-factory-scope-dataset-v1.yolov8/
└── robot_detection_layouts.v2i.yolov8 (1)/  ← USE THIS (138 images)
    ├── data.yaml
    ├── train/images/
    ├── train/labels/
    ├── valid/images/
    ├── valid/labels/
    ├── test/images/
    └── test/labels/
```

---

## 🎯 3-STEP FAST TRACK

### Step 1: Upload Notebook to Drive (1 minute)

```powershell
# Copy optimized notebook to your Drive
Copy-Item "notebooks\01_train_yolo11_drive.ipynb" -Destination "G:\My Drive\AutoFactoryScope\"
```

---

### Step 2: Open in Colab (30 seconds)

1. Open [Google Drive](https://drive.google.com/drive/my-drive)
2. Navigate to `AutoFactoryScope/`
3. Right-click **`01_train_yolo11_drive.ipynb`**
4. Select: **Open with → Google Colaboratory**

---

### Step 3: Train! (60 minutes hands-off)

#### In Colab:

1. **Set GPU Runtime:**
   ```
   Runtime → Change runtime type → T4 GPU → Save
   ```

2. **Run All Cells:**
   ```
   Runtime → Run all (Ctrl+F9)
   ```

3. **Approve Drive Mount** when prompted

4. **Watch Training:**
   - Epoch 1/50... ✅
   - Epoch 25/50... ⏳
   - Epoch 50/50... 🎉
   - Training complete!

5. **Model Auto-Saves to Drive:**
   ```
   G:\My Drive\AutoFactoryScope\models\best.pt
   ```

---

## 📊 EXPECTED RESULTS

After 50 epochs (~60 minutes):

| Metric | Target |
|--------|--------|
| mAP50 | > 0.80 |
| Precision | > 0.85 |
| Recall | > 0.80 |

**If mAP50 < 0.70:** Increase epochs to 100 (edit cell before running)

---

## 💾 AFTER TRAINING: Export to ONNX

### Copy Model to Local Machine

```powershell
# Model is saved in Drive - copy to your local repo
Copy-Item "G:\My Drive\AutoFactoryScope\models\best.pt" -Destination "c:\Users\georgem\source\repos\AutoFactoryScope\models\best.pt"

# Verify
ls c:\Users\georgem\source\repos\AutoFactoryScope\models\best.pt
```

### Export to ONNX

```powershell
cd c:\Users\georgem\source\repos\AutoFactoryScope

# Activate backend venv
src\backend\autofactoryscope_api\.venv\Scripts\Activate.ps1

# Install ultralytics
pip install ultralytics

# Deactivate venv
deactivate

# Open export notebook
jupyter notebook notebooks\02_export_onnx.ipynb
```

**In Jupyter:**
- Run all cells
- Output: `models/robot_detector.onnx` ✅

---

## 🧪 TEST YOUR MODEL

### Start Backend

```powershell
cd c:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --reload
```

**Expected:**
```
INFO:     Model loaded successfully
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Start Frontend

```powershell
# New terminal
cd c:\Users\georgem\source\repos\AutoFactoryScope\src\frontend\autofactoryscope-web
npm run dev
```

### Test in Browser

1. Open [http://localhost:5173](http://localhost:5173)
2. Upload test image: `datasets\v2_roboflow_export\test\images\<any>.jpg`
3. See robot detections! 🎉

---

## 🔧 TROUBLESHOOTING

### "Colab can't find dataset"

**Check path in notebook cell:**
```python
source_path = '/content/drive/MyDrive/AutoFactoryScope/robot_detection_layouts.v2i.yolov8 (1)'
```

**If different, update to match your Drive structure:**
```python
# List your Drive to find exact path
!ls -la /content/drive/MyDrive/AutoFactoryScope/
```

### "Out of GPU memory"

**Reduce batch size in training cell:**
```python
batch=8,  # Changed from 16
```

### "Drive not mounted"

**Re-run mount cell and approve:**
```python
from google.colab import drive
drive.mount('/content/drive')
```

---

## ✅ YOUR MINIMAL CHECKLIST

```
[ ] 1. Copy notebook: Copy-Item notebooks\01_train_yolo11_drive.ipynb -Destination "G:\My Drive\AutoFactoryScope\"
[ ] 2. Open in Colab from Drive
[ ] 3. Set GPU runtime
[ ] 4. Run all cells
[ ] 5. Wait ~60 minutes
[ ] 6. Copy best.pt to local: Copy-Item "G:\My Drive\AutoFactoryScope\models\best.pt" -Destination models\best.pt
[ ] 7. Export to ONNX (notebook 02)
[ ] 8. Start backend + frontend
[ ] 9. Test detection!
```

---

## 🎉 SUCCESS CRITERIA

After completing this guide, you will have:

- ✅ Trained YOLO11 model (best.pt)
- ✅ ONNX production model (robot_detector.onnx)
- ✅ Working detection pipeline
- ✅ mAP50 > 0.80 (good accuracy)

**Total time:** ~70 minutes (mostly training)

---

## 🔜 NEXT: IMPROVE YOUR MODEL

Once basic detection works:

1. **Add more classes** (weld_gun, fixture, conveyor, gate)
2. **Collect more images** (target: 500+)
3. **Active learning** (prelabel → correct → retrain)
4. **Deploy as Windows service** (see docs/RUNBOOK.md)

---

**START NOW!** First command:

```powershell
Copy-Item "notebooks\01_train_yolo11_drive.ipynb" -Destination "G:\My Drive\AutoFactoryScope\"
```

Then open in Colab and click **Run all**! 🚀
