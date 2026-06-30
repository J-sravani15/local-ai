import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ingest_image(file_path: str | Path) -> dict:
    path = Path(file_path)
    try:
        from PIL import Image
        img = Image.open(path)
        img_format = img.format
        img_mode = img.mode
        img_size = img.size
    except Exception as e:
        logger.warning(f"Could not open image metadata: {e}")
        img_format = path.suffix.lstrip(".").upper()
        img_mode = "unknown"
        img_size = (0, 0)

    text = _ocr_image(path)
    return {
        "raw_text": text,
        "source": str(path.name),
        "content_type": "image",
        "char_count": len(text),
        "word_count": len(text.split()),
        "image_format": img_format,
        "image_mode": img_mode,
        "image_size": img_size,
    }


def _ocr_image(file_path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang="eng")
        return text.strip()
    except ImportError:
        logger.warning("pytesseract not installed, trying PIL-based OCR...")
        return _ocr_fallback(file_path)
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""


def _ocr_fallback(file_path: Path) -> str:
    try:
        import subprocess
        import tempfile
        from PIL import Image
        img = Image.open(file_path)
        temp_dir = tempfile.mkdtemp()
        temp_png = Path(temp_dir) / "ocr_page.png"
        img.save(temp_png, format="PNG")
        result = subprocess.run(
            ["tesseract", str(temp_png), "stdout", "-l", "eng"],
            capture_output=True, text=True, timeout=30,
        )
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        if result.returncode == 0:
            return result.stdout.strip()
        logger.warning(f"Tesseract CLI failed: {result.stderr}")
        return ""
    except FileNotFoundError:
        logger.warning("Tesseract not installed on system")
        return ""
    except Exception as e:
        logger.error(f"OCR fallback failed: {e}")
        return ""
