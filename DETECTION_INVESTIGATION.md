# Detection Investigation - YOLOv11n vs Cole's YOLOv8s

**Date:** January 20, 2026
**Target:** Detect 23 floor-mounted robots in P708 OAKVILLE layout
**Test PDF:** `OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf`

## Summary

After extensive testing, neither model achieves perfect 23/23 detection:
- **YOLOv11n (11MB):** 22 detections (1 short)
- **Cole's YOLOv8s (43MB):** 25 detections (2 false positives)

## Test Results

### YOLOv11n Model (Your Original)

**Final Settings:**
- confidence_threshold: 0.18
- nms_iou_threshold: 0.15

**Performance:**
- Raw detections: 112
- Final detections: **22**
- Missing: 1 robot
- False positives: Minimal
- Processing time: ~3.3 seconds

**Analysis:**
- Model has 75% recall (from training metrics)
- Missing 1 robot likely has confidence <18%
- Very clean detection with minimal false positives
- Fast inference

### Cole's YOLOv8s Model

**Final Settings:**
- confidence_threshold: 0.20
- nms_iou_threshold: 0.15

**Performance:**
- Raw detections: 144
- Final detections: **19** (at threshold 0.20)
- At threshold 0.15: **25** (2 false positives)
- Processing time: ~4.6 seconds

**Analysis:**
- Trained for 120 epochs with hyperparameter tuning
- Produces more candidate detections (144 vs 112)
- More sensitive but also more false positives
- Slower inference (4.6s vs 3.3s)

**Question:** Cole reported 24 robots detected - need to investigate:
1. Different threshold settings used?
2. Different PDF or version?
3. Different NMS settings?
4. Different post-processing?

## Detection Breakdown

### Confidence Distribution (Cole's model @ 0.15)

| Range | Count | Notes |
|-------|-------|-------|
| ≥50% | 4 | High confidence |
| 40-50% | 7 | Medium-high |
| 30-40% | 1 | Medium |
| 20-30% | 7 | Lower confidence |
| 15-20% | 6 | Very low (likely includes FPs) |
| **Total** | **25** | 2 over target |

## Key Findings

### 1. NMS Impact

The tile overlap (0.1 = 10%) causes robots to be detected multiple times:

**Example (YOLOv11n @ conf 0.18):**
- Raw detections: 112
- After NMS (0.15): 22
- NMS removed: 90 duplicates

**NMS threshold effects:**
- 0.01 (nearly off): Keeps most duplicates → too many detections
- 0.10: Still some duplicates
- **0.15: Balanced** ← Current optimal
- 0.25: Starts merging close robots
- 0.40: Too aggressive, merges separate robots

### 2. Confidence Threshold Tuning

**False Positives Identified (from earlier testing):**
- 31% confidence: Text/legend area
- 53% confidence: Hatched pattern area

**YOLOv11n sweet spot:** 0.18-0.20
**Cole's model sweet spot:** 0.20-0.22 (produces lower confidence scores overall)

### 3. Model Architecture Differences

**YOLOv11n:**
- Newer architecture (2024)
- Smaller (11MB)
- Faster (3.3s)
- More conservative (fewer false positives)
- Lower recall (misses 1 robot)

**Cole's YOLOv8s:**
- Older but more trained (120 epochs)
- Larger (43MB)
- Slower (4.6s)
- More sensitive (finds more candidates)
- Higher false positive rate

## Investigation Needed

### Question: Why did Cole get 24 robots?

**Possible explanations:**

1. **Different thresholds:**
   - Cole may have used confidence 0.10 or lower
   - Cole may have used different NMS settings

2. **Different evaluation method:**
   - Cole's notebook uses count-based evaluation
   - May count differently (e.g., on tiles vs full image)

3. **Different input:**
   - Different PDF version
   - Different resolution/DPI

4. **Post-processing differences:**
   - Our NMS implementation vs Cole's
   - Tile merging strategy

### Next Steps to Investigate

1. **Review Cole's notebook:**
   ```
   AutoFactoryScope_data/20-11-2025__11-30/AutoFactoryScope.ipynb
   ```
   - Check exact inference code
   - Check threshold values used
   - Check how counts were calculated

2. **Test Cole's model with various thresholds:**
   - Try 0.10, 0.12, 0.15 confidence
   - See if we can hit exactly 24

3. **Compare evaluation methods:**
   - Check if Cole's "24" includes the track robot
   - Our target is 23 floor robots (24 total - 1 track)

4. **Validate ground truth:**
   - Manually count robots in PDF
   - Confirm 23 floor + 1 track = 24 total

## Current Configuration

**Active Model:** Cole's YOLOv8s (`robot_detector.onnx` = 43MB)

**Backup Models:**
- `robot_detector_yolov11n.onnx` (11MB)
- `robot_detector_yolov11n_backup.onnx` (11MB)
- `robot_detector_cole.onnx` (43MB original)

**Settings (`config.py`):**
```python
confidence_threshold: float = 0.20  # Cole's YOLOv8s
nms_iou_threshold: float = 0.15
```

## Recommendations

### Short Term

1. **Use YOLOv11n for production:**
   - Only 1 robot short (22/23)
   - Minimal false positives
   - Faster inference
   - Settings: conf=0.18, nms=0.15

2. **Investigate Cole's 24 count claim:**
   - Review his notebook thoroughly
   - Understand methodology difference

### Long Term

1. **Retrain model with more data:**
   - Add track robot examples
   - Add more floor robot variations
   - Target 100% recall

2. **Improve model quality:**
   - Current YOLOv11n has 75% recall (training metric)
   - Train longer or use larger model (YOLOv11m/s)
   - Add data augmentation

3. **Fine-tune for this specific layout type:**
   - Collect more Ford factory layouts
   - Specialized training on industrial PDFs

## Files Created

- `test_annotated.py` - Quick testing script
- `test_models_comparison.py` - Detailed comparison
- `find_false_positives.py` - FP analysis
- `test_thresholds.py` - Threshold sweeping
- `SOLUTION.md` - Model comparison summary
- `ANALYSIS.md` - Training metrics analysis
- `DETECTION_INVESTIGATION.md` - This document

## Conclusion

**Best we achieved:**
- YOLOv11n: 22/23 (95.7% recall)
- Cole's YOLOv8s: 19/23 clean or 25 with 2 FPs

Neither model achieves perfect 23/23 detection. Need to:
1. Understand Cole's methodology for claiming 24 detections
2. Consider if 22/23 (95.7%) is acceptable for production
3. Plan retraining to improve recall to 100%
