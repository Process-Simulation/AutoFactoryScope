# Detection Analysis - YOLOv11n Model Performance

## Model Training Metrics

### YOLOv11n (Current Active Model)

**Final Training Results (Epoch 37):**
- **Precision:** 68.4%
- **Recall:** 75.0% ← KEY METRIC
- **mAP@50:** 69.7%
- **mAP@50-95:** 41.5%

**What This Means:**
- Model finds **75% of real robots** (recall)
- Of the robots it detects, **68% are actually robots** (precision = 32% are false positives!)

### Expected vs Actual Performance

**On Validation Set (Training Data):**
- Precision: 68.4% → Expects ~32% false positives
- Recall: 75.0% → Misses ~25% of real robots

**On Your PDF (Real World):**
- Total detections: **26**
- Expected real robots: **23**
- False positives: **2 confirmed** (at 31% and 53% confidence)

**Analysis:**
- False positive rate: 2/26 = **7.7%** (much better than 32% on validation!)
- If 24 out of 26 are real (26-2 FP): **92.3% precision** (excellent!)
- Model is actually performing **MUCH BETTER** on this PDF than on validation data

## The Problem

Your images show 2 clear false positives:
1. **Text/legend area:** 31% confidence
2. **Hatched pattern:** 53% confidence

## Confidence Threshold Analysis

### Current Setting: 0.54

**Risk:** This threshold may be **TOO HIGH** and will lose real robots.

**Why?** Looking at detection distribution from Swagger:
- 1st detection: 66.9% ✓ (kept)
- 2nd detection: 61.7% ✓ (kept)
- ...
- False positive #2: 53% ✗ (filtered)
- ...
- False positive #1: 31% ✗ (filtered)

**Problem:** We don't know how many **real robots** are between 27-54% confidence!

## Solution Options

### Option 1: Test Current 0.54 Threshold
**Action:** Restart backend and test
**Expected:** May get fewer than 23 if real robots fall in 27-54% range
**Benefit:** Eliminates both false positives

### Option 2: Lower to 0.32 (Just Above First FP)
**Action:** Set `confidence_threshold: float = 0.32`
**Expected:** 25 detections (keeps 53% FP, filters 31% FP)
**Benefit:** Safer - less likely to lose real robots
**Drawback:** Still has 1 false positive

### Option 3: Manual Analysis Needed
**Action:** Get the full list of ALL 26 detections with confidences
**Then:** Find the gap between false positives and real robots
**Example:** If real robots are all >60%, and FPs are at 31% and 53%, set threshold to 0.60

## Recommended Next Steps

1. **First, test current 0.54 setting:**
   ```powershell
   # Stop backend (Ctrl+C)
   .\scripts\start_backend.ps1
   python test_annotated.py
   ```

2. **Count the results:**
   - If exactly 23: ✓ Perfect!
   - If less than 23: Lower threshold to 0.32
   - If still 26: Raise threshold to 0.60

3. **If results aren't 23, get full confidence list:**
   Run the test_thresholds.py script (fix Unicode issue first)
   This will show ALL 26 detections sorted by confidence
   Then manually identify which ones are false positives

## Model Training Quality Assessment

**YOLOv11n Model Quality: MODERATE**

Concerns:
- Recall of 75% means it misses 25% of robots on average
- Precision of 68% means 32% false positive rate on validation
- mAP@50 of 69.7% is decent but not excellent

**On your specific PDF, it's performing better than expected!**

## Alternative: Retrain Model

If we can't find a good threshold:
1. Add more training data (especially similar layouts)
2. Train for more epochs (current: 37, could go to 100)
3. Use data augmentation to reduce false positives
4. Consider YOLOv11m or YOLOv11s (larger, more accurate models)

---

**Current Status:**
- Model: YOLOv11n (11MB, 75% recall)
- Threshold: 0.54 (configured, not yet tested with restart)
- Expected: Unknown - need to test and see actual count
