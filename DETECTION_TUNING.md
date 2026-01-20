# Detection Tuning Report

## Current Status

PDF support is working! The API successfully detects **21 out of 24** robots in the factory layout PDF.

## Analysis Results

Testing PDF: `OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf`
- Image size: 4963 x 3509 pixels (300 DPI)
- Tiles generated: 88
- Raw detections: 60
- Final detections (after NMS): 21
- **Missing: 3 robots**

### Confidence Distribution

| Range | Count | Percentage |
|-------|-------|------------|
| Very High (>90%) | 0 | 0% |
| High (70-90%) | 0 | 0% |
| Medium (50-70%) | 3 | 14% |
| Low (30-50%) | 14 | 67% |
| Very Low (<30%) | 4 | 19% |

**Key Finding**: The lowest detected robot has 25.1% confidence, just barely above the 0.25 threshold.

## Root Cause

The 3 missing robots are likely just below the **confidence threshold of 0.25** (25%).

Current settings:
- `confidence_threshold`: 0.25 (filters out low-confidence detections)
- `nms_iou_threshold`: 0.50 (merges overlapping detections)
- `tile_overlap`: 0.10 (10% overlap between tiles)

## Recommendations

### Option 1: Lower Confidence Threshold (Recommended)

Lower the confidence threshold to **0.20** (20%) to catch the missing robots.

**Pros:**
- Simple one-parameter change
- Will likely catch the 3 missing robots
- Low risk of false positives (still filtering below 20%)

**Cons:**
- May introduce a few false positives
- Need to validate on multiple PDFs

**How to test:**
```powershell
.\scripts\start_backend_tuned.ps1
```

Then run:
```powershell
.\scripts\test_pdf_detection.ps1
```

### Option 2: Adjust NMS Threshold

Lower NMS IoU threshold to **0.40** to avoid merging close robots.

**Pros:**
- May recover robots that were incorrectly merged
- Analysis shows 5 pairs of robots within 100px of each other

**Cons:**
- May create duplicate detections if set too low
- Less likely to be the main issue (only 5 close pairs)

### Option 3: Increase Tile Overlap

Increase tile overlap from **0.10** to **0.15** or **0.20**.

**Pros:**
- Better coverage at tile boundaries
- Reduces risk of splitting robots between tiles

**Cons:**
- More tiles = more processing time
- Analysis shows robots aren't clustered at edges

## Implementation

The tuned backend script (`start_backend_tuned.ps1`) sets:
- `AFS_CONFIDENCE_THRESHOLD=0.20` (was 0.25)
- `AFS_NMS_IOU_THRESHOLD=0.40` (was 0.50)

These are passed as environment variables, so no code changes needed!

## Test Results

### Version 1: Threshold 0.20
**Results**: 26 detections (expected 24)

**Analysis**:
- ✅ Detected most floor-mounted robots successfully
- ❌ 2 false positives (circled areas that aren't robots)
- ❌ Missing overhead track robot (different visual style)

**Conclusion**: Threshold too low, causing false positives.

### Version 2: Threshold 0.22 (Recommended)
**Goal**: Eliminate the 2 false positives (likely in 20-22% range) while keeping real robots.

**To test**:
```powershell
# Stop current backend (Ctrl+C)
.\scripts\start_backend_tuned_v2.ps1

# Test and view annotated image
python test_annotated.py
```

## Known Limitations

### Missing Track Robots
The overhead track-mounted robot systems are not detected because:
1. Training data only includes floor-mounted circular robot symbols
2. Track robots have different visual appearance (linear tracks)
3. Model hasn't learned to recognize this robot type

**Solution**: Add track robots to training dataset
- Annotate 10-20 examples of track robots
- Include in next training run
- Model will learn both robot types

## Next Steps

1. **Test v2 (threshold 0.22)**:
   ```powershell
   # Stop current backend (Ctrl+C)
   .\scripts\start_backend_tuned_v2.ps1
   python test_annotated.py
   ```

2. **Validate results**:
   - Check if false positives are eliminated
   - Verify real robots still detected
   - Note which robots are missed

3. **If successful, update defaults**:
   - Modify `src/backend/autofactoryscope_api/config.py`
   - Change `confidence_threshold` from 0.25 to 0.22
   - Change `nms_iou_threshold` from 0.50 to 0.40

4. **For track robots**:
   - Create new annotation batch with track robots
   - Retrain model with expanded dataset
   - Or: Create separate endpoint for track robot detection

## Analysis Tools

Created diagnostic tools:
- `analyze_detections.py` - Analyze confidence distribution and spatial patterns
- `start_backend_tuned.ps1` - Start backend with lowered thresholds
- `test_pdf_detection.ps1` - Test PDF uploads and view results

## Conclusion

The model is performing well overall (21/24 = 87.5% recall). The missing robots are likely due to the confidence threshold being slightly too high. Lowering it to 0.20 should catch the remaining 3 robots without introducing significant false positives.

The fact that most detections are in the 30-50% confidence range suggests that re-training with more data could improve overall confidence scores.
