"""
PDF to image conversion utilities.

Supports converting PDF files to PNG images for detection processing.
"""

from io import BytesIO
from typing import List

try:
    import fitz  # PyMuPDF
except ImportError:
    try:
        import pymupdf as fitz  # Alternative import
    except ImportError:
        raise ImportError(
            "PyMuPDF not found. Install it with: pip install PyMuPDF"
        )

import numpy as np
from PIL import Image

from .logging_config import get_logger

logger = get_logger(__name__)


def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[np.ndarray]:
    """
    Convert PDF bytes to a list of image arrays.

    Args:
        pdf_bytes: Raw PDF file bytes
        dpi: Resolution for rendering (default 300 for high quality)

    Returns:
        List of numpy arrays (one per page) in RGB format

    Raises:
        ValueError: If PDF is invalid or cannot be processed
    """
    try:
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        if pdf_document.page_count == 0:
            raise ValueError("PDF has no pages")

        logger.info(f"processing_pdf_pages", page_count=pdf_document.page_count, dpi=dpi)

        images = []

        for page_num in range(pdf_document.page_count):
            # Get page
            page = pdf_document[page_num]

            # Render page to image at specified DPI
            # mat is the transformation matrix for scaling
            zoom = dpi / 72.0  # PDF default is 72 DPI
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert to PIL Image
            img_bytes = pix.tobytes("png")
            img = Image.open(BytesIO(img_bytes))

            # Convert to numpy array
            img_array = np.array(img)

            images.append(img_array)

            logger.debug(
                f"converted_pdf_page",
                page=page_num + 1,
                shape=img_array.shape,
            )

        pdf_document.close()

        logger.info(f"pdf_conversion_complete", total_pages=len(images))

        return images

    except Exception as e:
        logger.error(f"pdf_conversion_failed", error=str(e))
        raise ValueError(f"Failed to convert PDF: {e}")


def is_pdf(content_type: str | None, filename: str | None = None) -> bool:
    """
    Check if file is a PDF based on content type or filename.

    Args:
        content_type: MIME type from upload
        filename: Original filename

    Returns:
        True if file appears to be a PDF
    """
    if content_type and content_type == "application/pdf":
        return True

    if filename and filename.lower().endswith(".pdf"):
        return True

    return False


def validate_pdf_size(pdf_bytes: bytes, max_pages: int = 10) -> None:
    """
    Validate PDF doesn't exceed page limits.

    Args:
        pdf_bytes: Raw PDF bytes
        max_pages: Maximum allowed pages

    Raises:
        ValueError: If PDF has too many pages
    """
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = pdf_document.page_count
        pdf_document.close()

        if page_count > max_pages:
            raise ValueError(
                f"PDF has {page_count} pages, maximum allowed is {max_pages}"
            )

    except Exception as e:
        raise ValueError(f"Failed to validate PDF: {e}")
