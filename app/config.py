import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "local_ai.db"
MODEL_CACHE_DIR = BASE_DIR / "model_cache"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_CONFIG = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "ner_model": "dslim/bert-base-NER",
    "classifier_model": "typeform/distilbert-base-uncased-mnli",
    "max_length": 512,
    "device": "cpu",
}

OCR_CONFIG = {
    "tesseract_cmd": "tesseract",
    "lang": "eng",
}

CHUNK_CONFIG = {
    "chunk_size": 300,
    "chunk_overlap": 50,
}

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
