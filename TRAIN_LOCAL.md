# 🚀 Train Locally (No Colab Needed!)

**Your Setup:**
- ✅ **GPU:** Quadro P4000 (8GB VRAM) - Perfect for training!
- ✅ **Dataset:** Already extracted in Downloads
- ✅ **Python:** 3.12 with venv ready

**No need for Colab or Google Drive!**

---

## ⚡ ONE COMMAND TO TRAIN

```powershell
.\scripts\train_local.ps1
```

**That's it!** This will:
1. ✅ Check your GPU (Quadro P4000)
2. ✅ Install Ultralytics YOLO11
3. ✅ Copy dataset from Downloads to repo
4. ✅ Fix data.yaml paths
5. ✅ Train for 50 epochs (~20-30 minutes on GPU)
6. ✅ Save best model to `models/best.pt`

---

## ⏱️ TIMELINE

| Time | What's Happening |
|------|------------------|
| **0:00** | Script starts |
| **0:01** | GPU detected: Quadro P4000 ✅ |
| **0:02** | Installing ultralytics (first time only) |
| **0:03** | Copying dataset from Downloads |
| **0:04** | Training starts: Epoch 1/50 |
| **⏳ 0:05-0:25** | Training in progress... |
| **0:25** | Epoch 50/50 complete! |
| **0:26** | Validation & model save ✅ |

**Total:** 20-30 minutes (much faster than Colab's 60 min!)

---

## 📊 WHAT YOU'LL SEE

### During Training:
```
Epoch 1/50 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 120/120 0:00:45
              Class     Images  Instances      Box(P          R      mAP50  mAP50-95)
              all        120        235      0.823      0.784      0.856      0.612

Epoch 2/50 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 120/120 0:00:43
...
```

### Final Output:
```
============================================================
TRAINING COMPLETE!
============================================================
mAP50:     0.873
mAP50-95:  0.621
Precision: 0.891
Recall:    0.847
============================================================

✓ Best model saved to: models\best.pt

Next steps:
  1. Run: .\scripts\export_onnx.ps1
  2. Run: .\scripts\start_backend.ps1
  3. Test your model!
```

---

## 🎯 AFTER TRAINING

### Step 1: Export to ONNX (2 minutes)
```powershell
.\scripts\export_onnx.ps1
```

### Step 2: Test System (2 minutes)
```powershell
# Terminal 1
.\scripts\start_backend.ps1

# Terminal 2 (new window)
.\scripts\start_frontend.ps1
```

### Step 3: See Detection! (30 seconds)
1. Open: [http://localhost:5173](http://localhost:5173)
2. Upload: `datasets\v2_roboflow_export\test\images\<any>.jpg`
3. **See robots detected with bounding boxes!** 🎉

---

## 🔧 ADVANTAGES OF LOCAL TRAINING

| Feature | Local (Your PC) | Colab Free |
|---------|-----------------|------------|
| **Training Time** | 20-30 min | 60 min |
| **GPU** | Quadro P4000 (dedicated) | T4 (shared) |
| **Session Limits** | None | 12 hours max |
| **Interruptions** | None | Can disconnect |
| **Network Required** | No | Yes (fast upload needed) |
| **Privacy** | 100% local | Data in cloud |

---

## 🚨 TROUBLESHOOTING

### "CUDA out of memory"
**Solution:** Reduce batch size

Edit `scripts\train_local.ps1`, find:
```python
batch=8,  # Change to 4
```

### "Dataset not found"
**Solution:** Verify path

```powershell
# Check if dataset exists
Test-Path "C:\Users\georgem\Downloads\robot_detection_layouts.v2i.yolov8 (1)"

# Should return: True
```

### "Ultralytics installation fails"
**Solution:** Update pip first

```powershell
cd src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install ultralytics torch torchvision
```

---

## 📈 EXPECTED RESULTS

With your Quadro P4000 + 138 training images:

| Metric | Target | Good |
|--------|--------|------|
| mAP50 | > 0.80 | > 0.85 |
| Training Time | 20-30 min | On your GPU |
| Model Size | ~5 MB | ONNX after export |

---

## ✅ COMPLETE WORKFLOW

```powershell
# 1. Train model (20-30 min)
.\scripts\train_local.ps1

# 2. Export to ONNX (2 min)
.\scripts\export_onnx.ps1

# 3. Start backend (Terminal 1)
.\scripts\start_backend.ps1

# 4. Start frontend (Terminal 2)
.\scripts\start_frontend.ps1

# 5. Test in browser
# http://localhost:5173
```

**Total time: ~35 minutes from start to working system!**

---

## 🎉 BENEFITS

- ✅ **Faster training** (GPU is all yours, not shared)
- ✅ **No network issues** (100% local)
- ✅ **No session limits** (train as long as needed)
- ✅ **Complete privacy** (data never leaves your PC)
- ✅ **Easier debugging** (can inspect files immediately)

---

## 🔜 AFTER FIRST MODEL WORKS

### Improve Accuracy:
1. **Add more images** (target: 500+)
2. **Add more classes** (weld_gun, fixture, conveyor, gate)
3. **Increase epochs** to 100
4. **Use YOLO11s** (small) instead of nano for better accuracy

### Production:
1. **INT8 quantization** (2x faster inference)
2. **Deploy as Windows service** (NSSM)
3. **Add OCR** for legend extraction

All documented in `docs/IMPLEMENTATION_PLAN.md`!

---

**START NOW!**

```powershell
.\scripts\train_local.ps1
```

Your model will be ready in ~25 minutes! 🚀
