import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ingest_pdf(file_path: str | Path) -> dict:
    path = Path(file_path)
    try:
        import fitz
        doc = fitz.open(str(path))
        pages = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            pages.append({
                "page_num": page_num + 1,
                "text": text,
                "char_count": len(text),
            })
        doc.close()
        full_text = "\n".join(p["text"] for p in pages)
        return {
            "raw_text": full_text,
            "source": str(path.name),
            "content_type": "pdf",
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "page_count": len(pages),
            "pages": pages,
        }
    except ImportError:
        logger.warning("PyMuPDF not installed, trying pdfminer...")
        return _ingest_pdf_fallback(path)
    except Exception as e:
        logger.error(f"PDF ingestion failed: {e}")
        return {
            "raw_text": "",
            "source": str(path.name),
            "content_type": "pdf",
            "char_count": 0,
            "word_count": 0,
            "page_count": 0,
            "pages": [],
            "error": str(e),
        }


def _ingest_pdf_fallback(file_path: Path) -> dict:
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(str(file_path))
        return {
            "raw_text": text,
            "source": str(file_path.name),
            "content_type": "pdf",
            "char_count": len(text),
            "word_count": len(text.split()),
            "page_count": 1,
            "pages": [{"page_num": 1, "text": text, "char_count": len(text)}],
        }
    except ImportError:
        return {
            "raw_text": "",
            "source": str(file_path.name),
            "content_type": "pdf",
            "error": "No PDF parser available. Install PyMuPDF or pdfminer.",
            "char_count": 0,
            "word_count": 0,
            "page_count": 0,
            "pages": [],
        }
