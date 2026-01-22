# Model Export Notes

## YOLOv8 to ONNX
To export the YOLOv8 model to ONNX format:

```python
from ultralytics import YOLO

model = YOLO("path/to/best.pt")
model.export(format="onnx", imgsz=640, dynamic=True)
```

## Optimization
- Use `half=True` for FP16 inference (if supported by hardware).
- Use `simplify=True` to optimize the ONNX graph.
