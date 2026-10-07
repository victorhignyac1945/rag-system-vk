"""OCR wrapper: pytesseract для изображений и PDF-сканов."""
import logging
from pathlib import Path

from backend.config import OCR_ENABLED, TESSERACT_LANG

logger = logging.getLogger(__name__)


def ocr_image(image_path: str) -> str:
    """Распознать текст с изображения через Tesseract."""
    if not OCR_ENABLED:
        logger.warning("OCR disabled, skipping %s", image_path)
        return ""

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        logger.error("pytesseract or Pillow not installed")
        return ""

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=TESSERACT_LANG)
        return text.strip()
    except Exception as e:
        logger.error("OCR failed for %s: %s", image_path, e)
        return ""


def ocr_pdf(pdf_path: str) -> str:
    """Распознать текст из PDF через pdf2image + pytesseract."""
    if not OCR_ENABLED:
        logger.warning("OCR disabled, skipping PDF %s", pdf_path)
        return ""

    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        logger.error("pdf2image or pytesseract not installed")
        return ""

    try:
        pages = convert_from_path(pdf_path, dpi=200)
        texts: list[str] = []
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang=TESSERACT_LANG)
            texts.append(text.strip())
            logger.debug("OCR page %d: %d chars", i + 1, len(text))
        return "\n\n".join(t for t in texts if t)
    except Exception as e:
        logger.error("OCR PDF failed for %s: %s", pdf_path, e)
        return ""
