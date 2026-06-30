import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.processing.normalizer import normalize_text, clean_ocr_artifacts
from app.processing.chunker import chunk_text
from app.ingestion.text_ingestor import ingest_text


def test_normalize_text():
    assert normalize_text("  Hello   World  ") == "Hello World"
    assert normalize_text("\n\n\nTest\n\n") == "Test"
    assert normalize_text("") == ""


def test_clean_ocr():
    text = "Hello|World•Test"
    result = clean_ocr_artifacts(text)
    assert "|" not in result
    assert "•" not in result


def test_chunker():
    text = "word " * 500
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert chunks[0]["word_count"] <= 100


def test_ingest_text():
    result = ingest_text("Hello World", "test")
    assert result["raw_text"] == "Hello World"
    assert result["word_count"] == 2
    assert result["char_count"] == 11


if __name__ == "__main__":
    test_normalize_text()
    test_clean_ocr()
    test_chunker()
    test_ingest_text()
    print("All tests passed!")
