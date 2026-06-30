import re
import unicodedata


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_ocr_artifacts(text: str) -> str:
    text = re.sub(r"[|¦]", "I", text)
    text = re.sub(r"[¬]", "", text)
    text = re.sub(r"[•◦▪▸▹►]", "-", text)
    text = re.sub(r"[–—]", "-", text)
    text = re.sub(r"[«»]", '"', text)
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    return text


def normalize_pipeline(text: str) -> str:
    text = normalize_text(text)
    text = clean_ocr_artifacts(text)
    return text
