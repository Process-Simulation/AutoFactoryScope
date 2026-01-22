"""
ONNX Inference module for AutoFactoryScope.
Handles loading the model and running inference on image tiles.
"""

import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image


def load_model(model_path: str):
    """Loads the ONNX model and label map."""
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    label_map_path = Path(model_path).with_name("label_map.json")
    label_map = {}
    if label_map_path.exists():
        with label_map_path.open("r", encoding="utf-8") as handle:
            label_map = {int(k): v for k, v in json.load(handle).items()}
    return session, label_map

def _prepare_input(image_tile: Image.Image, input_width: int, input_height: int):
    image = image_tile.convert("RGB").resize((input_width, input_height))
    image_array = np.asarray(image).astype(np.float32) / 255.0
    image_array = np.transpose(image_array, (2, 0, 1))
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def _parse_output(outputs, input_width, input_height, score_threshold):
    output = outputs[0]
    if isinstance(output, (list, tuple)):
        output = output[0]
    data = np.squeeze(output)
    if data.ndim == 3:
        data = data[0]
    if data.shape[0] < data.shape[1]:
        data = data.T

    detections = []
    for row in data:
        if row.shape[0] < 5:
            continue
        x, y, w, h = row[0:4]
        scores = row[4:]
        if scores.size == 1:
            conf = float(scores[0])
            class_id = 0
        elif scores.size >= 2:
            if scores.size > 2 and scores[0] <= 1.0 and np.max(scores[1:]) <= 1.0:
                obj = scores[0]
                cls_scores = scores[1:]
                class_id = int(np.argmax(cls_scores))
                conf = float(obj * cls_scores[class_id])
            else:
                class_id = int(np.argmax(scores))
                conf = float(scores[class_id])
        else:
            continue

        if conf < score_threshold:
            continue

        x1 = x - w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2

        x1 = max(0.0, min(float(x1), float(input_width)))
        y1 = max(0.0, min(float(y1), float(input_height)))
        x2 = max(0.0, min(float(x2), float(input_width)))
        y2 = max(0.0, min(float(y2), float(input_height)))

        detections.append(
            {
                "bbox": [x1, y1, x2, y2],
                "score": conf,
                "class_id": class_id,
            }
        )
    return detections


def run_inference(session, image_tile, score_threshold=0.5, label_map=None):
    """Runs inference on a single tile and returns detections in tile space."""
    inputs = session.get_inputs()
    input_name = inputs[0].name
    input_shape = inputs[0].shape
    raw_height = input_shape[2] if len(input_shape) > 2 else None
    raw_width = input_shape[3] if len(input_shape) > 3 else None
    try:
        input_height = int(raw_height)
    except (TypeError, ValueError):
        input_height = image_tile.height
    try:
        input_width = int(raw_width)
    except (TypeError, ValueError):
        input_width = image_tile.width

    input_tensor = _prepare_input(image_tile, input_width, input_height)
    outputs = session.run(None, {input_name: input_tensor})
    detections = _parse_output(outputs, input_width, input_height, score_threshold)

    scale_x = image_tile.width / float(input_width)
    scale_y = image_tile.height / float(input_height)
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        det["bbox"] = [x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y]
        if label_map:
            det["label"] = label_map.get(det["class_id"])
    return detections
