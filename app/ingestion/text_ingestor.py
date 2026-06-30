from pathlib import Path


def ingest_text(text: str, source: str = "manual") -> dict:
    return {
        "raw_text": text,
        "source": source,
        "content_type": "text",
        "char_count": len(text),
        "word_count": len(text.split()),
    }


def ingest_text_file(file_path: str | Path) -> dict:
    path = Path(file_path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    return ingest_text(text, source=str(path.name))
