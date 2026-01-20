# Model Licensing Decision Matrix

**Context**: AutoFactoryScope uses object detection models. License choice impacts future commercial use.

---

## Option Comparison

| Criteria | YOLO11 (Ultralytics) | RT-DETR (Baidu/PaddlePaddle) |
|----------|----------------------|------------------------------|
| **License** | AGPL-3.0 (free) / Commercial ($$$) | Apache 2.0 (permissive) |
| **Training Speed** | Fast (optimized for consumer GPUs) | Moderate |
| **Inference Speed** | Excellent (optimized for ONNX) | Good |
| **mAP (COCO)** | 53.9% (YOLO11n) | 53.0% (rtdetr_r18vd) |
| **OBB Support** | ✅ Yes (YOLO11-obb) | ❌ No (bbox only) |
| **Model Size** | 2.6 MB (nano), 9.4 MB (small) | 20 MB (r18), 42 MB (r50) |
| **Commercial Risk** | HIGH (AGPL copyleft) | LOW (Apache 2.0) |
| **Ecosystem** | Large (Ultralytics Hub, export tools) | Moderate (PaddleDetection) |
| **ONNX Export** | One-liner (`model.export()`) | Requires Paddle2ONNX |
| **Active Development** | Very active | Active |

---

## Decision Framework

### Scenario 1: Internal Use Only (No SaaS, No Distribution)

**✅ RECOMMENDED: YOLO11 (AGPL-3.0)**

**Why:**
- AGPL-3.0 is fine for internal tools (no copyleft trigger)
- Best performance/size ratio
- Easiest training + export workflow
- OBB support for angled symbols

**Action:**
- Train with `ultralytics` library
- Export to ONNX for production
- Keep source code private (no external deployment)

---

### Scenario 2: Future SaaS or API Service

**✅ RECOMMENDED: RT-DETR (Apache 2.0)**

**Why:**
- Apache 2.0 allows commercial use without licensing fees
- No copyleft restrictions on your API service
- Still modern transformer-based architecture

**Alternative:**
- Buy Ultralytics Enterprise license (~$1000+/year)

**Action:**
- Train with PaddleDetection
- Export via Paddle2ONNX
- Deploy freely in any environment

---

### Scenario 3: Open Source Project

**✅ RECOMMENDED: YOLO11 (AGPL-3.0)**

**Why:**
- License already requires open source
- Best tooling for community contributions

**Action:**
- Release under AGPL-3.0 or compatible license
- Use Ultralytics ecosystem fully

---

## Current Recommendation

**For AutoFactoryScope MVP: YOLO11 (AGPL-3.0)**

**Rationale:**
1. You're currently in internal testing phase
2. Best balance of speed, accuracy, and ease of use
3. OBB support is valuable for rotated symbols
4. Can always re-train RT-DETR later if commercialization happens

**License Compliance:**
- ✅ Keep code in private repo (OK under AGPL for internal use)
- ✅ Export to ONNX (model weights can be used under AGPL)
- ❌ Do NOT distribute the model or API externally without:
  - Releasing full source code under AGPL, OR
  - Purchasing Ultralytics Enterprise license

---

## Switching Models Later

If you decide to commercialize:

1. **Re-train on RT-DETR** using same dataset (~1-2 days work)
2. Export to ONNX (same inference pipeline)
3. Benchmark mAP difference (<2% expected)
4. Deploy under Apache 2.0

**Effort**: Low (inference code already model-agnostic via ONNX)

---

## References

- [Ultralytics Licensing](https://github.com/ultralytics/ultralytics/blob/main/LICENSE)
- [RT-DETR Paper](https://arxiv.org/abs/2304.08069)
- [PaddleDetection License](https://github.com/PaddlePaddle/PaddleDetection/blob/release/2.7/LICENSE)

---

**Decision Date**: 2026-01-20
**Chosen Model**: YOLO11 (AGPL-3.0)
**Review Trigger**: Before any external deployment or API launch
