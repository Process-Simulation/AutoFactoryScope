"""
ONNX Runtime inference module for YOLOv8 robot detection.

Handles model loading, preprocessing, inference execution, and output parsing.
"""

import logging
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from .postprocess import Detection
from .tiling import Tile, TilingResult, tile_bbox_to_global

logger = logging.getLogger(__name__)


class InferenceSession(Protocol):
    """Protocol for ONNX Runtime inference session."""

    def run(
        self,
        output_names: list[str] | None,
        input_feed: dict[str, NDArray],
    ) -> list[NDArray]: ...

    def get_inputs(self) -> list: ...

    def get_outputs(self) -> list: ...


class ModelWrapper:
    """
    Wrapper for ONNX YOLOv8 model inference.

    Handles preprocessing, inference, and output parsing.
    """

    def __init__(
        self,
        model_path: Path | str,
        confidence_threshold: float = 0.25,
        input_size: int = 512,
    ):
        """
        Initialize the model wrapper.

        Args:
            model_path: Path to the ONNX model file
            confidence_threshold: Minimum confidence for detections
            input_size: Expected input size for the model
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.input_size = input_size
        self._session: InferenceSession | None = None
        self._input_name: str = ""
        self._output_names: list[str] = []

    def load(self) -> None:
        """Load the ONNX model."""
        try:
            import onnxruntime as ort

            logger.info("Loading model from %s", self.model_path)

            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")

            self._session = ort.InferenceSession(
                str(self.model_path),
                providers=["CPUExecutionProvider"],
            )

            inputs = self._session.get_inputs()
            outputs = self._session.get_outputs()

            self._input_name = inputs[0].name
            self._output_names = [o.name for o in outputs]

            logger.info(
                "Model loaded. Input: %s, Outputs: %s",
                self._input_name,
                self._output_names,
            )

        except ImportError as e:
            logger.error("ONNX Runtime not available: %s", e)
            raise RuntimeError("ONNX Runtime is required for inference") from e

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._session is not None

    def preprocess(self, image: NDArray[np.uint8]) -> NDArray[np.float32]:
        """
        Preprocess image for YOLOv8 inference.

        Args:
            image: Input image as (H, W, C) uint8 array

        Returns:
            Preprocessed tensor as (1, 3, H, W) float32 array
        """
        # Ensure 3 channels
        if image.ndim == 2:
            image = np.stack([image] * 3, axis=-1)
        elif image.shape[2] == 4:
            image = image[:, :, :3]

        # Resize if needed
        h, w = image.shape[:2]
        if h != self.input_size or w != self.input_size:
            pil_img = Image.fromarray(image)
            pil_img = pil_img.resize(
                (self.input_size, self.input_size),
                Image.Resampling.BILINEAR,
            )
            image = np.array(pil_img)

        # Normalize to [0, 1] and transpose to (C, H, W)
        tensor = image.astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))

        # Add batch dimension
        tensor = np.expand_dims(tensor, axis=0)

        return tensor

    def postprocess(
        self,
        outputs: list[NDArray],
        scale_x: float = 1.0,
        scale_y: float = 1.0,
    ) -> list[Detection]:
        """
        Parse YOLOv8 output tensor into Detection objects.

        Args:
            outputs: Raw model outputs
            scale_x: X scale factor for coordinate adjustment
            scale_y: Y scale factor for coordinate adjustment

        Returns:
            List of Detection objects
        """
        # YOLOv8 output shape: (1, num_classes + 4, num_predictions)
        # Format: [x_center, y_center, width, height, class_scores...]
        output = outputs[0]

        if output.ndim == 3:
            output = output[0]  # Remove batch dimension

        # Transpose if needed (predictions should be columns)
        if output.shape[0] < output.shape[1]:
            output = output.T

        detections: list[Detection] = []

        for pred in output:
            # First 4 values are bbox (x_center, y_center, w, h)
            x_center, y_center, w, h = pred[:4]

            # Remaining values are class scores
            class_scores = pred[4:]
            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])

            if confidence < self.confidence_threshold:
                continue

            # Convert from center format to corner format
            x1 = (x_center - w / 2) * scale_x
            y1 = (y_center - h / 2) * scale_y
            x2 = (x_center + w / 2) * scale_x
            y2 = (y_center + h / 2) * scale_y

            detections.append(
                Detection(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                    confidence=confidence,
                    class_id=class_id,
                    class_name="robot",  # Single class for now
                )
            )

        return detections

    def predict(self, image: NDArray[np.uint8]) -> list[Detection]:
        """
        Run inference on a single image.

        Args:
            image: Input image as (H, W, C) uint8 array

        Returns:
            List of Detection objects
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        assert self._session is not None

        # Get original size for scaling
        orig_h, orig_w = image.shape[:2]

        # Preprocess
        tensor = self.preprocess(image)

        # Run inference
        outputs = self._session.run(self._output_names, {self._input_name: tensor})

        # Scale factors for coordinate adjustment
        scale_x = orig_w / self.input_size
        scale_y = orig_h / self.input_size

        # Postprocess
        return self.postprocess(outputs, scale_x, scale_y)

    def predict_tiles(
        self,
        tiling_result: TilingResult,
    ) -> list[Detection]:
        """
        Run inference on all tiles and merge results.

        Args:
            tiling_result: Result from tile_image()

        Returns:
            Merged detections in global coordinates
        """
        all_detections: list[Detection] = []

        for tile in tiling_result.tiles:
            # Run inference on tile
            tile_detections = self.predict(tile.data)

            # Convert to global coordinates
            for det in tile_detections:
                global_bbox = tile_bbox_to_global(tile, det.bbox)
                all_detections.append(
                    Detection(
                        x1=global_bbox[0],
                        y1=global_bbox[1],
                        x2=global_bbox[2],
                        y2=global_bbox[3],
                        confidence=det.confidence,
                        class_id=det.class_id,
                        class_name=det.class_name,
                    )
                )

        return all_detections


# Global model instance (lazy loaded)
_model: ModelWrapper | None = None


def get_model(model_path: Path | None = None) -> ModelWrapper:
    """Get or create the global model instance."""
    global _model

    if _model is None:
        from .config import get_settings

        settings = get_settings()
        path = model_path or settings.get_model_path()

        _model = ModelWrapper(
            model_path=path,
            confidence_threshold=settings.confidence_threshold,
            input_size=settings.tile_size,
        )

    return _model


def load_model(model_path: Path | None = None) -> ModelWrapper:
    """Load the model and return the wrapper."""
    model = get_model(model_path)
    if not model.is_loaded:
        model.load()
    return model
