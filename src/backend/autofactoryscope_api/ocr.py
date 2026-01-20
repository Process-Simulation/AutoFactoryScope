"""
OCR module for extracting text from factory layouts.

Uses PaddleOCR for robust text detection and recognition in technical drawings.
"""

import logging
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray
from PIL import Image

logger = logging.getLogger(__name__)


class OCRResult:
    """Represents OCR detection result."""

    def __init__(
        self,
        text: str,
        bbox: tuple[float, float, float, float],
        confidence: float,
    ):
        self.text = text
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence

    def __repr__(self) -> str:
        return f"OCRResult(text='{self.text}', conf={self.confidence:.2f})"


class OCREngine(Protocol):
    """Protocol for OCR engines."""

    def ocr(
        self,
        img: NDArray[np.uint8],
        cls: bool = True,
    ) -> list: ...


class TextExtractor:
    """
    Text extraction from factory layout images.

    Supports both vector-based PDF extraction and raster OCR fallback.
    """

    def __init__(
        self,
        use_angle_cls: bool = True,
        lang: str = "en",
    ):
        """
        Initialize text extractor.

        Args:
            use_angle_cls: Enable text angle classification
            lang: OCR language (default: English)
        """
        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self._engine: OCREngine | None = None

    def load(self) -> None:
        """Load OCR engine (lazy loading)."""
        if self._engine is not None:
            return

        try:
            from paddleocr import PaddleOCR

            logger.info("Loading PaddleOCR engine (lang=%s)", self.lang)

            self._engine = PaddleOCR(
                use_angle_cls=self.use_angle_cls,
                lang=self.lang,
                show_log=False,
                use_gpu=False,  # CPU-only for simplicity
            )

            logger.info("PaddleOCR engine loaded successfully")

        except ImportError as e:
            logger.error("PaddleOCR not available: %s", e)
            raise RuntimeError(
                "PaddleOCR is required for text extraction. "
                "Install with: pip install paddleocr"
            ) from e

    @property
    def is_loaded(self) -> bool:
        """Check if OCR engine is loaded."""
        return self._engine is not None

    def extract_text(
        self,
        image: NDArray[np.uint8],
        min_confidence: float = 0.5,
    ) -> list[OCRResult]:
        """
        Extract text from image using OCR.

        Args:
            image: Input image as (H, W, C) uint8 array
            min_confidence: Minimum confidence threshold

        Returns:
            List of OCRResult objects
        """
        if not self.is_loaded:
            self.load()

        assert self._engine is not None

        # Run OCR
        results = self._engine.ocr(image, cls=self.use_angle_cls)

        # Parse results
        ocr_results: list[OCRResult] = []

        if results is None or len(results) == 0:
            return ocr_results

        for line in results[0]:  # PaddleOCR returns [[line1, line2, ...]]
            if line is None:
                continue

            bbox_points = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_info = line[1]  # (text, confidence)

            text = text_info[0]
            confidence = float(text_info[1])

            if confidence < min_confidence:
                continue

            # Convert polygon bbox to xyxy format
            xs = [p[0] for p in bbox_points]
            ys = [p[1] for p in bbox_points]
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)

            ocr_results.append(
                OCRResult(
                    text=text,
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                )
            )

        logger.info("Extracted %d text regions", len(ocr_results))
        return ocr_results

    def extract_from_crop(
        self,
        image: NDArray[np.uint8],
        crop_bbox: tuple[int, int, int, int],
    ) -> list[OCRResult]:
        """
        Extract text from a specific region of the image.

        Useful for extracting legend or title block text.

        Args:
            image: Full image
            crop_bbox: (x1, y1, x2, y2) region to OCR

        Returns:
            List of OCRResult objects (coordinates in crop space)
        """
        x1, y1, x2, y2 = crop_bbox
        crop = image[y1:y2, x1:x2]

        return self.extract_text(crop)


# Global OCR engine instance
_text_extractor: TextExtractor | None = None


def get_text_extractor() -> TextExtractor:
    """Get or create the global text extractor instance."""
    global _text_extractor

    if _text_extractor is None:
        _text_extractor = TextExtractor()

    return _text_extractor


def load_text_extractor() -> TextExtractor:
    """Load the text extractor and return the instance."""
    extractor = get_text_extractor()
    if not extractor.is_loaded:
        extractor.load()
    return extractor
